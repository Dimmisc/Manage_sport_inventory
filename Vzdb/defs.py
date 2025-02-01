from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from data.news import Asortiment
from data.users import Users


sqlite_database = "sqlite:///blogs.db"
engine = create_engine(sqlite_database, echo=True)


class Base(DeclarativeBase): pass


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)


Base.metadata.create_all(bind=engine)

with Session(autoflush=False, bind=engine) as db:
    # получение всех объектов
    people = db.query(Users).all()
    for p in people:
        print(f"{p.id}, {p.name} ({p.status})")