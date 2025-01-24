import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

class Request(SqlAlchemyBase):
    __tablename__ = 'request'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    description = sqlalchemy.Column(sqlalchemy.String)
    created_date_start = sqlalchemy.Column(sqlalchemy.DateTime)
    created_date_end = sqlalchemy.Column(sqlalchemy.DateTime)

    id_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    users = orm.relationship('Users')
    id_item = orm.relationship("Asortiment", secondary="association", backref="request")
