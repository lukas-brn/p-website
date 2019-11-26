from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import os

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug.datastructures import MultiDict
from wtforms.validators import ValidationError

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blog_posts.db',
    DEBUG = True,
    SECRET_KEY = '/x83j/xe7/x97/x9e///xf1/x17/xca/xd2/xde/x8f/xa9S/xca/xce/xad/x7f}/x03/x9d{/x14/xfe/x9b/xb1$/x143/xd5n~'
)
db = SQLAlchemy(app)
csrf = CSRFProtect()
csrf.init_app(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

current_error = ""

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
    if current_user.admin_acc == True:
        if request.method == 'POST':
            try: 
                db.session.add(Blog_Post(caption=request.form['caption'], body=request.form['body']))
                db.session.commit()
                return redirect(url_for('admin'))
            except Exception as e: 
                return render_template("error.html", title="Error", error=e)      
        else:
            posts = Blog_Post.query.order_by(Blog_Post.time_created).all()
            users = User.query.order_by(User.user_id).all()
            return render_template("admin.html", title="Admin", posts=posts, users=users)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    if current_user.admin_acc == True:
        try: 
            db.session.delete(Blog_Post.query.get_or_404(id))
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e: 
                return render_template("error.html", title="Error", error=e)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit(id):
    if current_user.admin_acc == True:
        post = Blog_Post.query.get_or_404(id)

        if request.method == 'POST':
            post.caption = request.form['caption']
            post.body = request.form['body']
            try: 
                db.session.commit()
                return redirect(url_for('admin'))
            except Exception as e: 
                return render_template("error.html", title="Error", error=e)
        else:
            return render_template("edit.html", title="Edit", post=post)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/manage_admins/<int:user_id>")
@login_required
def manage_admin(user_id):
    if current_user.admin_acc == True:
        try: 
            user = User.query.get_or_404(user_id)
            if current_user.user_id != user.user_id:
                user.set_admin(not user.admin_acc)
                db.session.commit()
                return redirect(url_for('admin'))
            else:
                raise Exception("Sie können nicht ihren eigenen Admin-Status verändern")
        except Exception as e: 
                return render_template("error.html", title="Error", error=e)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="404")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('login.html', title='Login', form=form)
    elif request.method == 'POST':
        form = request.form
        user = User.query.filter_by(username=form['username'].strip()).first()
        if user is None or not user.check_password(form['password'].strip()):
            return jsonify({"text": "Benutzername oder Passwort ist falsch.", "redirect": False})
        else: 
            login_user(user, remember=form['remember_me'])
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return jsonify({"text": next_page, "redirect": True})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        form = RegistrationForm()
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('register.html', title='Register', form=form)
    elif request.method == 'POST':
        form = request.form
        if User.query.filter_by(username=form['username'].strip()).first() is not None:
            return jsonify({"text": "Bitte wählen Sie einen anderen Benutzernamen.", "redirect": False})
        elif User.query.filter_by(email=form['email'].strip()).first() is not None:
            return jsonify({"text": "Bitte wählen Sie eine andere Email-Addresse.", "redirect": False})
        else: 
            user = User(username=form['username'].strip(), email=form['email'].strip())
            user.set_password(form['password'].strip())
            db.session.add(user)
            db.session.commit()
            return jsonify({"text": url_for('login'), "redirect": True})
                
class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Benutzername"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Passwort"})
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Benutzername"})
    email = StringField(validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Passwort"})
    password2 = PasswordField(validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Passwort wiederholen"})
    submit = SubmitField('Register')

if __name__ == "__main__":
    db.create_all()

    # User.query.get_or_404(1).set_admin(True)
    # db.session.commit()

    # db.session.delete(User.query.get_or_404(1))
    # db.session.commit()

    app.run()
