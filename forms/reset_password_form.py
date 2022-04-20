from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password_again = PasswordField('Введите новый пароль еще раз', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Установить новый пароль')
