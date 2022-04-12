from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo


class RegisterForm(FlaskForm):
    nickname = StringField('Имя пользователя', validators=[DataRequired()])

    name = StringField('Ваше имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Адрес почты', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('password_again', message='Passwords must match')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])

    submit = SubmitField('Создать аккаунт')
