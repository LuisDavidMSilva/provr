from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('UserName', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = StringField('Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = StringField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = StringField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Login')