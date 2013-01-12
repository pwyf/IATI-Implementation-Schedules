from sqlalchemy import *
from impschedules import app
from impschedules import db
from isfunctions import *
import models

@app.route("/api/publishers/<publisher_code>")
def publisher_implementation_data(publisher_code):
    publisher = models.ImpSchedule.query.filter_by(publisher_code=publisher_code).first()
   
    data = db.session.query(models.Data.status,
                            models.Data.publication_date,
                            models.Data.notes,
                            models.Element.name,
                            models.Element.level,
                            models.Property.defining_attribute,
                            models.Property.defining_attribute_value
                        ).filter(models.ImpSchedule.publisher_code==publisher_code
                        ).join(models.Property
                        ).join(models.Element
                        ).join(models.ImpSchedule
                        ).all()

    d = map(lambda x: {"element": str(x[3]),
                       "element_level": str(x[4]), 
                       "element_attribute": str(x[5]), 
                       "element_attribute_part": str(x[6]),
                       "status": x[0], 
                       "publication_date": str(x[1]), 
                       "notes": str(x[2])}, data)
    
    return jsonify({"publisher": publisher.as_dict(), "data": d})

@app.route("/api/elements/dates/groups")
def element_dates_groups():
    compliance_data = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Property.id.label("propertyid"),
                            models.Element.id, 
                            models.Element.name, 
                            models.Element.level,
                            models.Data.publication_date,
                            func.count(models.Data.id)
        ).group_by(models.Property.id, models.Data.publication_date
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
                            models.Data.publication_date,
                            func.count(models.Data.id)
        ).group_by(models.Data.status, models.Property
        ).join(models.Element).join(models.Data).all()

    compliance = publication_timeline(compliance_data, True)
    return jsonify(compliance)
