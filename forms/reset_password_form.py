from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=8)])
    password_again = PasswordField('Введите новый пароль еще раз', validators=[DataRequired(), EqualTo('password', message="Пароли не совпадают")])
    submit = SubmitField('Установить новый пароль')
