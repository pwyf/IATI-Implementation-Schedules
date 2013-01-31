from sqlalchemy import *
from impschedules import app
from impschedules import db

class ImpSchedule(db.Model):
    __tablename__ = 'impschedule'
    id = Column(Integer, primary_key=True)
    publisher_original = Column(UnicodeText)
    publisher_code_original = Column(UnicodeText)
    publisher_actual = Column(UnicodeText)
    publisher_code_actual = Column(UnicodeText)
    schedule_version_original = Column(UnicodeText)
    schedule_date_original = Column(UnicodeText)
    last_updated_date_original = Column(UnicodeText)
    schedule_version_actual = Column(UnicodeText)
    schedule_date_actual = Column(UnicodeText)
    last_updated_date = Column(UnicodeText)
    source_file = Column(UnicodeText)
    schedule_type_original = Column(UnicodeText)
    schedule_type_actual = Column(UnicodeText)
    schedule_type_code_original = Column(UnicodeText)
    schedule_type_code_actual = Column(UnicodeText)

    def __init__(self, publisher_original=None, publisher_code_original=None, schedule_version_original=None, schedule_date_original=None, publisher_actual=None, publisher_code_actual=None, schedule_version_actual=None, schedule_date_actual=None, last_updated_date=None, source_file=None, schedule_type_original=None, schedule_type_actual=None, schedule_type_code_original=None, schedule_type_code_actual=None):
        self.publisher_original = publisher_original
        self.publisher_code_original = publisher_code_original
        self.schedule_version_original = schedule_version_original
        self.schedule_date_original = schedule_date_original
        self.publisher_actual = publisher_actual
        self.publisher_code_actual = publisher_code_actual
        self.schedule_version_actual = schedule_version_actual
        self.schedule_date_actual = schedule_date_actual
        self.last_updated_date = last_updated_date
        self.source_file = source_file
        self.schedule_type_original = schedule_type_original
        self.schedule_type_actual = schedule_type_actual
        self.schedule_type_code_original = schedule_type_code_original
        self.schedule_type_code_actual = schedule_type_code_actual

    def __repr__(self):
        return self.publisher, self.id

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ImpScheduleData(db.Model):
    __tablename__ = 'impscheduledata'
    id = Column(Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('impschedule.id'))
    segment = Column(UnicodeText)
    segment_value_actual = Column(UnicodeText)
    segment_value_original = Column(UnicodeText)
    segment_value_change = Column(UnicodeText)

    def __init__(self, publisher_id=None, segment=None, segment_value_original=None, segment_value_actual=None, segment_value_change=None):
        self.publisher_id = publisher_id
        self.segment = segment
        self.segment_value_original = segment_value_original
        self.segment_value_actual = segment_value_actual
        self.segment_value_change = segment_value_change

    def __repr__(self):
        return self.id, self.publisher_id, self.segment, self.segment_value_actual

class AlterationCategory(db.Model):
    __tablename__ = 'alterationcategory'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    description = Column(UnicodeText)

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

class Data(db.Model):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('property.id'))
    impschedule_id = Column(Integer, ForeignKey('impschedule.id'))
    date_recorded = Column(DateTime)
    status_original = Column(UnicodeText)
    date_original = Column(Date)
    notes_original = Column(UnicodeText)
    status_actual = Column(UnicodeText)
    date_actual = Column(Date)
    notes_actual = Column(UnicodeText)
    status_change = Column(UnicodeText)
    date_change = Column(UnicodeText)
    notes_change = Column(UnicodeText)
    exclusions = Column(UnicodeText)

    def __init__(self, property_id=None, impschedule_id=None, date_recorded=None, status_original=None, date_original=None, notes_original=None, status_actual=None, date_actual=None, notes_actual=None, status_change=None, date_change=None, notes_change=None):
        self.property_id = property_id
        self.impschedule_id = impschedule_id
        self.date_recorded = date_recorded
        self.status_original = status_original
        self.date_original = date_original
        self.notes_original = notes_original
        self.status_actual = status_actual
        self.date_actual = date_actual
        self.notes_actual = notes_actual
        self.status_change = status_change
        self.date_change = date_change
        self.notes_change = notes_change

    
    def __repr__(self):
        return self.property_id, self.impschedule_id, self.status_actual, self.date_actual, self.notes_actual, self.status_original, self.date_original, self.notes_original
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
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

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

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

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
