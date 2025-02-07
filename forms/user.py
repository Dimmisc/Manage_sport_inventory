from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    choces = [["Nonwdwe", "Nonwdwe"]]
    name = StringField("Имя")
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    access = SelectField('Доступ', choices=choces, validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    status = StringField("Статус")
    submit = SubmitField('Войти')