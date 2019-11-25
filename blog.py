from flask import Flask, render_template, flash, redirect, url_for, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import os

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blog_posts.db',
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

# TODO: same secret key is needed, implement a better one
#SECRET_KEY = os.urandom(32)
#app.config['SECRET_KEY'] = SECRET_KEY

class Blog_Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.now() )

    def __repr__(self):
        return '<Blog_Post %r>' % self.id

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(120))
    email = db.Column(db.String, nullable=False, unique=True)
    admin_acc = db.Column(db.Boolean, default=False, nullable=False)
    is_active = True
    is_authenticated = True

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.user_id

    def set_admin(self, is_admin):
        self.admin_acc = is_admin

@app.context_processor
def inject_login_status():
    return dict(login_status=current_user.is_authenticated)

@app.route("/")
def index():
    return render_template("index.html", title="Startseite")

@app.route("/blog")
def blog():
    posts = Blog_Post.query.order_by(Blog_Post.time_created).all()
    return render_template("blog.html", title="Blog", posts=posts)

@app.route("/admin", methods=['POST', 'GET'])
@login_required
def admin():
    if request.method == 'POST':
        caption_content = request.form['caption']
        body_content = request.form['body']
        new_post = Blog_Post(caption=caption_content, body=body_content)

        try: 
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e: 
            return render_template("error.html", title="Error", error=e)      
    else:
        posts = Blog_Post.query.order_by(Blog_Post.time_created).all()
        users = User.query.order_by(User.user_id).all()
        return render_template("admin.html", title="Admin", posts=posts, users=users)

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    to_delete = Blog_Post.query.get_or_404(id)

    try: 
        db.session.delete(to_delete)
        db.session.commit()
        return redirect(url_for('admin'))
    except Exception as e: 
            return e

@app.route("/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit(id): 
    task = Blog_Post.query.get_or_404(id)

    if request.method == 'POST':
        task.caption = request.form['caption']
        task.body = request.form['body']
        try: 
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e: 
            return render_template("error.html", title="Error", error=e)
    else:
        return render_template("edit.html", title="Edit", task=task)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="404")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # TODO: add message incorrect data
            return redirect(url_for('login'))
        # TODO: add message logged in
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
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
        # TODO: add message registered
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = StringField(validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password2 = PasswordField(validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Repeat Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            # TODO: warning: different username
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            # TODO: warning: different email
            raise ValidationError('Please use a different email address.')

if __name__ == "__main__":
    db.create_all()
    # try: 
    #     db.session.delete(User.query.get_or_404(1))
    #     db.session.commit()
    # except Exception: 
    #     pass
    app.run()