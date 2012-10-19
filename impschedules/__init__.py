from flask import Flask, render_template, flash, request, Markup, session, redirect, url_for, escape, Response
from flask.ext.celery import Celery
#from celery.task.sets import TaskSet # Is this going to be used?
import sys, os
from lxml import etree
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template
from sqlalchemy import func
from lxml import etree
from datetime import date, datetime
import re

app = Flask(__name__)
app.config.from_pyfile('../config.py')
celery = Celery(app)
db = SQLAlchemy(app)

import models

db.create_all()

@app.route('/setup')
def setup():
    # create properties
    attributes = {'notes': {}, 'status_category': {}, 'publication_date': {}, 'exclusions': {}}
    elements = {
        'organisation': {'total-budget': {}, 'recipient-org-budget': {}, 'recipient-country-budget': {},'document-link': {}},
        'activity': {
            'reporting-org': {}, 
            'iati-identifier': {}, 
            'other-identifier': {},
            'title': { 
                'defining_attribute': 'type', 
                'defining_attribute_values': {
                    'agency': {},
                    'recipient': {}
                }
            }, 
            'description': { 
                'defining_attribute': 'type', 
                'defining_attribute_values': {
                    'agency': {},
                    'recipient': {}
                }
            },  
            'activity-status': {},
            'activity-date': { 
                'defining_attribute': 'type', 
                'defining_attribute_values': {
                    'start': {},
                    'end': {}
                }
            },
            'contact-info': {},
            'participating-org': {
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'funding': {},
                    'extending': {},
                    'accountable': {},
                    'implementing': {}
                }
            },
            'recipient-region': {},
            'recipient-country': {},
            'location': {},
            'sector': {
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'crs': {},
                    'agency': {}
                }
            },
            'policy-marker': {},
            'collaboration-type': {},
            'default-flow-type': {},
            'default-finance-type': {},
            'default-aid-type': {},
            'default-tied-status': {},
            'budget': {},
            'transaction': {
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'commitment': {},
                    'disbursement': {},
                    'reimbursement': {},
                    'incoming': {},
                    'repayment': {}
                }
            },
            'document-link': {},
            'activity-website': {},
            'related-activity': {},
            'conditions': {
                'defining_attribute': 'type',
                'defining_attribute_values': {
                    'attached': {},
                    'text': {}
                }
            },
            'result': {}
        }
    }
    for level, values in elements.items():
        for element, elvalue in values.items():
            e = models.Element()
            e.name = element
            e.level = level
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
    return "Done"

def parse_implementation_schedule(schedule, out, package_filename):
 
    out["last_updated_date"] = datetime.now()
    out["publisher"] = schedule.find("metadata").find("publisher").text
    out["publisher_code"] = schedule.find("metadata").find("publisher").get("code")
    out["schedule_version"] = schedule.find("metadata").find("version").text
    out["schedule_date"] = schedule.find("metadata").find("date").text

    sched = models.ImpSchedule(**out) 
    db.session.add(sched)
    db.session.commit()

    elements = models.Element.query.all()
    for element in elements:
        # element name is element.name
        for p in (models.Property.query.filter_by(parent_element=element.id).all()):
            data = models.Data()
            data.property_id = p.id
            data.impschedule_id = sched.id

            if (p.defining_attribute is not None):
                path = "/[@" + p.defining_attribute + '="' + p.defining_attribute_value + '"]'
                element_name = element.name + path
            else:
                element_name = element.name

            data.status = schedule.find(element.level).find(element_name).find("status").get("category")
            data.exclusions = schedule.find(element.level).find(element_name).find("exclusions").find("narrative").text
            if (data.exclusions is None):
                data.exclusions = ""
            try:
                data.notes = schedule.find(element.level).find(element_name).find("notes").text
            except AttributeError:
                data.notes=""
            try:
                data.publication_date = date.strptime(schedule.find(element.level).find(element_name).find("publication-date").text, "%y-%m-%d")
            except AttributeError:
                pass
            except TypeError:
                pass
            
            data.date_recorded = datetime.now()
            db.session.add(data)
    
    # check each element in organisation and activity
    """
    out["publishing"] = {}
    out["publishing_scope_value"] = schedule.find("publishing").find("scope").get("value")
    out["publishing_scope_narrative"] = schedule.find("publishing").find("scope").find("narrative").text
    out["publishing_timetable_date_initial"] = schedule.find("publishing").find("publication-timetable").get("date-initial")
    out["publishing_timetable_narrative"] = schedule.find("publishing").find("publication-timetable").find("narrative").text
    out["publishing_frequency_frequency"] = schedule.find("publishing").find("publication-frequency").get("frequency")
    out["publishing_frequency_timeliness"] = schedule.find("publishing").find("publication-frequency").get("timeliness")
    out["publishing_frequency_narrative"] = schedule.find("publishing").find("publication-frequency").find("narrative").text
    out["publishing_lifecycle_point"] = schedule.find("publishing").find("publication-lifecycle").get("point")
    out["publishing_lifecycle_narrative"] = schedule.find("publishing").find("publication-lifecycle").find("narrative").text
    out["publishing_data_quality_quality"] = schedule.find("publishing").find("data-quality").get("quality")
    out["publishing_data_quality_narrative"] = schedule.find("publishing").find("data-quality").find("narrative").text
    out["publishing_approach_resource"] = schedule.find("publishing").find("approach").get("resource")
    out["publishing_approach_narrative"] = schedule.find("publishing").find("approach").find("narrative").text
    out["publishing"]["notes"] = schedule.find("publishing").find("notes").find("narrative").text
    out["publishing_thresholds"] = schedule.find("publishing").find("thresholds").find("narrative").text
    out["publishing"]["exclusions"] = schedule.find("publishing").find("exclusions").find("narrative").text
    out["publishing_constraints"] = schedule.find("publishing").find("constraints-other").find("narrative").text
    out["publishing_license"] = schedule.find("publishing").find("license").get("license")
    out["publishing_license_narrative"] = schedule.find("publishing").find("license").find("narrative").text
    out["publishing_multilevel"] = schedule.find("publishing").find("activity-multilevel").get("yesno")
    out["publishing_multilevel_narrative"] = schedule.find("publishing").find("activity-multilevel").find("narrative").text
    out["publishing_segmentation"] = schedule.find("publishing").find("segmentation").get("segmentation")
    out["publishing_segmentation_narrative"] = schedule.find("publishing").find("segmentation").find("narrative").text
    out["publishing_user_interface_status"] = schedule.find("publishing").find("user-interface").get("status")
    out["publishing_user_interface_narrative"] = schedule.find("publishing").find("segmentation").find("narrative").text
    
    """
    db.session.commit()
    return "Done "

def toUs(element):
    # replace hyphen with underscore
    us = re.sub("-", "_", element)
    return us

def load_file(file_name, context=None):
    doc = etree.parse(file_name)
    if context is None:
        context = {}
    context['source_file'] = file_name

    schedules = doc.findall("metadata")

    return parse_implementation_schedule(doc, context.copy(), file_name)

    db.session.commit()


def load_package():
    path = app.config["XML_FILES_DIR"]
    listing = os.listdir(path)
    totalfiles = len(listing)
    out = ""
    out = "Found" + str(totalfiles) + "files."
    filecount = 1
    for infile in listing:
        #try: 
            out = out + "<br />"
            """
            out = out + "Loading file" + filecount + "of" + totalfiles + "(" + round(((float(filecount)/float(totalfiles))*100),2), "%)"
            """
            filecount = filecount +1
            out = out + load_file(path + '/' + infile)
        #except Exception, e:
        #    out = out + 'Failed:', e
	    #pass
    return out

def test_percentages(data):
    packages = set(map(lambda x: (x[5]), data))
    d = dict(map(lambda x: (x[5],x[6]), data))
    out = {}
    for p in packages:
        compliant = 0
        uncompliant = 0
        for s in d[(p)]:
            if (s == 'fc'):
                compliant = compliant +1
            else:
                uncompliant = uncompliant +1
        #except: success = 0
        try: 
            out[p] =  round((float(compliant)/(compliant+uncompliant)) * 100,2)
        except Exception, e:
            out[p]=compliant
        #out[p,q] = {}
        #out[p,q]['compliant'] = d[(p,q,0.status)]
    return out

@app.route("/")
def index():
    orgs = models.ImpSchedule.query.order_by(models.ImpSchedule.publisher).all()
    """elements = db.session.query(models.Property.parent_element, 
                                models.Property.defining_attribute_value,
                                models.Element.level,
                                models.Element.name,
                                models.Element.id,
                                models.Property.id.label("propertyid")
            ).order_by(models.Element.level.desc(), models.Element.name, models.Property.defining_attribute_value
            ).group_by(models.Element).all()
    """
    
    elements = db.session.query(models.Property.parent_element, 
                                models.Property.defining_attribute_value, 
                                models.Element.id, 
                                models.Element.name, 
                                models.Element.level,
                                models.Property.id.label("propertyid")
            ).distinct(
            ).join(models.Element).all()

    compliance = db.session.query(models.Property.id, func.count(models.Data.id).label("number")
            ).filter(models.Data.status=='fc'
            ).group_by(models.Property
            ).join(models.Data
            ).all() 
    
    totalnum = db.session.query(func.count(models.ImpSchedule.id).label("number")).first()

    return render_template("organisations.html", orgs=orgs, elements=elements, compliance=compliance, totalnum=totalnum.number)    

@app.route("/element/<id>")
@app.route("/element/<id>/<type>")
def element(id=id, type=None):
    if (type):
        element = db.session.query(models.Element, models.Property
            ).filter(models.Element.id==id, models.Property.defining_attribute_value==type
            ).join(models.Property).first()
        data = db.session.query(models.Data, models.ImpSchedule
            ).filter(models.Element.id==id, models.Property.defining_attribute_value==type
            ).join(models.Property
            ).join(models.Element
            ).join(models.ImpSchedule
            ).order_by(models.ImpSchedule.publisher
            ).all()
    else:
        element = models.Element.query.filter_by(id=id).first()
        data = db.session.query(models.Data, models.ImpSchedule
            ).filter(models.Element.id==id
            ).join(models.Property
            ).join(models.Element
            ).join(models.ImpSchedule
            ).order_by(models.ImpSchedule.publisher
            ).all()
    return render_template("element.html", element=element, data=data)

@app.route("/publisher/<id>")
def publisher(id=id):
    publisher = models.ImpSchedule.query.filter_by(id=id).first()
    
    data2 = []
    elements = db.session.query(models.Property.parent_element, models.Property.defining_attribute_value).distinct()
    
    for element in elements:
        d={}
        d["element"] = models.Element.query.filter_by(id=element.parent_element).first()
        d["property"] = models.Property.query.filter_by(parent_element=element.parent_element, defining_attribute_value=element.defining_attribute_value).first()
        d["data"] = db.session.query(models.Data
            ).filter(models.Element.id==element.parent_element, models.Property.defining_attribute_value==element.defining_attribute_value, models.Data.impschedule_id==publisher.id
            ).join(models.Property
            ).join(models.Element
            ).all()
        data2.append(d)

    return render_template("publisher.html", publisher=publisher, data=data2)

@app.route("/parse")
def parse():
    #try:
        return load_package()
    #except Exception, e:
    #    return "Failed"
