import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

class Request(SqlAlchemyBase):
    __tablename__ = 'request'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_item = sqlalchemy.relationship(
    time = 
    
