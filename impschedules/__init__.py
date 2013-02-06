from flask import Flask, render_template, flash, request, Markup, session, redirect, url_for, escape, Response, current_app
import sys, os
from lxml import etree
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime
import re
import json
import urllib
import string
import random
import iatiimplementationxml.toxml as toxml
import collections

app = Flask(__name__)
app.config.from_pyfile('../config.py')
app.secret_key = app.config["SECRET_KEY"]
db = SQLAlchemy(app)

import models
import properties
import api
from isfunctions import *
from isprocessing import *

db.create_all()

@app.route('/setup')
def setup():
    db.create_all()
    # create properties
    attributes = {'notes': {}, 'status_category': {}, 'publication_date': {}, 'exclusions': {}}
    elementgroups = properties.elementgroups
    
    for elementgroup, values in elementgroups.items():
        eg = models.ElementGroup()
        eg.name = elementgroup
        eg.description = values["description"]
        db.session.add(eg)
    db.session.commit()

    elementgroups = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name
                    ).all()
    elementgroups = dict(map(lambda x: (x[1],x[0]), elementgroups))

    elements = properties.elements
    for level, values in elements.items():
        for element, elvalue in values.items():
            e = models.Element()
            e.name = element
            e.level = level
            e.elementgroup = elementgroups[elvalue["group"]]
            if (elvalue.has_key("description")):
                e.description = elvalue["description"]
            db.session.add(e)
            db.session.commit()
            element_id = e.id
            if (elvalue.has_key("defining_attribute")):
                # if there are multiple versions of this element, e.g. funding, extending participating-orgs
                for defining_attribute_value in elvalue["defining_attribute_values"]:
                    #for attribute in attributes:
                    p = models.Property()
                    p.level = level
                    p.parent_element = element_id
                    #p.attribute = attribute
                    p.defining_attribute = elvalue["defining_attribute"]
                    p.defining_attribute_value = defining_attribute_value
                    db.session.add(p)
            else:
                #for attribute in attributes:
                p = models.Property()
                p.level = level
                p.parent_element = element_id
                #p.attribute = attribute
                db.session.add(p)
    db.session.commit()
    return 'Setup. <a href="/parse">Parse</a> XML files?'

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/import", methods=['GET', 'POST'])
def import_schedule():
    if (request.method == 'POST'):
        if ("do_import" in request.form):
            out = ""
            out2 = ""
            pr = {}
            data = {}
            s = {} # schedule
            for field, values in request.form.items():

                a = field.split('#')

                #a[0] is level
                #a[1] is field name, perhaps including a type (separated by @)
                #a[2] is field part (e.g. status_original, status_actual, etc.)
                if field.startswith('data'):
                    p = a[1]
                    s[p] = values
                elif field.startswith('metadata'):
                    p = a[1] + "_" + a[2]
                    s[p] = values

                elif field.startswith('publishing'):
                    try:
                        pr[a[1]]
                    except KeyError:
                        pr[a[1]] = {}

                    try:
                        pr[a[1]][a[2]]
                    except KeyError:
                        pr[a[1]][a[2]] = {}

                    pr[a[1]][a[2]] = values

                elif (field.startswith('organisation') or (field.startswith('activity'))):
                    at = a[1].split('@')

                    try:
                        at[1]
                    except IndexError:
                        at.append('')

                    try:
                        data[a[0]]
                    except KeyError:
                        data[a[0]] = {}

                    try:
                        data[a[0]][at[0]]
                    except KeyError:
                        data[a[0]][at[0]] = {}

                    try:
                        data[a[0]][at[0]][at[1]]
                    except KeyError:
                        data[a[0]][at[0]][at[1]] = {}

                    data[a[0]][at[0]][at[1]][a[2]] = values

            # write schedule
            sched = models.ImpSchedule(**s)
            db.session.add(sched)
            db.session.commit()
            # then write properties
            for k, v in pr.items():
                d = {}
                d["publisher_id"] = sched.id
                d["segment"] = k
                for a, b in v.items():
                    d["segment_value_"+a] = b
                dd = models.ImpScheduleData(**d)
                db.session.add(dd)

            # then write data
            elements = db.session.query(
                    models.Element.level, 
                    models.Element.name, 
                    models.Element.id
                    ).all()
            elements = dict(map(lambda x: ((x[0],x[1]),(x[2])), elements))

            element_properties = db.session.query(
                    models.Property.parent_element, 
                    models.Property.defining_attribute_value,
                    models.Property.id
                    ).all()
            element_properties = dict(map(lambda x: ((x[0],x[1]),(x[2])), element_properties))

            for level, values in data.items():
                for element, attributes in values.items():
                    element_id = elements[(level, element)]
                    for defining_attribute_value, prs in attributes.items():
                        # level
                        # element name
                        # defining_attribute_value
                        # properties
                        if (defining_attribute_value == ''):
                            defining_attribute_value = None
                        n = {}
                        n["property_id"] = element_properties[(element_id, defining_attribute_value)]
                        n["impschedule_id"] = sched.id
                        n["date_recorded"] = datetime.datetime.now()
                        for k, v in prs.items():
                            n[k] = v
                            if ((k=='date_original') or (k=='date_actual')):
                                if (v==''):
                                    n[k] = None
                                else:
                                    n[k] = datetime.datetime.strptime(v, "%Y-%m-%d")
                        if (n['status_actual'] is None):
                            n['status_actual'] = 'np'
                        if (n['status_actual'] is None):
                            n['status_actual'] = None
                        ndb = models.Data(**n)
                        db.session.add(ndb)
            db.session.commit()
            flash('Successfully imported your schedule', 'success')
            return redirect(url_for('publisher', id=sched.id))
        else:
            if (request.form['password'] == app.config["SECRET_PASSWORD"]):
                url = request.form['url']
                structure = request.form['structure']
                local_file_name = app.config["TEMP_FILES_DIR"] + "/" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range (5))
                #try:
                try:
                    f = urllib.urlretrieve(url, local_file_name)
                except IOError:
                    raise Exception("Could not connect to server. Are you sure you spelled it correctly?")
                # Pass to implementation schedule converter
                xml = toxml.convert_schedule(local_file_name, structure)
                doc = etree.fromstring(xml)
                context = {}
                context['source_file'] = url
                schedules = doc.findall("metadata")
                # Parse, manual check, and then import
                """try:"""
                #parse_implementation_schedule(doc, context.copy(), url, True)

                flash ("Successfully parsed your implementation schedule.", "success")
                return render_template("import_schedule_steps.html", doc=doc, properties=properties, source_file=url)
                """except Exception, e:
                    msg = "There was an unknown error importing your schedule. The error was: " + str(e)
                    flash (msg, "error")
                    return redirect(url_for('import_schedule'))
                except Exception, e:
                    msg = "There was an unknown error importing your schedule. The error was: " + str(e)
                    flash (msg, "error")
                    return redirect(url_for('import_schedule'))"""
            else:
                flash("Wrong password", "error")
                return redirect(url_for('import_schedule'))
    else:
        return render_template("import.html")

@app.route("/elementgroups")
@app.route("/elementgroups/<id>", methods=['GET', 'POST'])
def elementgroup(id=None):
    if (request.method == 'POST'):
        # handle post
        if (request.form['password'] == app.config["SECRET_PASSWORD"]):
            elementgroup = models.ElementGroup.query.filter_by(id=id).first()
            elementgroup.description = request.form['description']
            db.session.add(elementgroup)
            db.session.commit()
            flash('Updated element group', "success")
            return render_template("elementgroup.html", elementgroup=elementgroup)
        else:
            flash('Wrong password', "error")
            elementgroup = db.session.query(
                        models.ElementGroup.id,
                        models.ElementGroup.name,
                        models.ElementGroup.description,
                        models.ElementGroup.weight
                        ).filter(
                        models.ElementGroup.id==id
                        ).first()
            return render_template("elementgroup.html", elementgroup=elementgroup)
    else:
        if (id is not None):
            elementgroup = db.session.query(
                        models.ElementGroup.id,
                        models.ElementGroup.name,
                        models.ElementGroup.description,
                        models.ElementGroup.weight
                        ).filter(
                        models.ElementGroup.id==id
                        ).first()
            return render_template("elementgroup.html", elementgroup=elementgroup)
        else:
            elementgroups = db.session.query(
                        models.ElementGroup.id,
                        models.ElementGroup.name,
                        models.ElementGroup.description,
                        models.ElementGroup.weight
                        ).all()
            return render_template("elementgroups.html", elementgroups=elementgroups)

@app.route("/elements")
@app.route("/elements/<id>")
@app.route("/elements/<id>/<type>")
def element(id=None, type=None):
    if (id is not None):
        if (type):
            element = db.session.query(models.Element, models.Property
                ).filter(models.Element.name==id, models.Property.defining_attribute_value==type
                ).join(models.Property).first()
            data = db.session.query(models.Data, models.ImpSchedule
                ).filter(models.Element.name==id, models.Property.defining_attribute_value==type
                ).join(models.Property
                ).join(models.Element
                ).join(models.ImpSchedule
                ).order_by(models.ImpSchedule.publisher_actual
                ).all()

            element = {'element': element[0],
                       'properties': element[1]}
        else:
            element = models.Element.query.filter_by(name=id).first()
            data = db.session.query(models.Data, models.ImpSchedule
                ).filter(models.Element.name==id
                ).join(models.Property
                ).join(models.Element
                ).join(models.ImpSchedule
                ).order_by(models.ImpSchedule.publisher_actual
                ).all()
            element = {'element': element}
        return render_template("element.html", element=element, data=data)
    else:
        elements = db.session.query(models.Property.parent_element, 
                                    models.Property.defining_attribute_value, 
                                    models.Element.id, 
                                    models.Element.name, 
                                    models.Element.level,
                                    models.Element.description,
                                    models.Property.id.label("propertyid")
                ).distinct(
                ).join(models.Element).all()

        compliance_data = db.session.query(models.Property.parent_element, 
                                    models.Property.defining_attribute_value, 
                                    models.Property.id.label("propertyid"),
                                    models.Element.id, 
                                    models.Element.name, 
                                    models.Element.level,
                                    models.Data.score,
                                    func.count(models.Data.id)
                ).group_by(models.Data.status_actual, models.Property
                ).join(models.Element).join(models.Data).all()

        compliance = nest_compliance_scores(compliance_data)
        totalnum = db.session.query(func.count(models.ImpSchedule.id).label("number")).first()
        return render_template("elements.html", elements=elements, compliance=compliance, totalnum=totalnum.number)

@app.route("/publishers")
@app.route("/publishers/<id>")
def publisher(id=None):
    if (id is not None):
        """ need to return:
            # publisher information
            # publisher data
            # elementgroups 
                # element-property
                    # element-property data
                    # data

            Query: publisher for ImpSchedule
                   publisher data
                   all data where impschedule = id
                            + property
                            + element
                            + parent element
        """


        publisher = models.ImpSchedule.query.filter_by(id=id).first_or_404()
        publisher_data = db.session.query(models.ImpScheduleData
                ).filter(models.ImpSchedule.id==id
                ).join(models.ImpSchedule
                ).all()


        elementdata = db.session.query(models.Data,
                                       models.Property.id,
                                       models.Property.parent_element,
                                       models.Property.defining_attribute_value,
                                       models.Element.id,#4
                                       models.Element.name,
                                       models.Element.description,
                                       models.ElementGroup.id, #7
                                       models.ElementGroup.name,
                                       models.ElementGroup.description,
                                       models.Element.level
                                      ).filter(models.Data.impschedule_id == id
                                      ).join(models.Property
                                      ).join(models.Element
                                      ).join(models.ElementGroup
                                      ).all()
    
        
        data = {}
        elementdata = map(lambda x: {x[7] : {
                                               'name': x[8],
                                               'description': x[9],
                                               'elements': {
                                                  x[4]: {
                                                      'name': x[5],
                                                      'description': x[6],
                                                      'level': x[10],
                                                      'properties': {
                                                        x[1]: {
                                                            'parent_element': x[2],
                                                            'defining_attribute_value': x[3],
                                                            'data': x[0]
                                                        }
                                                  }
                                                }
                                    }}}, elementdata)

        for d in elementdata:
            merge_dict(data, d)
      
        try:
            s = score2(publisher_data, data)
        except IndexError:
            s = {}
            s['value'] = 0
            s['calculations'] = "Not able to calculate score"
        if publisher.under_consideration:
            s['group'] = "Under consideration"
            s['group_code'] = "alert-info"
        return render_template("publisher.html", publisher=publisher, data=data, segments=publisher_data, properties=properties, score=s, score_calculations=Markup(s["calculations"]))
    else:
        orgs = db.session.query(models.ImpSchedule, 
                                models.ImpScheduleData
                ).join(models.ImpScheduleData
                ).order_by(models.ImpSchedule.publisher_actual).all()

        # get impschedule id, # results for this score, the score, the elementgroup id
        org_data = db.session.query(models.Data.impschedule_id,
                                    func.count(models.Data.id),
                                    models.Data.score,
                                    models.ElementGroup.id
                ).join(models.Property
                ).join(models.Element
                ).join(models.ElementGroup
                ).group_by(models.Data.impschedule_id
                ).group_by(models.ElementGroup
                ).group_by(models.Data.score
                ).filter(models.Element.weight == None
                ).all()

        publishers = set(map(lambda x: x[0], org_data))
        elementgroups = set(map(lambda x: x[3], org_data))
        org_data = dict(map(lambda x: ((x[0],x[3],x[2]),(x[1])), org_data))
        org_pdata = map(lambda x: {x[0].id: {
                                    'impschedule': x[0],
                                    'properties': {
                                        x[1].segment: x[1].segment_value_actual
                                    }
                                }}, orgs)
        orgs = {}
        for o in org_pdata:
            merge_dict(orgs, o)

        scores=score_all(org_data, publishers, elementgroups, orgs)
        
        #scores = score_all(org_data)
        #print xx

        # need to get:
        # publisher data (not just publishing timetable date initial)
        # total scores per group where weight is not 0
        
        totalnum = db.session.query(func.count(models.ImpSchedule.id).label("number")).first()
        return render_template("publishers.html", orgs=orgs, totalnum=totalnum.number, scores=scores)

def merge_dict(d1, d2):
    # from here: http://stackoverflow.com/questions/10703858/python-merge-multi-level-dictionaries
    """
    Modifies d1 in-place to contain values from d2.  If any value
    in d1 is a dictionary (or dict-like), *and* the corresponding
    value in d2 is also a dictionary, then merge them in-place.
    """
    for k,v2 in d2.items():
        v1 = d1.get(k) # returns None if v1 has no value for this key
        if ( isinstance(v1, collections.Mapping) and 
             isinstance(v2, collections.Mapping) ):
            merge_dict(v1, v2)
        else:
            d1[k] = v2

@app.route("/publishers/<id>/edit", methods=['GET', 'POST'])
def publisher_edit(id=id):
    if (request.method == 'POST'):
        if (request.form['password'] == app.config["SECRET_PASSWORD"]):
            publisher = models.ImpSchedule.query.filter_by(id=id).first()
            publisher.publisher_actual = request.form['publisher']
            publisher.publisher_code_actual = request.form['publisher_code']
            publisher.schedule_version_actual = request.form['schedule_version']
            publisher.schedule_date_actual = request.form['schedule_date']
            db.session.add(publisher)
            db.session.commit()
            flash('Updated', "success")
            return render_template("publisher_editor.html", publisher=publisher)
        else:
            flash('Incorrect password', "error")
            publisher = models.ImpSchedule.query.filter_by(id=id).first()
            return render_template("publisher_editor.html", publisher=publisher)
    else:
        publisher = models.ImpSchedule.query.filter_by(id=id).first()
        return render_template("publisher_editor.html", publisher=publisher)

@app.route("/timeline")
def timeline(id=id):
    elements = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Element.id, 
                            models.Element.name, 
                            models.Element.level,
                            models.Property.id.label("propertyid")
        ).distinct(
        ).join(models.Element).all()
    return render_template("timeline.html", elements=elements)

@app.route("/flush")
def flush():
    db.session.remove()
    db.drop_all()
    return 'Deleted. <a href="/setup">Setup</a> again?'

@app.route("/parse")
def parse():
    #try:
        return load_package() + '<br />Parsed successfully. <a href="/">Go to front page</a>?'
    #except Exception, e:
    #    return "Failed"
