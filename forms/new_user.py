from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    nickname = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=20)])

    name = StringField('Ваше имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Адрес почты', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8), EqualTo('password_again', message='Пароли не совпадают')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])

    submit = SubmitField('Создать аккаунт')
