from flask import Flask, render_template, flash, request, Markup, session, redirect, url_for, escape, Response, current_app, send_file
from werkzeug.security import generate_password_hash, check_password_hash
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
from functools import wraps

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

def login_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash('You must log in to access that page.', 'error')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)
    return decorated_function

def check_login():
    if ("username" in session):
        return session["admin"]
    else:
        return None

@app.route('/setup/')
def setup():
    db.create_all()
    # create user
    username = "admin"
    password = app.config["ADMIN_PASSWORD"]
    admin = 1
    u = models.User(username,password,admin)
    db.session.add(u)
    db.session.commit()

    # create publishers

    for publisher in properties.publishers:
        p = models.Publisher()
        p.publisher_actual = publisher["name"]
        p.publisher_original = publisher["name"]
        p.publisher_code_actual = publisher["code"]
        p.publisher_code_original = publisher["code"]
        db.session.add(p)
    db.session.commit()
    
    # create properties
    attributes = {'notes': {}, 'status_category': {}, 'publication_date': {}, 'exclusions': {}}
    elementgroups = properties.elementgroups
    
    for elementgroup, values in elementgroups.items():
        eg = models.ElementGroup()
        eg.name = elementgroup
        eg.description = values["description"]
        eg.order = values["order"]
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
                e.order = elvalue["order"]
            db.session.add(e)
            db.session.commit()
            element_id = e.id
            if (elvalue.has_key("defining_attribute")):
                # if there are multiple versions of this element, e.g. funding, extending participating-orgs
                for defining_attribute_value, property_values in elvalue["defining_attribute_values"].items():
                    #for attribute in attributes:
                    p = models.Property()
                    p.level = level
                    p.parent_element = element_id
                    #p.attribute = attribute
                    p.defining_attribute = elvalue["defining_attribute"]
                    p.defining_attribute_value = defining_attribute_value
                    p.defining_attribute_description = property_values['description']
                    p.order = property_values['order']
                    db.session.add(p)
            else:
                #for attribute in attributes:
                p = models.Property()
                p.level = level
                p.parent_element = element_id
                #p.attribute = attribute
                db.session.add(p)
    db.session.commit()
    return 'Setup. <a href="/import">Import</a> XML files?'

@app.route("/")
def index():
    return render_template("dashboard.html", auth=check_login())

@app.route("/about/")
def about():
    return render_template("about.html", auth=check_login())

@app.route("/organisations/<publisher_id>/<id>/edit/", methods=['GET', 'POST'])
@login_required
def edit_schedule(publisher_id=None, id=None):
    if (request.method == 'POST'):
        if ("do_import" in request.form):
            out = ""
            out2 = ""
            pr = {}
            data = {}
            s = {} # schedule

            s = models.ImpSchedule.query.filter_by(id=id).first()

            for field, values in request.form.items():

                a = field.split('#')

                #a[0] is level
                #a[1] is field name, perhaps including a type (separated by @)
                #a[2] is field part (e.g. status_original, status_actual, etc.)
                if field.startswith('data'):
                    p = a[1]
                    s.p = values
                elif field.startswith('metadata'):
                    p = a[1] + "_" + a[2]
                    s.p = values

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
                    if ((a[2] == "score") and (values == "0")):
                        values = None
                    data[a[0]][at[0]][at[1]][a[2]] = values

            # write schedule
            db.session.add(s)
            db.session.commit()
            # then write properties
            for k, v in pr.items():
                d = models.ImpScheduleData.query.filter_by(publisher_id=s.id, segment=k).first()
                for a, b in v.items():
                    setattr(d, "segment_value_" + a, b)
                db.session.add(d)
                db.session.commit()

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
                        if (defining_attribute_value == ''):
                            defining_attribute_value = None
                        n = models.Data.query.filter_by(property_id=element_properties[(element_id, defining_attribute_value)], impschedule_id=s.id).first()
                        # level
                        # element name
                        # defining_attribute_value
                        # properties

                        #n.date_recorded = datetime.datetime.now() # might want to add date_updated to DB
                        for k, v in prs.items():
                            if ((k=='date_original') or (k=='date_actual')):
                                if (v=='' or v=='None'):
                                    setattr(n, k, None)
                                else:
                                    setattr(n, k, datetime.datetime.strptime(v, "%Y-%m-%d"))
                            else:
                                setattr(n, k, v)
                        db.session.add(n)
                        db.session.commit()

            flash('Successfully updated your schedule', 'success')
            return redirect(url_for('organisation', id=publisher_id))
    else:
        publisher = models.Publisher.query.filter_by(publisher_code_actual=publisher_id).first()
        schedule = models.ImpSchedule.query.filter_by(id=id).first()
        schedule_data = db.session.query(models.ImpScheduleData
                ).filter(models.ImpSchedule.id==schedule.id
                ).join(models.ImpSchedule
                ).all()

        schedule_data_x = map(lambda x: { x.segment+"_actual": x.segment_value_actual,
                                          x.segment+"_original": x.segment_value_original }, schedule_data)
        schedule_data = {}
        for o in schedule_data_x:
            merge_dict(schedule_data, o)
        
        data = db.session.query(models.Data,
                                models.Property,
                                models.Element
                                ).join(models.Property
                                ).join(models.Element
                                ).filter(models.Data.impschedule_id==id).all()

        elementdata = map(lambda x: {
                                      x[2].id: {
                                          'element': x[2],
                                          'properties': {
                                            x[1].id: {
                                                'property': x[1],
                                                'data': x[0]
                                            }
                                      }
                                    }
                                    }, data)

        data = {}
        for d in elementdata:
            merge_dict(data, d)
        return render_template("edit_schedule.html", auth=check_login(), publisher=publisher, schedule=schedule, schedule_data=schedule_data, data=data, properties=properties)

@app.route("/import/", methods=['GET', 'POST'])
@login_required
def import_schedule():
    if (request.method == 'POST'):
        if ("form#createupdate" in request.form):
            out = ""
            out2 = ""
            pr = {}
            data = {}
            s = {} # schedule

            if (request.form['form#createupdate'] == 'existing'):
                # use existing publisher
                publisher_id = request.form['form#existing-publisher']
                publisher = models.Publisher.query.filter_by(id=publisher_id).first()
            else:
                # create new publisher
                publisher = models.Publisher()
                publisher.publisher_original = request.form['form#publisher#original']
                publisher.publisher_actual = request.form['form#publisher#actual']
                publisher.publisher_code_original = request.form['form#publisher_code#original']
                publisher.publisher_code_actual = request.form['form#publisher_code#actual']
                db.session.add(publisher)
                db.session.commit()
                publisher_id = publisher.id
            s['publisher_id'] = publisher_id
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
            return redirect(url_for('organisation', id=publisher.publisher_code_actual))
        else:
            publishers = models.Publisher.query.all()
            url = request.form['url']
            structure = request.form['structure']
            local_file_name = app.config["TEMP_FILES_DIR"] + "/" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range (5))
            try:
                try:
                    f = urllib.urlretrieve(url, local_file_name)
                except IOError:
                    raise Exception("Could not connect to server. Are you sure you spelled it correctly?")

                # Pass to implementation schedule converter
                try:
                    xml = toxml.convert_schedule(local_file_name, structure)
                except Exception, e:
                    msg = "Could not convert your schedule: " + str(e)
                    flash (msg, "error")
                    return render_template('import.html')
                doc = etree.fromstring(xml)
                context = {}
                context['source_file'] = url
                schedules = doc.findall("metadata")
                try:
                    flash ("Successfully parsed your implementation schedule.", "success")
                    return render_template("import_schedule_steps.html", doc=doc, properties=properties, source_file=url, publishers=publishers)
                except Exception, e:
                    msg = "There was an unknown error importing your schedule. The error was: " + str(e)
                    flash (msg, "error")
                    return render_template('import.html')
            except Exception, e:
                msg = "There was an unknown error importing your schedule. The error was: " + str(e)
                flash (msg, "error")
                return render_template('import.html', auth=check_login())
    else:
        return render_template("import.html", auth=check_login())

@app.route("/fieldgroups/")
@app.route("/fieldgroups/<id>/")
def elementgroup(id=None):
    if (id is not None):
        elementgroup = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name,
                    models.ElementGroup.description,
                    models.ElementGroup.weight
                    ).filter(
                    models.ElementGroup.id==id
                    ).first()
        return render_template("elementgroup.html", elementgroup=elementgroup, auth=check_login())
    else:
        elementgroups = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name,
                    models.ElementGroup.description,
                    models.ElementGroup.weight,
                    models.ElementGroup.order
                    ).order_by(models.ElementGroup.order
                    ).all()
        return render_template("elementgroups.html", elementgroups=elementgroups, auth=check_login())

@app.route("/fieldgroups/<id>/edit/", methods=['GET', 'POST'])
@login_required
def elementgroup_edit(id=None):
    if (request.method == 'POST'):
        # handle post
        elementgroup = models.ElementGroup.query.filter_by(id=id).first()
        elementgroup.description = request.form['description']
        db.session.add(elementgroup)
        db.session.commit()
        flash('Updated element group', "success")
        return render_template("elementgroup_edit.html", elementgroup=elementgroup, auth=check_login())
    else:
        elementgroup = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name,
                    models.ElementGroup.description,
                    models.ElementGroup.weight
                    ).filter(
                    models.ElementGroup.id==id
                    ).first()
        return render_template("elementgroup_edit.html", elementgroup=elementgroup, auth=check_login())

@app.route("/fields/<level>/<id>/edit/", methods=['GET', 'POST'])
@app.route("/fields/<level>/<id>/<type>/edit/", methods=['GET', 'POST'])
@login_required
def edit_element(level=None,id=None,type=None):
    if (level is not None and id is not None):
        if (request.method == 'POST'):
            # handle post
            element = models.Element.query.filter_by(name=id, level=level).first()
            element.description = request.form['element#description']
            element.longdescription = request.form['element#longdescription']
            if "element#weight" in request.form:
                ew = 0
            else:
                ew=None
            element.weight = ew
            db.session.add(element)
            elements = {'element': element}

            if (type):
                p = models.Property.query.filter_by(defining_attribute_value=type, parent_element=element.id).first()
                p.defining_attribute_description = request.form['property#defining_attribute_description']
                p.longdescription = request.form['property#longdescription']
                if "property#weight" in request.form:
                    prw = 0
                else:
                    prw=None
                p.weight = prw
                db.session.add(p)

                elements = {'element': element,
                            'properties': p}

            db.session.commit()
            flash('Updated element', "success")
            return render_template("element_editor.html", element=elements, auth=check_login())
        else:
            if (type):
                element = db.session.query(models.Element, models.Property
                    ).filter(models.Element.name==id, models.Property.defining_attribute_value==type, models.Element.level==level
                    ).join(models.Property).first()

                elements = {'element': element[0],
                           'properties': element[1]}
            else:
                element = db.session.query(models.Element, models.Property
                    ).filter(models.Element.name==id
                    ).join(models.Property).first()
                elements = {'element': element[0]}

            return render_template("element_editor.html", element=elements, auth=check_login())
    else:
        abort(404)

@app.route("/fields/")
@app.route("/fields/<level>/<id>/")
@app.route("/fields/<level>/<id>/<type>/")
def element(level=None, id=None, type=None):
    if ((level is not None) and (id is not None)):
        if (type):
            element = db.session.query(models.Element, 
                                       models.Property
                ).filter(models.Element.name==id, models.Property.defining_attribute_value==type, models.Element.level==level
                ).join(models.Property).first()
            data = db.session.query(models.Data, models.ImpSchedule, models.Publisher
                ).filter(models.Element.name==id, models.Property.defining_attribute_value==type, models.Element.level==level
                ).join(models.Property
                ).join(models.Element
                ).join(models.ImpSchedule
                ).join(models.Publisher
                ).order_by(models.Publisher.publisher_actual
                ).all()

            elements = {'element': element[0],
                       'properties': element[1]}
        else:
            element = db.session.query(models.Element, models.Property
                ).filter(models.Element.name==id, models.Element.level==level
                ).join(models.Property).first()
            data = db.session.query(models.Data, models.ImpSchedule, models.Publisher
                ).filter(models.Element.name==id, models.Element.level==level
                ).join(models.Property
                ).join(models.Element
                ).join(models.ImpSchedule
                ).join(models.Publisher
                ).order_by(models.Publisher.publisher_actual
                ).all()
            elements = {'element': element[0]}
            if (element[1].defining_attribute_value):
                prop = db.session.query(models.Property
                ).filter(models.Element.name==id, models.Element.level==level
                ).join(models.Element).all()
                elements = {'element': element[0],
                            'properties':prop}
                return render_template("element_with_properties.html", element=elements, auth=check_login())
        return render_template("element.html", element=elements, data=data, auth=check_login(), properties=properties)
    else:
        x = db.session.query(models.Property,
                             models.Element,
                             models.Data.score,
                             func.count(models.Data.id)
        ).group_by(models.Data.score
        ).group_by(models.Property.id
        ).join(models.Element
        ).join(models.Data
        #).join(models.ImpSchedule
        #).join(models.ImpScheduleData
        #).filter(models.ImpScheduleData.segment=='publishing_timetable_date_initial'
        #).filter(models.ImpScheduleData.segment_value_actual != ""
        ).all()

        b = map(lambda x: {x[0].id: {"property": x[0], "element": x[1], "scores": {x[2]: x[3]}}}, x)
        data = {}
        for d in b:
            merge_dict(data, d)

        values = {True, None}
        for x in data:
            data[x]["scores"]
            for v in values:
                try:
                    data[x]["scores"][v]
                except KeyError:
                    data[x]["scores"][v] = 0
            data[x]["scores"]["percentage"] = int(round(((float(data[x]["scores"][True])/(float(data[x]["scores"][True]+data[x]["scores"][None])))*100),0))

        return render_template("elements.html", data=data, auth=check_login())



def makeName(evalues, pvalues):
    if pvalues["defining_attribute_value"]:
        return evalues["description"] + " (" + pvalues["defining_attribute_description"] + ")"
    else:
        return evalues["description"]

def makeNiceEncoding(value):
    return value.encode("UTF-8", "ignore")

@app.route("/organisations/")
@app.route("/organisations.<fileformat>")
@app.route("/organisations/<id>/")
@app.route("/organisations/<id>.<fileformat>")
def organisation(id=None, fileformat=None):
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

        publisher = models.Publisher.query.filter_by(publisher_code_actual=id).first_or_404()
        schedule = models.ImpSchedule.query.filter_by(publisher_id=publisher.id).first_or_404()
        schedule_data = db.session.query(models.ImpScheduleData
                ).filter(models.ImpSchedule.id==schedule.id
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
                                       models.Element.level,
                                       models.Element.weight,
                                       models.ElementGroup.weight,
                                       models.Property.weight,
                                       models.ElementGroup.weight,
                                       models.Element.weight,
                                       models.Property.weight,
                                       models.ElementGroup.order,
                                       models.Element.order,
                                       models.Property.order,
                                       models.Property.defining_attribute_description,
                                      ).filter(models.Data.impschedule_id == schedule.id
                                      ).order_by(models.ElementGroup.order, models.Element.order, models.Property.order
                                      ).join(models.Property
                                      ).join(models.Element
                                      ).join(models.ElementGroup
                                      ).all()
        
        data = collections.OrderedDict()
        elementdata = map(lambda x: {x[7] : {
                                               'name': x[8],
                                               'description': x[9],
                                               'weight': x[12],
                                               'order': x[17],
                                               'elements': {
                                                  x[4]: {
                                                      'name': x[5],
                                                      'description': x[6],
                                                      'level': x[10],
                                                      'weight': x[11],
                                                      'order': x[18],
                                                      'properties': {
                                                        x[1]: {
                                                            'parent_element': x[2],
                                                            'defining_attribute_value': x[3],
                                                            'defining_attribute_description': x[20],
                                                            'data': x[0],
                                                            'weight': x[13],
                                                            'order': x[19]
                                                        }
                                                  }
                                                }
                                    }}}, elementdata)

        for d in elementdata:
            merge_dict(data, d)
    
        change_reasons = models.AlterationCategory.query.all()
        change_reasons = dict(map(lambda x: (x.name, (x.description, x.longdescription)), change_reasons))
        
        try:
            s = score2(schedule_data, data)
        except IndexError:
            s = {}
            s['value'] = 0
            s['calculations'] = "Not able to calculate score"
        if schedule.under_consideration:
            s['group'] = "Under consideration"
            s['group_code'] = "alert-info"

        if ((fileformat is not None) and (fileformat=='csv')):
            import StringIO
            import csv
            
            strIO = StringIO.StringIO()
            out = csv.DictWriter(strIO, fieldnames="level name compliance_status publication_date notes score".split())
            out.writerow({"level": "level", "name": "name", "compliance_status": "compliance_status", "publication_date": "publication_date", "notes": "notes", "score": "score"})
            for d, dvalues in data.items():
                for e, evalues in dvalues["elements"].items():
                    for p,pvalues in evalues["properties"].items():
                        out.writerow({"level": evalues["level"], "name": makeName(evalues, pvalues), "compliance_status": pvalues["data"].status_actual, "publication_date": pvalues["data"].date_actual, "notes": makeNiceEncoding(pvalues["data"].notes_actual), "score": pvalues["data"].score})
            strIO.seek(0)
            return send_file(strIO,
                             attachment_filename="organisations.csv",
                             as_attachment=True)

        else:

            return render_template("publisher.html", publisher=publisher, schedule=schedule, data=data, segments=schedule_data, properties=properties, score=s, score_calculations=Markup(s["calculations"]), auth=check_login(), change_reasons=change_reasons)
    else:
        # get all publishers
        allpublishers = models.Publisher.query.all()
        allpublishers = dict(map(lambda x: (x.id, (x.publisher_actual, x.publisher_code_actual)), allpublishers))

        orgs = db.session.query(models.Publisher,
                                models.ImpSchedule, 
                                models.ImpScheduleData
                ).join(models.ImpSchedule
                ).join(models.ImpScheduleData
                ).order_by(models.Publisher.publisher_actual
                ).all()

        publishingpublishers = set(map(lambda x: x[0], orgs))
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
                ).filter(models.Element.weight == None,models.Property.weight == None
                ).all()

        publishers = set(map(lambda x: x[0], org_data))
        for publisher in publishingpublishers:
            allpublishers.pop(publisher.id)
        
        elementgroups = set(map(lambda x: x[3], org_data))
        org_data = dict(map(lambda x: ((x[0],x[3],x[2]),(x[1])), org_data))
        org_pdata = map(lambda x: {x[1].id: {
                                    'publisher': x[0],
                                    'impschedule': x[1],
                                    'properties': {
                                        x[2].segment: {
                                            "value": x[2].segment_value_actual
                                        }
                                    }
                                }}, orgs)
        orgs = collections.OrderedDict()
        for o in org_pdata:
            merge_dict(orgs, o)

        scores=score_all(org_data, publishers, elementgroups, orgs)


        if ((fileformat is not None) and (fileformat=='csv')):
            import StringIO
            import csv
            
            strIO = StringIO.StringIO()
            out = csv.DictWriter(strIO, fieldnames="publisher_name publisher_code implementation_date will_publish approach fields group".split())
            out.writerow({"publisher_name": "publisher_name", "publisher_code": "publisher_code", "implementation_date": "implementation_date", "will_publish": "will_publish", "approach": "approach", "fields": "fields", "group": "group"})
            for org,values in orgs.items(): 
                out.writerow({"publisher_name": values["publisher"].publisher_actual, "publisher_code": values["publisher"].publisher_code_actual, "implementation_date": values["properties"]["publishing_timetable_date_initial"]["value"], "will_publish": scores[values["publisher"].id]["score"]["will_publish"], "approach": scores[values["publisher"].id]["score"]["approach"], "fields": scores[values["publisher"].id]["score"]["elements"], "group": scores[values["publisher"].id]["score"]["group"]})
            strIO.seek(0)
            return send_file(strIO,
                             attachment_filename="organisations.csv",
                             as_attachment=True)
        else:
            return render_template("publishers.html", orgs=orgs, scores=scores, auth=check_login(), notpublishing=allpublishers)

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

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if (request.method=='POST'):
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        getuser = models.User.query.filter_by(username=username).first()
        if ((getuser) and (getuser.check_password(password))):
            session['username'] = escape(request.form['username'])
            session['user_id'] = getuser.id
            if (getuser.admin == 1):
                session['admin'] = getuser.admin
            flash('Welcome back.', 'success')
            return redirect(url_for('index'))
        else:
            flash("Could not find that user. Please try again.", 'error')
            return redirect(url_for('index'))
    else:
        return render_template("login.html")

@app.route('/logout/')
def logout():
    # remove the login from the session if its there
    session.pop('username', None)
    session.pop('admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route("/organisations/<id>/edit/", methods=['GET', 'POST'])
@login_required
def organisation_edit(id=id):
    if (request.method == 'POST'):
        publisher = models.Publisher.query.filter_by(publisher_code_actual=id).first()
        impschedule = models.ImpSchedule.query.filter_by(publisher_id=publisher.id).first()
        publisher.publisher_actual = request.form['publisher']
        publisher.publisher_code_actual = request.form['publisher_code']
        db.session.add(publisher)
        try:
            impschedule.analysis = request.form['impschedule_analysis']
            db.session.add(impschedule)
        # If there's no schedule, then pass
        except AttributeError:
            id = None
        flash('Updated', "success")
        db.session.commit()
        return redirect(url_for('organisation', id=id))
    else:
        publisher = models.Publisher.query.filter_by(publisher_code_actual=id).first()
        impschedule = models.ImpSchedule.query.filter_by(publisher_id=publisher.id).first()
        return render_template("publisher_editor.html", publisher=publisher, impschedule=impschedule, auth=check_login())

@app.route("/timeline/")
def timeline(id=id):
    elements = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Element.id, 
                            models.Element.description, 
                            models.Element.level,
                            models.Element.name,
                            models.Property.id.label("propertyid")
        ).distinct(
        ).join(models.Element).all()
    return render_template("timeline.html", elements=elements, auth=check_login())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', auth=check_login()), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', error=e, auth=check_login()), 500
