import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


ROLE_USER = 0
ROLE_ADMIN = 1

class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, 
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_seen = sqlalchemy.Column(sqlalchemy.DateTime,
                                  default=datetime.datetime.now)
    role = sqlalchemy.Column(sqlalchemy.SmallInteger, default=ROLE_USER)
    profile_photo = sqlalchemy.Column(sqlalchemy.BLOB, default=open('/Users/eremin/Documents/GitHub/PGI/static/icons/favicon.png', "rb").read())
    # Связь с таблицей Comments
    comments = orm.relation("Comments", back_populates='user')
    
    def __repr__(self):
        return f"It is {self.name} {self.second_name} number {self.id}\
        \n created {self.date_created}. His e-mail is {self.email}. His nickname id {self.nickname}"
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email.encode()).hexdigest() + '?d=identicon&s=' + str(size)


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    unix_time = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    mat_file = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    # Свящь с таблицей Users
    user = orm.relation('User')

