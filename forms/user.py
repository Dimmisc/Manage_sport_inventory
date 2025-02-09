from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, NumberRange


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    name = StringField("Имя")
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    status = StringField("Статус")
    submit = SubmitField('Войти')

class EU(FlaskForm):
    choces = [["User", "User"], ["admin", "admin"], ["baned", "baned"]]
    status = StringField("Cтатус")
    access = SelectField('Доступ', choices=choces)
    submit = SubmitField('Изменить')

class IU(FlaskForm):
    choces = [["Nonwdwe", "Nonwdwe"]]
    name = StringField('Название', validators=[DataRequired()])
    status = StringField('Состояние')
    submit = SubmitField("Добавить")

class PurchasePlanForm(FlaskForm):
    item_name = StringField('Название товара (если нет в ассортименте)')
    
    asortiment_id = SelectField('Товар из ассортимента', coerce=int, choices=[])
    
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Цена за единицу', validators=[DataRequired(), NumberRange(min=0)])
    supplier = StringField('Поставщик', validators=[DataRequired()])
    submit = SubmitField('Добавить в план закупок')