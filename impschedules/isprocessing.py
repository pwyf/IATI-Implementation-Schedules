from sqlalchemy import *
from impschedules import app
from impschedules import db
from isfunctions import *
import models
import os
from lxml import etree
import datetime
import properties

def score(publisher_data, element_data):
    properties = dict(map(lambda x: ((x.segment),(x.segment_value_actual)), publisher_data))
    data = map(lambda x: ((x["data"][0].status_actual),(str(x["data"][0].date_actual), str(x["data"][0].property_id))), element_data)
    ok = 0.0
    nook = 0.0
    s = {}
    s['calculations'] = ""
    s['value'] = 0.0
    for d, values in data:
        if (d=='fc'):
            ok=ok+1.0
        elif ((d=='fp') and (values[0]!='')):
            ok=ok+1.0
        else:
            nook = nook+1.0
    
    if (properties['publishing_timetable_date_initial'] != ''):
        willpublish = 1.0
        s['calculations'] += "Planning to publish to IATI<br />"
    else:
        willpublish = 0.0
    if ((properties['publishing_frequency_frequency'] == 'm') or (properties['publishing_frequency_frequency'] == 'q')):
        frequent = 1.0
    else:
        frequent = 0.0
    try:
        if ((properties['publishing_license'] == 'p') or (properties['publishing_license'] == 'a')):
            license = 1.0
        else:
            license = 0.0
    except KeyError:
        license = 0.0

    if ((license==1.0) and (frequent==1.0)):
        s['calculations'] += "Planning to publish at least quarterly under an open license (100% score)<br />"
    elif (license==1.0):
        s['calculations'] += "Planning to publish under an open license, but not planning to publish at least quarterly (50% score)<br />"
    elif (frequent==1.0):
        s['calculations'] += "Planning to publish at least quarterly, but planning to publish under an open license (50% score)<br />"
    
    s['calculations'] += "Elements publishing: " + str(int(ok)) + "<br />"
    s['calculations'] += "Elements not publishing: " + str(int(nook)) + "<br />"
    s['calculations'] += "Elements score: " + str(int(round(((ok/(ok+nook))*100),0))) + "%<br />"

    s['calculations'] += "<br />"
    s['calculations'] += str(int(willpublish*100)) + "% (plan to publish) x " + str(int(((frequent+license)/2)*100)) + "% (publishing approach) x " + str((round(((ok/(ok+nook))*100),0))) + "% (elements score)"
   
    s['value'] = round((willpublish*(ok/(ok+nook))*((frequent+license)/2))*100)
    return s

def parse_implementation_schedule(schedule, out, package_filename):
 
    out["last_updated_date"] = datetime.datetime.now()
    out["publisher_actual"] = schedule.find("metadata").find("publisher").text
    out["publisher_code_actual"] = schedule.find("metadata").find("publisher").get("code")
    out["schedule_version_actual"] = schedule.find("metadata").find("version").text
    out["schedule_date_actual"] = schedule.find("metadata").find("date").text

    out["publisher_original"] = schedule.find("metadata").find("publisher").text
    out["publisher_code_original"] = schedule.find("metadata").find("publisher").get("code")
    out["schedule_version_original"] = schedule.find("metadata").find("version").text
    out["schedule_date_original"] = schedule.find("metadata").find("date").text

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
        d.segment_value_actual = v
        d.segment_value_original = v
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
            try:
                data.status_actual = schedule.find(element.level).find(element_name).find("status").get("category")
            except AttributeError:
                pass
            try:
                data.exclusions = schedule.find(element.level).find(element_name).find("exclusions").find("narrative").text
            except AttributeError:
                pass
            if (data.exclusions is None):
                data.exclusions = ""
            try:
                data.notes_actual = schedule.find(element.level).find(element_name).find("notes").text
            except AttributeError:
                data.notes_actual=""
            try:
                data.date_actual = datetime.datetime.strptime(schedule.find(element.level).find(element_name).find("publication-date").text, "%Y-%m-%d")
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
