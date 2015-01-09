from flask import Flask, render_template, flash, request, session, redirect, url_for, current_app, Markup, send_file
from sqlalchemy import func

from functools import wraps
import collections

import StringIO
import csv, datetime
from icalendar import Calendar, Event

import models, usermanagement, publisher_redirects
from impschedules import app, db, properties
from isfunctions import merge_dict
from isprocessing import score2, score_all, score_publisher

@app.route("/organisations/<publisher_id>/<id>/delete/")
@usermanagement.login_required
def delete_schedule(publisher_id, id):
    try:
        # Delete data:
        data = models.Data.query.filter_by(impschedule_id=id).all()
        for d in data:
            db.session.delete(d)
        db.session.commit()

        isdata = models.ImpScheduleData.query.filter_by(publisher_id=id).all()
        for isd in isdata:
            db.session.delete(isd)
        db.session.commit()
        
        schedule = models.ImpSchedule.query.filter_by(id=id).first()
        db.session.delete(schedule)
        db.session.commit()
        flash('Successfully deleted schedule', 'success')
    except Exception:
        flash("Couldn't delete schedule", 'error')
    return redirect(url_for('show_impschedules'))

@app.route("/organisations/<publisher_id>/<id>/edit/", methods=['GET', 'POST'])
@usermanagement.login_required
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
        return render_template("edit_schedule.html", auth=usermanagement.check_login(), publisher=publisher, schedule=schedule, schedule_data=schedule_data, data=data, properties=properties)

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
        # Small hack for now...
        id = publisher_redirects.correct_publisher(id)

        publisher = models.Publisher.query.filter_by(publisher_code_actual=id).first_or_404()
        schedule = models.ImpSchedule.query.filter_by(publisher_id=publisher.id).first_or_404()
        schedule_data = db.session.query(models.ImpScheduleData
                ).filter(models.ImpSchedule.id==schedule.id
                ).join(models.ImpSchedule
                ).all()

        element_data = db.session.query(models.Data,
                                       models.Property,
                                       models.Element,
                                       models.ElementGroup,
                                      ).filter(models.Data.impschedule_id == schedule.id
                                      ).order_by(models.ElementGroup.order, models.Element.order, models.Property.order
                                      ).join(models.Property
                                      ).join(models.Element
                                      ).join(models.ElementGroup
                                      ).all()
        
        data = collections.OrderedDict()
        element_data = map(lambda ed: {ed.ElementGroup.id : {
                   'name': ed.ElementGroup.name,
                   'description': ed.ElementGroup.description,
                   'weight': ed.Element.weight,
                   'order': ed.ElementGroup.order,
                   'elements': {
                      ed.Element.id: {
                          'name': ed.Element.name,
                          'description': ed.Element.description,
                          'level': ed.Element.level,
                          'weight': ed.Element.weight,
                          'order': ed.Element.order,
                          'properties': {
                            ed.Property.id: {
                                'parent_element': ed.Property.parent_element,
                                'defining_attribute_value': ed.Property.defining_attribute_value,
                                'defining_attribute_description': ed.Property.defining_attribute_description,
                                'data': ed.Data,
                                'weight': ed.Property.weight,
                                'order': ed.Property.order
                            }
                      }
                    }
                }}}, element_data)

        for d in element_data:
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

        if fileformat is not None:
            if fileformat=='csv':
                fieldnames = ['level', 'name', 'compliance_status',
                              'publication_date', 'notes', 'score']
                strIO = StringIO.StringIO()
                out = csv.DictWriter(strIO, fieldnames=fieldnames)
                out.writerow(dict(map(lambda fn: (fn, fn), fieldnames)))
                
                for d, dvalues in data.items():
                    for e, evalues in dvalues["elements"].items():
                        for p,pvalues in evalues["properties"].items():
                            out.writerow({
                        "level": evalues["level"],
                        "name": makeName(evalues, pvalues),
                        "compliance_status": pvalues["data"].status_actual,
                        "publication_date": pvalues["data"].date_actual,
                        "notes": makeNiceEncoding(pvalues["data"].notes_actual),
                        "score": pvalues["data"].score,
                        })
                strIO.seek(0)
                return send_file(strIO,
                                 attachment_filename=id + ".csv",
                                 as_attachment=True)
            if fileformat=='ics':
                cal = Calendar()
                cal.add('prodid', '-//IATI-Common Standard Publication for ' + publisher.publisher_actual + '//')
                for d, dvalues in data.items():
                    for e, evalues in dvalues["elements"].items():
                        for p,pvalues in evalues["properties"].items():
                            try:
                                event = Event()
                                event.add('summary', publisher.publisher_actual + ' publishes ' + makeName(evalues, pvalues))
                                event.add('dtstart', datetime.datetime(pvalues["data"].date_actual.year, pvalues["data"].date_actual.month, pvalues["data"].date_actual.day))
                                event.add('dtend', datetime.datetime(pvalues["data"].date_actual.year, pvalues["data"].date_actual.month, pvalues["data"].date_actual.day)+datetime.timedelta(hours=24))
                                cal.add_component(event)
                            except AttributeError:
                                pass
                strIO = StringIO.StringIO()
                strIO.write(cal.to_ical())
                strIO.seek(0)
                return send_file(strIO,
                                 attachment_filename=id + ".ics",
                                 as_attachment=True)

        else:

            return render_template("publisher.html",
                publisher=publisher,
                schedule=schedule,
                data=data,
                segments=schedule_data,
                properties=properties,
                score=s,
                score_calculations=Markup(s["calculations"]),
                auth=usermanagement.check_login(),
                change_reasons=change_reasons)
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
                ).filter(models.Element.weight == None,
                         models.Property.weight == None
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
        
            strIO = StringIO.StringIO()
            fieldnames = ['publisher_name', 'publisher_code',
            'implementation_date', 'total', 'will_publish', 'approach',
            'fields', 'group']
            out = csv.DictWriter(strIO, fieldnames=fieldnames)
            out.writerow(dict(map(lambda fn: (fn, fn), fieldnames)))
            for org in orgs:
                
                publisher = orgs[org]["publisher"].id
                schedule = orgs[org]["impschedule"].id
                out.writerow({"publisher_name": orgs[schedule]["publisher"].publisher_actual,
                "publisher_code": orgs[schedule]["publisher"].publisher_code_actual,
                "implementation_date": orgs[schedule]["properties"]["publishing_timetable_date_initial"]["value"],
                "total": scores[schedule]["score"]["total"],
                "will_publish": scores[schedule]["score"]["will_publish"],
                "approach": scores[schedule]["score"]["approach"],
                "fields": scores[schedule]["score"]["elements"],
                "group": scores[schedule]["score"]["group"]})
            strIO.seek(0)
            return send_file(strIO,
                             attachment_filename="organisations.csv",
                             as_attachment=True)
        else:
            return render_template("publishers.html", orgs=orgs, scores=scores, auth=usermanagement.check_login(), notpublishing=allpublishers)

@app.route("/organisations/<id>/edit/", methods=['GET', 'POST'])
@usermanagement.login_required
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
        return render_template("publisher_editor.html", publisher=publisher, impschedule=impschedule, auth=usermanagement.check_login())