from sqlalchemy import *
from impschedules import app
from impschedules import db
from isfunctions import *
import isprocessing
import collections
import models
import properties
import flask
import re

@app.route("/api/publishers/data/<segment>/")
def publishers_implementation_data(segment):
    # Get each publisher, most recent ImpSchedule
    publishers = db.session.query(models.Publisher,
                                  models.ImpSchedule,
                                  models.ImpScheduleData.segment_value_actual
                        ).join(models.ImpSchedule,
                               models.ImpScheduleData
                        ).filter(models.ImpScheduleData.segment == flask.escape(segment)
                        ).filter(models.ImpScheduleData.segment_value_actual != ""
                        ).order_by(models.ImpScheduleData.segment_value_actual
                        ).all()
    p = map(lambda x: {"organisation_code": str(x[0].publisher_code_actual),
                       "organisation_name": str(x[0].publisher_actual),
                       "implementationschedule_id": str(x[1].id), 
                       "date": str(x[2])}, publishers)
    return jsonify({"dates": p})
    #{"metadata": {"segment": segment, "name": properties.properties[segment]["name"]}, 

@app.route("/api/organisations/")
@support_jsonp
def api_publishers():
    orgs = db.session.query(models.Publisher,
                            models.ImpSchedule, 
                            models.ImpScheduleData
            ).join(models.ImpSchedule
            ).join(models.ImpScheduleData
            ).order_by(models.Publisher.publisher_actual
            ).all()

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

    scores=isprocessing.score_all(org_data, publishers, elementgroups, orgs)

    d = []
    for org in orgs:
        publisher = orgs[org]["publisher"].id
        schedule = orgs[org]["impschedule"].id
        d.append({"publisher_name": orgs[schedule]["publisher"].publisher_actual, "publisher_code": orgs[schedule]["publisher"].publisher_code_actual, "implementation_date": orgs[schedule]["properties"]["publishing_timetable_date_initial"]["value"], "will_publish": scores[schedule]["score"]["will_publish"], "approach": scores[schedule]["score"]["approach"], "fields": scores[schedule]["score"]["elements"], "group": scores[schedule]["score"]["group"], "group_code": makeGroupCode(scores[schedule]["score"]["group"])})
    return jsonify({"data": d})

def makeGroupCode(group):
    return (re.sub(" ", "-", group)).lower()

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

@app.route("/api/publishers/<publisher_code>/")
@app.route("/api/organisations/<publisher_code>/")
@support_jsonp_publishercode
def publisher_implementation_data(publisher_code):
    # Small hack for now...
    if publisher_code.startswith('US'):
        publisher_code='US'
    elif publisher_code.startswith('JP'):
        publisher_code='JP'
    publisher = models.Publisher.query.filter_by(publisher_code_actual=publisher_code).first_or_404()
    impschedule = models.ImpSchedule.query.filter_by(publisher_id=publisher.id).first_or_404()
   
    data = db.session.query(models.Data.status_actual,
                            models.Data.date_actual,
                            models.Data.notes_actual,
                            models.Element.name,
                            models.Element.level,
                            models.Property.defining_attribute,
                            models.Property.defining_attribute_value
                        ).filter(models.ImpSchedule.id==impschedule.id
                        ).join(models.Property
                        ).join(models.Element
                        ).join(models.ImpSchedule
                        ).all()

    d = map(lambda x: {"element": str(x[3]),
                       "element_level": str(x[4]), 
                       "element_attribute": str(x[5]), 
                       "element_attribute_part": str(x[6]),
                       "status_actual": x[0], 
                       "date_actual": str(x[1]), 
                       "notes_actual": x[2]}, data)


    # TODO: tidy all this up, it's a bit of a mess

    orgs = db.session.query(models.Publisher,
                            models.ImpSchedule, 
                            models.ImpScheduleData
            ).join(models.ImpSchedule
            ).join(models.ImpScheduleData
            ).order_by(models.Publisher.publisher_actual
            ).filter(models.ImpSchedule.id==impschedule.id
            ).all()

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
                     models.Property.weight == None,
                     models.Data.impschedule_id==impschedule.id
            ).all()

    publishers = set(map(lambda x: x[0], org_data))
    
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

    scores=isprocessing.score_all(org_data, publishers, elementgroups, orgs)
    
    return jsonify({"publisher": publisher.as_dict(), "data": d, "scores": scores[impschedule.id]['score']})

@app.route("/api/elements/dates/groups/")
def element_dates_groups():
    compliance_data = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Property.id.label("propertyid"),
                            models.Element.id, 
                            models.Element.name, 
                            models.Element.level,
                            models.Data.date_actual,
                            func.count(models.Data.id)
        ).group_by(models.Property.id, 
                   models.Data.date_actual,
                   models.Element.id,
                   models.Data.date_actual
        ).filter(models.Data.score==True
        ).filter(models.Data.date_actual!=None
        ).join(models.Element).join(models.Data).all()

    compliance = publication_dates_groups(compliance_data, True)
    return jsonify(compliance)

@app.route("/api/elements/dates/")
def element_dates():
    compliance_data = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Property.id.label("propertyid"),
                            models.Element.id, 
                            models.Element.name, 
                            models.Element.level,
                            models.Data.date_actual,
                            func.count(models.Data.id)
        ).group_by(models.Data.status_actual, 
        ).group_by(models.Property, 
                   models.Element.id, 
                   models.Element.name, 
                   models.Element.level, 
                   models.Data.date_actual
        ).join(models.Element).join(models.Data).all()

    compliance = publication_timeline(compliance_data, True)
    return jsonify(compliance)
