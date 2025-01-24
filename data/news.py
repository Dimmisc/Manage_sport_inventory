import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Asortiment(SqlAlchemyBase):
    __tablename__ = 'asortiment'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    arend = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo_href = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    id_type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('idtype.id'))

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    users = orm.relationship('Users')
    idtype = orm.relationship("Idtype", secondary="association", backref="asortiment")