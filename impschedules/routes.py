from flask import Flask, render_template, flash, request, Markup, session, redirect, url_for, escape, Response, current_app, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sys, os
from lxml import etree
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime
import re
import json
import urllib
import string
import random
import iatiimplementationxml.toxml as toxml
import collections
from functools import wraps
import StringIO
import csv
from icalendar import Calendar, Event

from impschedules import app, db

import models, properties, api
from isfunctions import *
from isprocessing import *
import publisher_redirects, usermanagement

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
