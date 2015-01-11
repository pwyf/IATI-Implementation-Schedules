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
        out[publisher]["score"]["total"] = round(
            (out[publisher]["score"]["total"]*100), 2
        )

        # Get scoring headlines (total score etc)

        out[publisher]["score"].update(get_scoring_headlines(
            org_data[publisher]["properties"]["publishing_timetable_date_initial"]["value"],
            org_data[publisher]["properties"]["publishing_license"]["value"],
            org_data[publisher]["properties"]["publishing_frequency_frequency"]["value"],
            out[publisher]["score"]["total"],
            )
        )

        under_consideration = org_data[publisher]["impschedule"]

        # Get the scoring group (ambitious, etc)

        out[publisher]["score"].update(get_scoring_group(
            out[publisher]["score"]["will_publish"],
            out[publisher]["score"]["elements"],
            out[publisher]["score"]["approach"]
            )
        )

    return out
    
def score_publisher():
    return
    
def get_scoring_headlines(initial_pub, license_val, frequency_val, elements):

    # Will publish
    if initial_pub != "":
        will_publish = 100.0
    else:
        will_publish = 0.0

    # License
    if (license_val != "" and license_val != "o"):
        license = 1.0
        license_comment = "open license"
    else:
        license = 0.0
        license_comment = "not an open license"

    # Frequency
    if (frequency_val in ['m', 'q']):
        frequency = 1.0
        frequency_comment = "at least quarterly"
    else:
        frequency = 0.0
        frequency_comment = "less than quarterly"

    # Approach
    approach = ((license + frequency)/2)*100

    # Total
    total = elements * will_publish/100 * ((license + frequency)/2)

    # Rounding
    total = round(total, 0)
    elements = round(elements, 0)


    return {"will_publish": will_publish,
            "approach": approach,
            "license": license,
            "license_comment": license_comment,
            "frequency": frequency,
            "frequency_comment": frequency_comment,
            "elements": elements,
            "total": total}

def get_scoring_group(will_publish, elements, approach):
    score = {}
    if (will_publish >= 100):
        if ((elements >=60)  and (approach>=100)):
            score["group"] = "Ambitious"
            score["group_code"] = "label-success"
            score["group_order"] = "1"
        elif ((elements >=40) and (approach>=50)):
            score["group"] = "Moderately ambitious"
            score["group_code"] = "label-warning"
            score["group_order"] = "2"
        elif (elements >=1):
            score["group"] = "Unambitious"
            score["group_code"] = "label-important"
            score["group_order"] = "3"
        elif ((elements == 0) and (will_publish >=100)):
            score["group"] = "Incomplete"
            score["group_code"] = "label-important"
            score["group_order"] = "5"
    elif (will_publish ==0):
        score["group"] = "No publication"
        score["group_code"] = "label-inverse"
        score["group_order"] = "6"
            
    return score

def score2(publisher_data, element_data):
    s = {}
    s['calculations'] = ""
    s['value'] = 0.0
    s['groups'] = {}

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
        s['groups'][elementgroup]['yes'] = int(ok_group)
        s['groups'][elementgroup]['no'] = int(nook_group)
        s['groups'][elementgroup]['total'] = round((ok_group/(ok_group+nook_group))*100, 2)
        ok = (ok + ((ok_group/(ok_group+nook_group))/num_groups))

    s['elements'] = round(ok*100, 2)
    
    properties = dict(map(lambda x: ((x.segment),(x.segment_value_actual)), publisher_data))
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
    
    scoring_group = get_scoring_group(
                s["will_publish"],
                s["elements"],
                s["approach"])
                
    s["group"] = scoring_group["group"]
    s["group_code"] = scoring_group["group_code"]
    s["group_order"] = scoring_group["group_order"]

    s["total"] = s["total"]

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
