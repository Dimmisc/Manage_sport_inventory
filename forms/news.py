import datetime
import sqlalchemy
from sqlalchemy import orm, create_engine
from sqlalchemy.orm import Session
from .db_session import SqlAlchemyBase

sqlite_database = "sqlite:///blogs.db"
engine = create_engine(sqlite_database, echo=True)

class AsortimentForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    status = StringField('Состояние')
    # content = TextAreaField("Содержание")
    arend = BooleanField("Состояние аренды")
    photo_hrev = FileField('Изображение')
    submit = SubmitField("Применить")

class RecuestForm(FlaskForm):
    id_user = IntegerField('Id пользователя')
    id_item = IntegerField('Id товара')
    description = TextAreaField('Причина аренды')
    datetime_start = DateField('Начало аренды')
    datetime_end = DateField('Окончание аренды')

    def date_check(self):
        with Session(autoflush=False, bind=engine) as db:
            # получение всех объектов
            dates = db.query(Request).all()
            for p in dates:
                if self.datetime_start > p.datetime_start and self.datetime_start < p.datetime_end and self.datetime_end < p.datetime_end and self.datetime_end > p.datetime_start:
                    return False
                if self.datetime_start < p.datetime_start and self.datetime_start < p.datetime_end and self.datetime_end < p.datetime_end and self.datetime_end > p.datetime_start:
                    return False
                if self.datetime_start > p.datetime_start and self.datetime_start < p.datetime_end and self.datetime_end > p.datetime_end and self.date_end > p.datetime_start:
                    return False
                else:
                    return True
    
