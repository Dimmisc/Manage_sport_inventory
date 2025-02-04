from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired


class AsortimentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    status = StringField('Состояние')
    type = StringField('Объект')
    # content = TextAreaField("Содержание")
    photo = FileField('Изображение')
    submit = SubmitField("Добавить")

class RequestForm(FlaskForm):
    id_item = IntegerField('Id товара')
    description = TextAreaField('Причина аренды')
    datetime_start = DateField('Начало аренды')
    datetime_end = DateField('Окончание аренды')
    confirmed = BooleanField('Одобрить?')
    submit = SubmitField("Применить")

class IdtypeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание')
<<<<<<< HEAD
    submit = SubmitField("Добавить")
=======
>>>>>>> ca9d584e28f6f2933817848f0577c6b3680f0efc
