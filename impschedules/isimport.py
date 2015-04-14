from flask import Flask, render_template, flash, request, Markup, session, redirect, url_for, escape, Response, current_app, send_file
from impschedules import app, db, models, usermanagement, properties
import random, string, urllib
from iatiimplementationxml import toxml
from lxml import etree
import datetime

@app.route("/import/", methods=['GET', 'POST'])
@usermanagement.login_required
def import_schedule():
    if (request.method == 'POST'):
        if ("form#createupdate" in request.form):
            out = ""
            out2 = ""
            pr = {}
            data = {}
            s = {} # schedule

            if (request.form['form#createupdate'] == 'existing'):
                # use existing publisher
                publisher_id = request.form['form#existing-publisher']
                publisher = models.Publisher.query.filter_by(id=publisher_id).first()
            else:
                # create new publisher
                publisher = models.Publisher()
                publisher.publisher_original = request.form['form#publisher#original']
                publisher.publisher_actual = request.form['form#publisher#actual']
                publisher.publisher_code_original = request.form['form#publisher_code#original']
                publisher.publisher_code_actual = request.form['form#publisher_code#actual']
                db.session.add(publisher)
                db.session.commit()
                publisher_id = publisher.id
            s['publisher_id'] = publisher_id
            for field, values in request.form.items():

                a = field.split('#')

                #a[0] is level
                #a[1] is field name, perhaps including a type (separated by @)
                #a[2] is field part (e.g. status_original, status_actual, etc.)
                if field.startswith('data'):
                    p = a[1]
                    s[p] = values
                elif field.startswith('metadata'):
                    p = a[1] + "_" + a[2]
                    s[p] = values

                elif field.startswith('publishing'):
                    try:
                        pr[a[1]]
                    except KeyError:
                        pr[a[1]] = {}

                    try:
                        pr[a[1]][a[2]]
                    except KeyError:
                        pr[a[1]][a[2]] = {}

                    pr[a[1]][a[2]] = values

                elif (field.startswith('organisation') or (field.startswith('activity'))):
                    at = a[1].split('@')

                    try:
                        at[1]
                    except IndexError:
                        at.append('')

                    try:
                        data[a[0]]
                    except KeyError:
                        data[a[0]] = {}

                    try:
                        data[a[0]][at[0]]
                    except KeyError:
                        data[a[0]][at[0]] = {}

                    try:
                        data[a[0]][at[0]][at[1]]
                    except KeyError:
                        data[a[0]][at[0]][at[1]] = {}

                    data[a[0]][at[0]][at[1]][a[2]] = values

            # write schedule
            sched = models.ImpSchedule(**s)
            db.session.add(sched)
            db.session.commit()
            # then write properties
            for k, v in pr.items():
                d = {}
                d["publisher_id"] = sched.id
                d["segment"] = k
                for a, b in v.items():
                    d["segment_value_"+a] = b
                dd = models.ImpScheduleData(**d)
                db.session.add(dd)

            # then write data
            elements = db.session.query(
                    models.Element.level, 
                    models.Element.name, 
                    models.Element.id
                    ).all()
            elements = dict(map(lambda x: ((x[0],x[1]),(x[2])), elements))

            element_properties = db.session.query(
                    models.Property.parent_element, 
                    models.Property.defining_attribute_value,
                    models.Property.id
                    ).all()
            element_properties = dict(map(lambda x: ((x[0],x[1]),(x[2])), element_properties))

            for level, values in data.items():
                for element, attributes in values.items():
                    element_id = elements[(level, element)]
                    for defining_attribute_value, prs in attributes.items():
                        # level
                        # element name
                        # defining_attribute_value
                        # properties
                        if (defining_attribute_value == ''):
                            defining_attribute_value = None
                        n = {}
                        n["property_id"] = element_properties[(element_id, defining_attribute_value)]
                        n["impschedule_id"] = sched.id
                        n["date_recorded"] = datetime.datetime.now()
                        for k, v in prs.items():
                            n[k] = v
                            if ((k=='date_original') or (k=='date_actual')):
                                if (v==''):
                                    n[k] = None
                                else:
                                    n[k] = datetime.datetime.strptime(v, "%Y-%m-%d")
                        if (n['status_actual'] is None):
                            n['status_actual'] = 'np'
                        if (n['status_actual'] is None):
                            n['status_actual'] = None
                        ndb = models.Data(**n)
                        db.session.add(ndb)
            db.session.commit()
            flash('Successfully imported your schedule', 'success')
            return redirect(url_for('organisation', id=publisher.publisher_code_actual))
        else:
            publishers = models.Publisher.query.all()
            url = request.form['url']
            structure = request.form['structure']
            local_file_name = app.config["TEMP_FILES_DIR"] + "/" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range (5))
            #try:
            #try:
            f = urllib.urlretrieve(url, local_file_name)
            #except IOError:
            #    raise Exception("Could not connect to server. Are you sure you spelled it correctly?")

            # Pass to implementation schedule converter
            try:
                xml = toxml.convert_schedule(local_file_name, structure)
            except Exception, e:
                msg = "Could not convert your schedule: " + str(e)
                flash (msg, "error")
                return render_template('import.html')
            doc = etree.fromstring(xml)
            context = {}
            context['source_file'] = url
            schedules = doc.findall("metadata")
            try:
                flash ("Successfully parsed your implementation schedule.", "success")
                return render_template("import_schedule_steps.html", doc=doc, properties=properties, source_file=url, publishers=publishers)
            except Exception, e:
                msg = "There was an unknown error importing your schedule. The error was: " + str(e)
                flash (msg, "error")
                return render_template('import.html')
            """except Exception, e:
                msg = "There was an unknown error importing your schedule. The error was: " + str(e)
                flash (msg, "error")
                return render_template('import.html', auth=usermanagement.check_login())"""
    else:
        return render_template("import.html", auth=usermanagement.check_login())