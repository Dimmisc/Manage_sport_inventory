import sqlalchemy

from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('asortiment', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('asortiment.id')),
                                     sqlalchemy.Column('idtype', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('idtype.id'))
                                     )



class Idtype(SqlAlchemyBase):
    __tablename__ = 'idtype'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
