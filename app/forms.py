from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

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
    submit = SubmitField('Registrieren')

class ChangePasswordForm(FlaskForm):
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Altes Passwort"})
    password2 = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Neues Passwort"})
    password3 = PasswordField(validators=[DataRequired(), EqualTo('password2')], render_kw={"placeholder": "Neues Passwort"})
    submit = SubmitField('Ändern')

class ChangeUsernameForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Benutzername"})
    submit = SubmitField('Ändern')