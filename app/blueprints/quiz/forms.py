from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

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