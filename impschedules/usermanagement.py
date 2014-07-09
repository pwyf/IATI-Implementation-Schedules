from flask import Flask, render_template, flash, request, Markup, session, redirect, url_for, escape, Response, current_app, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

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
