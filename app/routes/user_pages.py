# region imports
from flask import render_template, request, jsonify, url_for
from flask_login import current_user, login_required
from app.forms import ChangePasswordForm, ChangeUsernameForm
from app.models import User
from werkzeug.urls import url_parse
from blog import db, app
#endregion

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_page():
    if request.method == 'GET':
        return render_template('user/user.html', title='Nutzer')
    elif request.method == 'POST':
        content = f'''
        <p>ID: { current_user.id }</p>
        <p>Benutzername: { current_user.username }</p>
        <p>Email: { current_user.email }</p>
        <p>Admin: { current_user.admin_acc }</p>
        '''
        return jsonify({'body': content})

@app.route('/user/settings', methods=['POST'])
@login_required
def user_settings():
    content = f'''
    <a href="{ url_for('change_password') }" class="button">Passwort ändern</a>
    <a href="{ url_for('change_username') }" class="button">Benutzername ändern</a>
    '''
    return jsonify({'body': content})

@app.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'GET':
        form = ChangePasswordForm()
        return render_template('user/change_password.html', title='Passwort ändern', form=form)
    else:
        form = request.form
        if current_user.check_password(form['password']):
            if form['password2'] == form['password3']:
                current_user.set_password(form['password2'])
                db.session.commit()
                return jsonify({"text": url_for('user_page'), "redirect": True})
            else:
                return jsonify({"text": "Die 2 neuen Passwörter stimmen nicht überein.", "redirect": False})
        else: 
            return jsonify({"text": "Das ursprüngliche Passwort passt nicht.", "redirect": False})

@app.route('/user/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    if request.method == 'GET':
        form = ChangeUsernameForm()
        return render_template('user/change_username.html', title='Benutzernamen ändern', username=current_user.username, form=form)
    elif request.method == 'POST':
        if User.query.filter(User.username == request.form['username']).first() is not None:
            return jsonify({"text":"Bitte wählen Sie einen anderen Benutzernamen.", "redirect": False})
        else:
            current_user.username = request.form['username']
            db.session.commit()
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('user_settings')
            return jsonify({"text": next_page, "redirect": True})