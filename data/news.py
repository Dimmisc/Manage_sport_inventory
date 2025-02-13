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
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    users = orm.relationship('Users')
    idtype = orm.relationship("Idtype")
    request = orm.relationship("Request", back_populates='asortiment')
    purchase_plans = orm.relationship("PurchasePlan", back_populates='asortiment')


class Request(SqlAlchemyBase):
    __tablename__ = 'request'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    description = sqlalchemy.Column(sqlalchemy.String)
    date_start = sqlalchemy.Column(sqlalchemy.String)
    date_end = sqlalchemy.Column(sqlalchemy.String)
    approved = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    id_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    name_user = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relationship('Users')
    id_item = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("asortiment.id"))
    asortiment = orm.relationship("Asortiment")


class PurchasePlan(SqlAlchemyBase):
    __tablename__ = 'purchase_plan'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    asortiment_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('asortiment.id'), nullable=True)
    asortiment = orm.relationship("Asortiment", back_populates="purchase_plans")
    
    item_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    supplier = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, default='Планируется')

    def __repr__(self):
        return f"<PurchasePlan> {self.item_name} - {self.quantity} шт. от {self.supplier}"