from flask import Flask, render_template, flash, request, Markup, session, redirect, url_for, escape, Response, current_app
import sys, os
from lxml import etree
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template
from sqlalchemy import func
import datetime
import re
import json
import urllib
import string
import random
import iatiimplementationxml.toxml as toxml

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
    return 'Setup. <a href="/parse">Parse</a> XML files?'

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/import", methods=['GET', 'POST'])
def import_schedule():
    if (request.method == 'POST'):
        if (request.form['password'] == app.config["SECRET_PASSWORD"]):
            url = request.form['url']
            structure = request.form['structure']
            local_file_name = app.config["TEMP_FILES_DIR"] + "/" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range (5))
            try:
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
                # Parse and import
                parse_implementation_schedule(doc, context.copy(), url)
                flash ("Successfully imported your schedule.", "success")
                return redirect(url_for('import_schedule'))
            except Exception, e:
                msg = "There was an unknown error importing your schedule. The error was: " + str(e)
                flash (msg, "error")
                return redirect(url_for('import_schedule'))
        else:
            flash("Wrong password", "error")
            return redirect(url_for('import_schedule'))
    else:
        return render_template("import.html")

@app.route("/elements")
@app.route("/elements/<id>")
@app.route("/elements/<id>/<type>")
def element(id=None, type=None):
    if (id is not None):
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
    else:
        elements = db.session.query(models.Property.parent_element, 
                                    models.Property.defining_attribute_value, 
                                    models.Element.id, 
                                    models.Element.name, 
                                    models.Element.level,
                                    models.Property.id.label("propertyid")
                ).distinct(
                ).join(models.Element).all()

        compliance_data = db.session.query(models.Property.parent_element, 
                                    models.Property.defining_attribute_value, 
                                    models.Property.id.label("propertyid"),
                                    models.Element.id, 
                                    models.Element.name, 
                                    models.Element.level,
                                    models.Data.status,
                                    func.count(models.Data.id)
                ).group_by(models.Data.status, models.Property
                ).join(models.Element).join(models.Data).all()

        compliance = nest_compliance_results(compliance_data)
        totalnum = db.session.query(func.count(models.ImpSchedule.id).label("number")).first()
        return render_template("elements.html", elements=elements, compliance=compliance, totalnum=totalnum.number)

@app.route("/publishers")
@app.route("/publishers/<id>")
def publisher(id=None):
    if (id is not None):
        publisher = models.ImpSchedule.query.filter_by(id=id).first()
        publisher_data = db.session.query(models.ImpScheduleData
                ).filter(models.ImpSchedule.id==id
                ).join(models.ImpSchedule
                ).all()
        
        data2 = []
        elements = db.session.query(models.Property.parent_element, models.Property.defining_attribute_value).order_by(models.Element.level, models.Property.parent_element, models.Property.defining_attribute_value).distinct()
        
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

        return render_template("publisher.html", publisher=publisher, data=data2, segments=publisher_data, properties=properties)
    else:
        orgs = db.session.query(models.ImpSchedule, models.ImpScheduleData.segment_value
                ).filter(models.ImpScheduleData.segment=="publishing_timetable_date_initial"
                ).join(models.ImpScheduleData
                ).order_by(models.ImpSchedule.publisher).all()

        totalnum = db.session.query(func.count(models.ImpSchedule.id).label("number")).first()
        return render_template("publishers.html", orgs=orgs, totalnum=totalnum.number)

@app.route("/publishers/<id>/edit", methods=['GET', 'POST'])
def publisher_edit(id=id):
    if (request.method == 'POST'):
        if (request.form['password'] == app.config["SECRET_PASSWORD"]):
            publisher = models.ImpSchedule.query.filter_by(id=id).first()
            publisher.publisher = request.form['publisher']
            publisher.publisher_code = request.form['publisher_code']
            publisher.schedule_version = request.form['schedule_version']
            publisher.schedule_date = request.form['schedule_date']
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
