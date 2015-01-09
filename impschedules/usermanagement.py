from flask import Flask, render_template, flash, request, session, redirect, url_for, current_app, escape
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import models
from impschedules import app, db

def login_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash('You must log in to access that page.', 'error')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)
    return decorated_function

def check_login():
    if ("username" in session):
        return session["admin"]
    else:
        return None

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if (request.method=='POST'):
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        getuser = models.ImpSchedUser.query.filter_by(username=username).first()
        if ((getuser) and (getuser.check_password(password))):
            session['username'] = escape(request.form['username'])
            session['user_id'] = getuser.id
            if (getuser.admin == 1):
                session['admin'] = getuser.admin
            flash('Welcome back.', 'success')
            return redirect(url_for('index'))
        else:
            flash("Could not find that user. Please try again.", 'error')
            return redirect(url_for('index'))
    else:
        return render_template("login.html")

@app.route('/logout/')
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))