from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ResetPasswordRequestForm(FlaskForm):
    nick = StringField('Почтовый адрес или имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Запросить сброс пароля')