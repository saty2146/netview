from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class VlanForm(FlaskForm):
    post = StringField('post', validators=[DataRequired()])

class MacForm(FlaskForm):
    find_item = StringField('find_item', validators=[DataRequired()])
    file_option = SelectField('file_option', coerce=int)

class UpdateForm(FlaskForm):
    post = StringField('post')

class ArpForm(FlaskForm):
    find_item = StringField('find_item', validators=[DataRequired()])
    #file_option = SelectField('file_option',  choices = [('cpp', 'C++'), ('py', 'Python')])
    file_option = SelectField('file_option', coerce=int)
