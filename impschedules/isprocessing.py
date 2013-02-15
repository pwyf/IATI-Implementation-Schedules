from sqlalchemy import *
from impschedules import app
from impschedules import db
from isfunctions import *
import models
import os
from lxml import etree
import datetime
import properties

def score_all(data, publishers, elements, org_data):
    out = {}
    for publisher in publishers:
        out[publisher] = {}
        numelements = float(len(elements))
        out[publisher]["score"] = {}
        out[publisher]["score"]["total"] = 0.0
        for element in elements:
            out[publisher][element] = {}
            try:
                yes = float(data[(publisher,element,True)])
            except KeyError:
                yes = 0.0
            try:
                no = float(data[(publisher,element,None)])
            except KeyError:
                no = 0.0
            try:
                total = (yes/(yes+no))
            except ZeroDivisionError:
                total = 0.0
            out[publisher][element]["total"] = total
            out[publisher][element]["num"] = yes+no
            out[publisher][element]["yes"] = yes
            out[publisher][element]["no"] = no
            out[publisher]["score"]["total"] += total/numelements
        out[publisher]["score"]["total"] = round((out[publisher]["score"]["total"]*100), 0)

        if (org_data[publisher]["properties"]["publishing_timetable_date_initial"]["value"] != ""):
            will_publish = 1.0
        else:
            will_publish = 0.0
        
        if (org_data[publisher]["properties"]["publishing_license"]["value"] != ""):
            license = 1.0
        else:
            license = 0.0
        
        if ((org_data[publisher]["properties"]["publishing_frequency_frequency"]["value"] == "m") or (org_data[publisher]["properties"]["publishing_frequency_frequency"]["value"] == "q")):
            frequency = 1.0
        else:
            frequency = 0.0

        out[publisher]["score"]["elements"] = out[publisher]["score"]["total"]
        out[publisher]["score"]["total"] = out[publisher]["score"]["total"] * will_publish * ((license + frequency)/2)
        out[publisher]["score"]["will_publish"] = will_publish*100
        out[publisher]["score"]["approach"] = ((license + frequency)/2)*100
        out[publisher]["score"]["approach"] = ((license + frequency)/2)*100

        if (org_data[publisher]["impschedule"].under_consideration):
            out[publisher]["score"]["group"] = "Under consideration"
            out[publisher]["score"]["group_code"] = ""
        if (out[publisher]["score"]["will_publish"] >= 100):
            if ((out[publisher]["score"]["elements"] >=60)  and (out[publisher]["score"]["approach"]>=100)):
                out[publisher]["score"]["group"] = "Ambitious"
                out[publisher]["score"]["group_code"] = "label-success"
            elif ((out[publisher]["score"]["elements"] >=40) and (out[publisher]["score"]["approach"]>=50)):
                out[publisher]["score"]["group"] = "Moderately ambitious"
                out[publisher]["score"]["group_code"] = "label-warning"
            elif (out[publisher]["score"]["elements"] >=1):
                out[publisher]["score"]["group"] = "Unambitious"
                out[publisher]["score"]["group_code"] = "label-important"
            elif ((out[publisher]["score"]["elements"] == 0) and (out[publisher]["score"]["will_publish"] >=100)):
                out[publisher]["score"]["group"] = "Incomplete"
                out[publisher]["score"]["group_code"] = "label-inverse"
        elif (out[publisher]["score"]["will_publish"] ==0):
            out[publisher]["score"]["group"] = "No publication"
            out[publisher]["score"]["group_code"] = "label-inverse"

    return out

def score2(publisher_data, element_data):
    s = {}
    s['calculations'] = ""
    s['value'] = 0.0
    s['groups'] = {}
    properties = dict(map(lambda x: ((x.segment),(x.segment_value_actual)), publisher_data))

    num_groups = len(element_data)
    ok = 0.0
    nook = 0.0
    for elementgroup, elementgroupvalues in element_data.items():
        ok_group = 0.0
        nook_group = 0.0
        for element, elementvalues in elementgroupvalues["elements"].items():
            if elementvalues['weight'] == None:
                for prop, propvalues in elementvalues["properties"].items():
                    if propvalues['weight'] == None:
                        score = propvalues["data"].score
                        if (score == 1):
                            ok_group = ok_group+1.0
                        else:
                            nook_group = nook_group + 1.0
        s['groups'][elementgroup] = {}
        s['groups'][elementgroup]['yes'] = ok_group
        s['groups'][elementgroup]['no'] = nook_group
        s['groups'][elementgroup]['total'] = (ok_group/(ok_group+nook_group))*100
        ok = (ok + ((ok_group/(ok_group+nook_group))/num_groups))

    s['elements'] = ok*100
    
    if (properties['publishing_timetable_date_initial'] != ''):
        willpublish = 1.0
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
   
    s['total'] = round((willpublish*(ok)*((frequent+license)/2))*100)
    s['will_publish'] = willpublish*100
    s['approach'] = (((frequent+license)/2)*100)
    s['license'] = license
    s['frequency'] = frequent

    if (s["will_publish"] == 100):
        if ((s["elements"] >=60)  and (s["approach"]>=100)):
            s["group"] = "Ambitious"
            s["group_code"] = "label-success"
        elif ((s["elements"] >=40) and (s["approach"]>=50)):
            s["group"] = "Moderately ambitious"
            s["group_code"] = "label-warning"
        elif (s["elements"] >=1):
            s["group"] = "Unambitious"
            s["group_code"] = "label-important"
        elif ((s["elements"] == 0) and (s["will_publish"] >=100)):
            s["group"] = "Incomplete"
            s["group_code"] = "label-inverse"
    elif (s["will_publish"] ==0):
        s["group"] = "No publication"
        s["group_code"] = "label-inverse"


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
