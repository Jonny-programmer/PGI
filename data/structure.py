import datetime
from hashlib import md5

import jwt
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from config import SECRET_KEY
from .db_session import SqlAlchemyBase


ROLE_USER = 0
ROLE_ADMIN = 1


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_seen = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_admin = sqlalchemy.Column(sqlalchemy.SmallInteger, default=ROLE_USER)

    profile_pic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # Связь с таблицей Comments
    comments = orm.relation("Comments", back_populates='user')
    
    def info(self):
        return f"\n\n Фамилия и имя: {self.name} {self.surname} \n Имя пользователя: \'{self.nickname}\' \n " \
               f"Почтовый адрес: {self.email} \n Номер: {self.id} \n Создан: {self.last_seen}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email.encode()).hexdigest() + '?d=identicon&s=' + str(size)

    def get_reset_password_token(self, expires_in=600):
        from time import time
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, SECRET_KEY,
                                 algorithms=['HS256'])['reset_password']
        except:
            return
        return user_id


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    date_created = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    time_related = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    mat_file = sqlalchemy.Column(sqlalchemy.String, index=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    # Свящь с таблицей Users
    user = orm.relation('User')


class Email_services(SqlAlchemyBase):
    __tablename__ = 'email_services'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    domain = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    url = sqlalchemy.Column(sqlalchemy.String, nullable=False)