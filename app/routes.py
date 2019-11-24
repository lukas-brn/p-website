# from app import db, app, login
# from app.models import Blog_Post, User
# from app.forms import LoginForm, RegistrationForm

# from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
# from wtforms.validators import ValidationError
# from flask_sqlalchemy import SQLAlchemy
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Blog_Post

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError

@app.route("/")
def index():
    return render_template("index.html", title="Startseite")

@app.route("/blog")
def blog():
    posts = Blog_Post.query.order_by(Blog_Post.time_created).all()
    return render_template("blog.html", title="Blog", posts=posts)

@app.route("/console", methods=['POST', 'GET'])
@login_required
def console():
    if request.method == 'POST':
        caption_content = request.form['caption']
        body_content = request.form['body']
        new_post = Blog_Post(caption=caption_content, body=body_content)

        try: 
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('console'))
            raise Exception("error accured")
        except Exception as e: 
            return render_template("error.html", title="Error", error=e)      
    else:
        tasks = Blog_Post.query.order_by(Blog_Post.time_created).all()
        return render_template("console.html", title="Console", tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):
    to_delete = Blog_Post.query.get_or_404(id)

    try: 
        db.session.delete(to_delete)
        db.session.commit()
        return redirect(url_for('console'))
    except Exception as e: 
            return e

@app.route("/edit/<int:id>", methods=['POST', 'GET'])
def edit(id): 
    task = Blog_Post.query.get_or_404(id)

    if request.method == 'POST':
        task.caption = request.form['caption']
        task.body = request.form['body']
        try: 
            db.session.commit()
            return redirect(url_for('console'))
        except Exception as e: 
            return render_template("error.html", title="Error", error=e)
    else:
        return render_template("edit.html", title="Edit", task=task)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="404")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
