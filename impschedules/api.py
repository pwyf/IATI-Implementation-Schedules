from sqlalchemy import *
from impschedules import app
from impschedules import db
from isfunctions import *
import models
import properties
import flask

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

@app.route("/api/publishers/<publisher_code>")
def publisher_implementation_data(publisher_code):
    publisher = models.Publisher.query.filter_by(publisher_code_actual=publisher_code).first()
    impschedule = models.ImpSchedule.query.filter_by(publisher_id=publisher.id).first()
   
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
    
    return jsonify({"publisher": publisher.as_dict(), "data": d})

@app.route("/api/elements/dates/groups")
def element_dates_groups():
    compliance_data = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Property.id.label("propertyid"),
                            models.Element.id, 
                            models.Element.name, 
                            models.Element.level,
                            models.Data.date_actual,
                            func.count(models.Data.id)
        ).group_by(models.Property.id, models.Data.date_actual
        ).filter(models.Data.score==1
        ).filter(models.Data.date_actual!=None
        ).join(models.Element).join(models.Data).all()

    compliance = publication_dates_groups(compliance_data, True)
    return jsonify(compliance)

@app.route("/api/elements/dates")
def element_dates():
    compliance_data = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Property.id.label("propertyid"),
                            models.Element.id, 
                            models.Element.name, 
                            models.Element.level,
                            models.Data.date_actual,
                            func.count(models.Data.id)
        ).group_by(models.Data.status_actual, models.Property
        ).join(models.Element).join(models.Data).all()

    compliance = publication_timeline(compliance_data, True)
    return jsonify(compliance)
