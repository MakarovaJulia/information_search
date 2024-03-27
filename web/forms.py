from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    query = StringField('Введите запрос', validators=[DataRequired()])
    submit = SubmitField('Отправить')