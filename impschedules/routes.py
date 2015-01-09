from flask import Flask, render_template, redirect, url_for, current_app

from impschedules import app, db

import models, properties, usermanagement

@app.route("/")
def index():
    return render_template("dashboard.html", auth=usermanagement.check_login())

@app.route("/about/")
def about():
    return render_template("about.html", auth=usermanagement.check_login())


@app.route("/impschedules/")
@usermanagement.login_required
def show_impschedules():
    impschedules = db.session.query(models.ImpSchedule,
                                    models.Publisher
                ).join(models.Publisher
                ).all()
    return render_template("impschedules.html",
                impschedules=impschedules,
                auth=usermanagement.check_login())

@app.route("/timeline/")
def timeline(id=id):
    elements = db.session.query(models.Property.parent_element, 
                            models.Property.defining_attribute_value, 
                            models.Element.id, 
                            models.Element.description, 
                            models.Element.level,
                            models.Element.name,
                            models.Property.id.label("propertyid")
        ).distinct(
        ).join(models.Element).all()
    return render_template("timeline.html", elements=elements, auth=usermanagement.check_login())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', auth=usermanagement.check_login()), 404

#@app.errorhandler(500)
#def internal_server_error(e):
#    return render_template('500.html', error=e, auth=usermanagement.check_login()), 500
