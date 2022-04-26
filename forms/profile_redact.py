from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length


class UpdateAccountForm(FlaskForm):
    picture = FileField('Обновить фото профиля', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    nickname = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=20)])

    name = StringField('Ваше имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Адрес почты', validators=[DataRequired(), Email()])

    submit = SubmitField('Обновить информацию')
