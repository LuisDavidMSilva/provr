from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class UploadBankForm(FlaskForm):
    name = StringField('Bank', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    file = FileField('Question Bank File', validators=[
        DataRequired(),
        FileAllowed(['json', 'txt'], 'JSON or TXT files only!')
    ])
    submit = SubmitField('Upload')

class DeleteBankForm(FlaskForm):
    submit = SubmitField('Delete')

class QuizConfigForm(FlaskForm):
    quantity = IntegerField('Number of Questions', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message='Between 1 and 100 questions')
    ])
    level = SelectField('Level', choices=[
        ('all', 'All levels'),
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ])
    time_limit = SelectField('Time Limit', choices=[
        ('0', 'No limit'),
        ('600', '10 minutes'),
        ('1800', '30 minutes'),
        ('3600', '1 hour')
    ])
    submit = SubmitField('Start Quiz')

class AnswerForm(FlaskForm):
    pass