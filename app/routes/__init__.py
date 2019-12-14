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

@app.route("/")
def index():
    return render_template("index.html", title="Startseite")

@app.route("/kontakt")
def contact():
    return render_template('contact.html', title="Kontakt")

white_list = ['http://127.0.0.1:5001/post_bme', 'http://127.0.0.1:5001/post_mpu']

@app.after_request
def add_cors(rv):
    r = request.referrer[:-1]
    if rv in white_list:
        rv.headers.add('Access-Control-Allow-Origin', r)
        rv.headers.add('Access-Control-Allow-Headers', 'X-CSRFToken')
        rv.headers.add('Access-Control-Allow-Credentials', 'true')
    return rv

@app.route('/get_csrf_token', methods=['GET', 'POST'])
def get_csrf_token():
    csrf_token = generate_csrf()
    return jsonify(csrf_token=csrf_token)

from app.routes.admin_pages import *
from app.routes.blog_pages import *
from app.routes.input_registration import *
from app.routes.user_pages import *