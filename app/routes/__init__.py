# region imports
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from blog import app, db, ALLOWED_EXTENSIONS
from app.models import Blog_Post, User
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm, ChangeUsernameForm
from datetime import datetime
from sqlalchemy import extract
import os
from werkzeug.utils import secure_filename
import re

from flask import jsonify, session
from flask_wtf.csrf import generate_csrf
# endregion

@app.errorhandler(404)
def page_not_found(e):
    current_url = request.url
    if current_url[-1] == '/':
        return redirect(current_url[0:-1])
    elif current_url.find('blog')>=0:
        return redirect( url_for('blog') )
    return render_template("errors/404.html", title="404")

@app.route('/', defaults={'msg': ''})
@app.route("/<string:msg>")
def index(msg=''):
    return render_template("index.html", title="Startseite", msg=msg)

@app.route("/kontakt")
def contact():
    return render_template('contact.html', title="Kontakt")

from app.routes.admin_pages import *
from app.routes.blog_pages import *
from app.routes.input_registration import *
from app.routes.user_pages import *