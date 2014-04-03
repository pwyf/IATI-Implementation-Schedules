from sqlalchemy import *
from impschedules import app
from impschedules import db
from werkzeug.security import generate_password_hash, check_password_hash

class ImpSchedUser(db.Model):
    __tablename__ = 'impscheduleuser'
    id = Column(Integer, primary_key=True)
    username = Column(UnicodeText)
    admin = Column(Integer)
    pw_hash = db.Column(String(255))

    def __init__(self, username, password, admin=None):
        self.username = username
        self.admin = admin
        self.pw_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return self.username, self.id, self.password

class Publisher(db.Model):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    publisher_original = Column(UnicodeText)
    publisher_code_original = Column(UnicodeText)
    publisher_actual = Column(UnicodeText)
    publisher_code_actual = Column(UnicodeText)
    publisher_change = Column(UnicodeText)

    def __init__(self, publisher_original=None, publisher_code_original=None, publisher_actual=None, publisher_code_actual=None, publisher_change=None):

        self.publisher_original = publisher_original
        self.publisher_code_original = publisher_code_original
        self.publisher_actual = publisher_actual
        self.publisher_code_actual = publisher_code_actual
        self.publisher_change = publisher_change

    def __repr__(self):
        return self.publisher_actual, self.id

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ImpSchedule(db.Model):
    __tablename__ = 'impschedule'
    id = Column(Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    schedule_version_original = Column(UnicodeText)
    schedule_date_original = Column(UnicodeText)
    last_updated_date_original = Column(UnicodeText)
    schedule_version_actual = Column(UnicodeText)
    schedule_date_actual = Column(UnicodeText)
    last_updated_date = Column(UnicodeText)
    source_file = Column(UnicodeText)
    under_consideration = Column(UnicodeText)
    schedule_type_original = Column(UnicodeText)
    schedule_type_actual = Column(UnicodeText)
    schedule_type_code_original = Column(UnicodeText)
    schedule_type_code_actual = Column(UnicodeText)
    schedule_version_change = Column(UnicodeText)
    schedule_date_change = Column(UnicodeText)
    schedule_type_change = Column(UnicodeText)
    schedule_type_code_change = Column(UnicodeText)
    analysis = Column(UnicodeText)

    def __init__(self, publisher_id=None, schedule_version_original=None, schedule_date_original=None, schedule_version_actual=None, schedule_date_actual=None, last_updated_date=None, source_file=None, schedule_type_original=None, schedule_type_actual=None, schedule_type_code_original=None, schedule_type_code_actual=None,schedule_version_change=None, schedule_date_change=None, schedule_type_change=None, schedule_type_code_change=None,under_consideration=None,analysis=None):
        self.publisher_id=publisher_id
        self.schedule_version_original = schedule_version_original
        self.schedule_date_original = schedule_date_original
        self.schedule_version_actual = schedule_version_actual
        self.schedule_date_actual = schedule_date_actual
        self.last_updated_date = last_updated_date
        self.source_file = source_file
        self.schedule_type_original = schedule_type_original
        self.schedule_type_actual = schedule_type_actual
        self.schedule_type_code_original = schedule_type_code_original
        self.schedule_type_code_actual = schedule_type_code_actual
        self.schedule_version_change = schedule_version_change
        self.schedule_date_change = schedule_date_change
        self.schedule_type_change = schedule_type_change
        self.schedule_type_code_change = schedule_type_code_change
        self.under_consideration = under_consideration
        self.analysis = analysis

    def __repr__(self):
        return self.id, self.publisher_id

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
    longdescription = Column(UnicodeText)

    def __init__(self, name=None, description=None, longdescription=None):
        self.name = name
        self.description = description
        self.longdescription = longdescription
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

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
    score = Column(Boolean)
    exclusions = Column(UnicodeText)

    def __init__(self, property_id=None, impschedule_id=None, date_recorded=None, status_original=None, date_original=None, notes_original=None, status_actual=None, date_actual=None, notes_actual=None, status_change=None, date_change=None, notes_change=None,score=None):
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
        self.score = score

    
    def __repr__(self):
        return self.property_id, self.impschedule_id, self.status_actual, self.date_actual, self.notes_actual, self.status_original, self.date_original, self.notes_original
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ElementGroup(db.Model):
    __tablename__ = 'elementgroup'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    description = Column(UnicodeText)
    longdescription = Column(UnicodeText)
    weight = Column(Integer)
    order = Column(Integer)

    def __init__(self, name=None, description=None, weight=None, longdescription=None, order=None):
        self.name = name
        self.description = description
        self.longdescription = longdescription
        self.weight = weight
        self.order = order

    def __repr__(self):
        return self.id, self.name, self.description

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Element(db.Model):
    __tablename__ = 'element'
    id = Column(Integer, primary_key=True)
    level = Column(UnicodeText)
    name = Column(UnicodeText)
    description = Column(UnicodeText)
    longdescription = Column(UnicodeText)
    elementgroup = Column(Integer, ForeignKey('elementgroup.id'))
    weight = Column(Integer)
    order = Column(Integer)

    def __init__(self, level=None, name=None, description=None, longdescription=None, elementgroup=None, weight=None, order=None):
        self.level = level
        self.name = name
        self.description = description
        self.longdescription = longdescription
        self.elementgroup = elementgroup
        self.weight = weight
        self.order = order

    def __repr__(self):
        return self.id, self.level, self.name, self.description

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    
class Property(db.Model):
    __tablename__ = 'property'
    id = Column(Integer, primary_key=True)
    parent_element = Column(Integer, ForeignKey('element.id'))
    attribute = Column(UnicodeText)
    defining_attribute = Column(UnicodeText)
    defining_attribute_value = Column(UnicodeText)
    defining_attribute_description = Column(UnicodeText)
    weight = Column(Integer)
    longdescription = Column(UnicodeText)
    order = Column(Integer)

    def __init__(self, parent_element=None, attribute=None, defining_attribute_description=None, defining_attribute=None, defining_attribute_value=None, longdescription=None, weight=None, order=None):
        self.parent_element = parent_element
        self.attribute = attribute
        self.defining_attribute_description = defining_attribute_description
        self.defining_attribute = defining_attribute
        self.defining_attribute_value = defining_attribute_value
        self.longdescription=longdescription
        self.weight=weight
        self.order=order

    def __repr__(self):
        return self.id, self.parent_element, self.defining_attribute_value, self.defining_attribute_description

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
