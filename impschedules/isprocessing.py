from sqlalchemy import *
from impschedules import app
from impschedules import db
from isfunctions import *
import models
import os
from lxml import etree
import datetime
import properties

def parse_implementation_schedule(schedule, out, package_filename):
 
    out["last_updated_date"] = datetime.datetime.now()
    out["publisher"] = schedule.find("metadata").find("publisher").text
    out["publisher_code"] = schedule.find("metadata").find("publisher").get("code")
    out["schedule_version"] = schedule.find("metadata").find("version").text
    out["schedule_date"] = schedule.find("metadata").find("date").text

    sched = models.ImpSchedule(**out) 
    db.session.add(sched)
    db.session.commit()

    pd = {}
    
    #properties come from module properties.py
    for k, v in properties.properties.items():
        try:
            pd[k] = (eval(v["data"]))
        except AttributeError:
            pass

    for k, v in pd.items():
        d = models.ImpScheduleData()
        d.publisher_id = sched.id
        d.segment = k
        d.segment_value = v
        db.session.add(d)

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
            try:
                data.exclusions = schedule.find(element.level).find(element_name).find("exclusions").find("narrative").text
            except AttributeError:
                pass
            if (data.exclusions is None):
                data.exclusions = ""
            try:
                data.notes = schedule.find(element.level).find(element_name).find("notes").text
            except AttributeError:
                data.notes=""
            try:
                data.publication_date = datetime.datetime.strptime(schedule.find(element.level).find(element_name).find("publication-date").text, "%Y-%m-%d")
            except AttributeError:
                pass
            
            data.date_recorded = datetime.datetime.now()
            db.session.add(data)
    
    db.session.commit()
    return "Done "

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
        #    pass
    return out
