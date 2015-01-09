from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('../config.py')
app.secret_key = app.config["SECRET_KEY"]
db = SQLAlchemy(app)

import usermanagement
import api
import routes
import isimport
import fields
import organisations