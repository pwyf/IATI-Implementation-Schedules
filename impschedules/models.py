from sqlalchemy import *
from impschedules import app
from impschedules import db

class ImpSchedule(db.Model):
    __tablename__ = 'impschedule'
    id = Column(Integer, primary_key=True)
    publisher = Column(UnicodeText)
    publisher_code = Column(UnicodeText)
    schedule_version = Column(UnicodeText)
    schedule_date = Column(UnicodeText)
    last_updated_date = Column(UnicodeText)
    source_file = Column(UnicodeText)

    def __init__(self, publisher=None, publisher_code=None, schedule_version=None, schedule_date=None, last_updated_date=None, source_file=None):
        self.publisher = publisher
        self.publisher_code = publisher_code
        self.schedule_version = schedule_version
        self.schedule_date = schedule_date
        self.last_updated_date = last_updated_date
        self.source_file = source_file

    def __repr__(self):
        return self.publisher, self.id

class Data(db.Model):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('property.id'))
    impschedule_id = Column(Integer, ForeignKey('impschedule.id'))
    data = Column(UnicodeText)
    date_recorded = Column(DateTime)
    status = Column(UnicodeText)
    exclusions = Column(UnicodeText)
    notes = Column(UnicodeText)
    publication_date = Column(DateTime)

    def __init__(self, property_id=None, impschedule_id=None, data=None, date_recorded=None, status=None, exclusions=None, notes=None, publication_date=None):
        self.property_id = property_id
        self.impschedule_id = impschedule_id
        self.data = data
        self.date_recorded = date_recorded
        self.status = status
        self.exclusions = exclusions
        self.notes = notes
        self.publication_date = publication_date

    def __repr__(self):
        return self.property_id, self.impschedule_id, self.status, self.publication_date, self.notes, self.exclusions
    
class Property(db.Model):
    __tablename__ = 'property'
    id = Column(Integer, primary_key=True)
    parent_element = Column(Integer, ForeignKey('element.id'))
    attribute = Column(UnicodeText)
    defining_attribute = Column(UnicodeText)
    defining_attribute_value = Column(UnicodeText)
    description = Column(UnicodeText)

    def __init__(self, parent_element=None, attribute=None, description=None, defining_attribute=None, defining_attribute_value=None):
        self.parent_element = parent_element
        self.attribute = attribute
        self.description = description
        self.defining_attribute = defining_attribute
        self.defining_attribute_value = defining_attribute_value

    def __repr__(self):
        return self.id, self.parent_element, self.defining_attribute_value, self.description

class Element(db.Model):
    __tablename__ = 'element'
    id = Column(Integer, primary_key=True)
    level = Column(UnicodeText)
    name = Column(UnicodeText)
    description = Column(UnicodeText)

    def __init__(self, level=None, name=None, description=None):
        self.level = level
        self.name = name
        self.description = description

    def __repr__(self):
        return self.id, self.level, self.name, self.description
