from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_babel import lazy_gettext as _

class UploadBankForm(FlaskForm):
    name = StringField(_('Bank'), validators=[
        DataRequired(message=_('This field is required.')),
        Length(min=3, max=100)
    ])
    file = FileField(_('Question Bank File'), validators=[
        DataRequired(message=_('This field is required.')),
        FileAllowed(['json', 'txt'], _('JSON or TXT files only!')),
        FileSize(max_size=3 * 1024 * 1024, message=_('File must be less than 3MB'))
    ])
    submit = SubmitField(_('Upload'))

class DeleteBankForm(FlaskForm):
    submit = SubmitField(_('Delete'))

class QuizConfigForm(FlaskForm):
    quantity = IntegerField(_('Number of Questions'), validators=[
        DataRequired(message=_('This field is required.')),
        NumberRange(min=1, max=100, message=_('Between 1 and 100 questions'))
    ])
    level = SelectField(_('Level'), choices=[
        ('all', _('All levels')),
        ('easy', _('Easy')),
        ('medium', _('Medium')),
        ('hard', _('Hard')),
    ])
    time_limit = SelectField(_('Time Limit'), choices=[
        ('0', _('No limit')),
        ('600', _('10 minutes')),
        ('1800', _('30 minutes')),
        ('3600', _('1 hour'))
    ])
    submit = SubmitField(_('Start Quiz'))

class AnswerForm(FlaskForm):
    pass