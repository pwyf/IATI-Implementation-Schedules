from flask import Flask, render_template, flash, request, session, redirect, url_for, current_app

from sqlalchemy import func
from functools import wraps
import models, usermanagement
from impschedules import app, db
from isfunctions import merge_dict

@app.route("/fieldgroups/")
@app.route("/fieldgroups/<id>/")
def elementgroup(id=None):
    if (id is not None):
        elementgroup = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name,
                    models.ElementGroup.description,
                    models.ElementGroup.weight
                    ).filter(
                    models.ElementGroup.id==id
                    ).first()
        return render_template("elementgroup.html", elementgroup=elementgroup, auth=usermanagement.check_login())
    else:
        elementgroups = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name,
                    models.ElementGroup.description,
                    models.ElementGroup.weight,
                    models.ElementGroup.order
                    ).order_by(models.ElementGroup.order
                    ).all()
        return render_template("elementgroups.html", elementgroups=elementgroups, auth=usermanagement.check_login())

@app.route("/fieldgroups/<id>/edit/", methods=['GET', 'POST'])
@usermanagement.login_required
def elementgroup_edit(id=None):
    if (request.method == 'POST'):
        # handle post
        elementgroup = models.ElementGroup.query.filter_by(id=id).first()
        elementgroup.description = request.form['description']
        db.session.add(elementgroup)
        db.session.commit()
        flash('Updated element group', "success")
        return render_template("elementgroup_edit.html", elementgroup=elementgroup, auth=usermanagement.check_login())
    else:
        elementgroup = db.session.query(
                    models.ElementGroup.id,
                    models.ElementGroup.name,
                    models.ElementGroup.description,
                    models.ElementGroup.weight
                    ).filter(
                    models.ElementGroup.id==id
                    ).first()
        return render_template("elementgroup_edit.html", elementgroup=elementgroup, auth=usermanagement.check_login())

@app.route("/fields/<level>/<id>/edit/", methods=['GET', 'POST'])
@app.route("/fields/<level>/<id>/<type>/edit/", methods=['GET', 'POST'])
@usermanagement.login_required
def edit_element(level=None,id=None,type=None):
    if (level is not None and id is not None):
        if (request.method == 'POST'):
            # handle post
            element = models.Element.query.filter_by(name=id, level=level).first()
            element.description = request.form['element#description']
            element.longdescription = request.form['element#longdescription']
            if "element#weight" in request.form:
                ew = 0
            else:
                ew=None
            element.weight = ew
            db.session.add(element)
            elements = {'element': element}

            if (type):
                p = models.Property.query.filter_by(defining_attribute_value=type, parent_element=element.id).first()
                p.defining_attribute_description = request.form['property#defining_attribute_description']
                p.longdescription = request.form['property#longdescription']
                if "property#weight" in request.form:
                    prw = 0
                else:
                    prw=None
                p.weight = prw
                db.session.add(p)

                elements = {'element': element,
                            'properties': p}

            db.session.commit()
            flash('Updated element', "success")
            return render_template("element_editor.html", element=elements, auth=usermanagement.check_login())
        else:
            if (type):
                element = db.session.query(models.Element, models.Property
                    ).filter(models.Element.name==id, models.Property.defining_attribute_value==type, models.Element.level==level
                    ).join(models.Property).first()

                elements = {'element': element[0],
                           'properties': element[1]}
            else:
                element = db.session.query(models.Element, models.Property
                    ).filter(models.Element.name==id
                    ).join(models.Property).first()
                elements = {'element': element[0]}

            return render_template("element_editor.html", element=elements, auth=usermanagement.check_login())
    else:
        abort(404)

@app.route("/fields/")
@app.route("/fields/<level>/<id>/")
@app.route("/fields/<level>/<id>/<type>/")
def element(level=None, id=None, type=None):
    if ((level is not None) and (id is not None)):
        if (type):
            element = db.session.query(models.Element, 
                                       models.Property
                ).filter(models.Element.name==id, models.Property.defining_attribute_value==type, models.Element.level==level
                ).join(models.Property).first()
            data = db.session.query(models.Data, models.ImpSchedule, models.Publisher
                ).filter(models.Element.name==id, models.Property.defining_attribute_value==type, models.Element.level==level
                ).join(models.Property
                ).join(models.Element
                ).join(models.ImpSchedule
                ).join(models.Publisher
                ).order_by(models.Publisher.publisher_actual
                ).all()

            elements = {'element': element[0],
                       'properties': element[1]}
        else:
            element = db.session.query(models.Element, models.Property
                ).filter(models.Element.name==id, models.Element.level==level
                ).join(models.Property).first()
            data = db.session.query(models.Data, models.ImpSchedule, models.Publisher
                ).filter(models.Element.name==id, models.Element.level==level
                ).join(models.Property
                ).join(models.Element
                ).join(models.ImpSchedule
                ).join(models.Publisher
                ).order_by(models.Publisher.publisher_actual
                ).all()
            elements = {'element': element[0]}
            if (element[1].defining_attribute_value):
                prop = db.session.query(models.Property
                ).filter(models.Element.name==id, models.Element.level==level
                ).join(models.Element).all()
                elements = {'element': element[0],
                            'properties':prop}
                return render_template("element_with_properties.html", element=elements, auth=usermanagement.check_login())
        return render_template("element.html", element=elements, data=data, auth=usermanagement.check_login(), properties=properties)
    else:
        x = db.session.query(models.Property,
                             models.Element,
                             models.Data.score,
                             func.count(models.Data.id)
        ).group_by(models.Data.score
        ).group_by(models.Property.id
        ).group_by(models.Element
        ).join(models.Element
        ).join(models.Data
        ).all()

        b = map(lambda x: {x[0].id: {"property": x[0], "element": x[1], "scores": {x[2]: x[3]}}}, x)
        data = {}
        for d in b:
            merge_dict(data, d)

        values = {True, None}
        for x in data:
            data[x]["scores"]
            for v in values:
                try:
                    data[x]["scores"][v]
                except KeyError:
                    data[x]["scores"][v] = 0
            data[x]["scores"]["percentage"] = int(round(((float(data[x]["scores"][True])/(float(data[x]["scores"][True]+data[x]["scores"][None])))*100),0))

        return render_template("elements.html", data=data, auth=usermanagement.check_login())