from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class AsortimentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    status = StringField('Состояние')
    # content = TextAreaField("Содержание")
    arend = BooleanField("Состояние аренды")
    photo_hrev = FileField('Изображение')
    submit = SubmitField("Применить")

class RecuestForm(FlaskForm):
    id_user = IntegerField('Id пользователя')
    id_item = IntegerField('Id товара')
    description = TextAreaField('Причина аренды')
    datetime_start = DateField('Начало аренды')
    datetime_end = DateField('Окончание аренды')
    
