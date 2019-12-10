# region imports
from flask import render_template, request, url_for, jsonify, redirect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from blog import app
from app.models import db, User
from app.forms import LoginForm, RegistrationForm
# endregion

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('login/login.html', title='Anmelden', form=form)
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
        return render_template('login/register.html', title='Registrieren', form=form)
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
