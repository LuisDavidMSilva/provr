from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('UserName', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=12, max=128)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    terms = BooleanField('I agree to the Terms of Use', validators=[DataRequired()])
    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Login')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class UpdateProfilePictureForm(FlaskForm):
    picture = FileField('Profile Picture', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('Update Profile Picture')