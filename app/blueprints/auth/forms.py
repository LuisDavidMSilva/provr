from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_babel import lazy_gettext as _

class RegistrationForm(FlaskForm):
    username = StringField(_('Username'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=3, max=80)
    ])
    email = StringField(_('Email'), validators=[
        DataRequired(message=_('This field is required.')),
        Email(message=_('Invalid email address.'))
    ])
    password = PasswordField(_('Password'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=12, max=128)
    ])
    confirm_password = PasswordField(_('Confirm Password'), validators=[
        DataRequired(message=_('This field is required.')),
        EqualTo('password', message=_('Passwords must match.'))
    ])
    terms = BooleanField(_('I agree to the Terms of Use'), validators=[
        DataRequired(message=_('You must agree to the Terms of Use.'))
    ])
    submit = SubmitField(_('Create Account'))

class LoginForm(FlaskForm):
    email = StringField(_('Email'), validators=[
        DataRequired(message=_('This field is required.')),
        Email(message=_('Invalid email address.'))
    ])
    password = PasswordField(_('Password'), validators=[
        DataRequired(message=_('This field is required.'))
    ])
    submit = SubmitField(_('Login'))

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(_('Current Password'), validators=[
        DataRequired(message=_('This field is required.'))
    ])
    new_password = PasswordField(_('New Password'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=12, max=128)
    ])
    confirm_password = PasswordField(_('Confirm Password'), validators=[
        DataRequired(message=_('This field is required.')),
        EqualTo('new_password', message=_('Passwords must match.'))
    ])
    submit = SubmitField(_('Change Password'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_('Email'), validators=[
        DataRequired(message=_('This field is required.')),
        Email(message=_('Invalid email address.'))
    ])
    username = StringField(_('Username'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=3, max=80)
    ])
    recovery_key = StringField(_('Recovery Key'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=12, max=36)
    ])
    submit = SubmitField(_('Request Reset'))

class SetNewPassword(FlaskForm):
    password = PasswordField(_('Password'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=12, max=128)
    ])
    confirm_password = PasswordField(_('Confirm Password'), validators=[
        DataRequired(message=_('This field is required.')),
        EqualTo('password', message=_('Passwords must match.'))
    ])
    submit = SubmitField(_('Reset Password'))

class UpdateProfilePictureForm(FlaskForm):
    picture = FileField(_('Profile Picture'), validators=[
        DataRequired(message=_('This field is required.')),
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], _('Images only!')),
        FileSize(max_size=3 * 1024 * 1024, message=_('File must be less than 3MB'))
    ])
    submit = SubmitField(_('Update Profile Picture'))

class RecoveryPassword(FlaskForm):
    email = StringField(_('Email'), validators=[
        DataRequired(message=_('This field is required.')),
        Email(message=_('Invalid email address.'))
    ])
    recovery_key = StringField(_('Recovery Key'), validators=[
        DataRequired(message=_('This field is required.'))
    ])
    password = PasswordField(_('New Password'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=12, max=128)
    ])
    confirm_password = PasswordField(_('Confirm New Password'), validators=[
        DataRequired(message=_('This field is required.')),
        EqualTo('password', message=_('Passwords must match.'))
    ])
    submit = SubmitField(_('Reset Password'))

class GenerateRecoveryKeyForm(FlaskForm):
    password = PasswordField(_('Confirm Password'), validators=[
        DataRequired(message=_('This field is required.'))
    ])
    submit = SubmitField(_('Generate Recovery Key'))