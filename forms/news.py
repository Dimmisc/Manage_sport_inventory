from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired


class AsortimentForm(FlaskForm):
    choces = [["Nonwdwe", "Nonwdwe"]]
    name = StringField('Название', validators=[DataRequired()])
    status = StringField('Состояние')
    type = SelectField('Объект', choices=choces)
    photo = FileField('Изображение')
    submit = SubmitField("Добавить")

class RequestForm(FlaskForm):
    description = TextAreaField('Причина аренды')
    datetime_start = DateField('Начало аренды')
    datetime_end = DateField('Окончание аренды')
    confirmed = BooleanField('Одобрить?')
    submit = SubmitField("Арендовать")

class IdtypeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField("Добавить")