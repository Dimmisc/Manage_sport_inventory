import os
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from forms.news import AsortimentForm, RequestForm
from forms.user import RegisterForm, LoginForm
from data.news import Asortiment, Request
from data.users import Users
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from data import db_session

UPLOAD_FOLDER = 'static/images'

sqlite_database = "sqlite:///blogs.db"
engine = create_engine(sqlite_database, echo=True)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def Check_free(date_start, date_end):
    with Session(autoflush=False, bind=engine) as db:
        # получение всех объектов
        dates = db.query(Request).all()
        for p in dates:
            if date_start > p.date_start and date_start < p.date_end and date_end < p.date_end and date_end > p.date_start:
                return False
            if date_start < p.date_start and date_start < p.date_end and date_end < p.date_end and date_end > p.date_start:
                return False
            if date_start > p.date_start and date_start < p.date_end and date_end > p.date_end and date_end > p.date_start:
                return False
            else:
                return True


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(Users, user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run(debug=True)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = AsortimentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = Asortiment()
        news.title = form.name.data
        news.content = form.status.data
        news.is_private = form.arend.data
        img_file = secure_filename(form.photo_hrev.data.filename)
        print(img_file)
        path = os.path.join(app.config['UPLOAD_FOLDER'], img_file)
        print(path)
        form.photo_hrev.data.save(path)
        #img_file.save(path)
        news.image = path
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Asortiment).filter(Asortiment.id == id, Asortiment.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/request/<int:id_item>', methods=['GET', 'POST'])
@login_required
def edit_news(id_item):
    db_sess = db_session.create_session()
    item = db_sess.get(Asortiment, id_item)
    form = RequestForm()
    form.description = item.idtype.description
    print(form, item)
    if form.validate_on_submit():
        if Check_free(form.datetime_start.data, form.datetime_end.data):
            request = Request(id_item=id_item,
                              id_user=current_user,
                              date_start=form.datetime_start.data,
                              date_end=form.datetime_end.data,
                              description="None"
                              )
            db_sess.add(request)
            db_sess.commit()
            return redirect()
        else:
            return render_template("request.html",
                                   form=form,
                                   item=item,
                                   message="Товар занят в указаное вами время!",
                                   title="Аренда",
                                   )
    return render_template("request.html",
                           form=form,
                           item=item,
                           title="Аренда",
                           )


# @app.route("/admin_panel")
# @login_required
# def admin_panel():
#     db_sess = db_session.create_session()
#     # user = db_sess.query(Users).filter_by(id=current_user)
#     # if user.

@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(Asortiment).filter((Asortiment.users == current_user) | (Asortiment.is_private != True))
    else:
        news = db_sess.query(Asortiment).filter(Asortiment.is_private != True)
    return render_template("index.html", news=news)

def index_prod_info():
    db_sess = db_session.create_session()
    asor = db_sess.query(Asortiment).all()
    return render_template("index.html", news=asor) #Создай новый html документ


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают",
                                   )
        db_sess = db_session.create_session()
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message= "Такой пользователь уже есть",
                                   )
        user = Users(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            password=form.password.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form,
                               )
    return render_template('login.html',
                           title='Авторизация',
                           form=form,
                           )


if __name__ == '__main__':
    main()

    # form = AsortimentForm()
    # if request.method == "GET":
    #     db_sess = db_session.create_session()
    #     news = db_sess.query(Asortiment).filter(Asortiment.id == id, Asortiment.user == current_user).first()
    #     if news:
    #         form.title.data = news.title
    #         form.content.data = news.content
    #         form.is_private.data = news.is_private
    #     else:
    #         abort(404)
    # if form.validate_on_submit():
    #     db_sess = db_session.create_session()
    #     news = db_sess.query(Asortiment).filter(Asortiment.id == id, Asortiment.user == current_user).first()
    #     if news:
    #         news.title = form.title.data
    #         news.content = form.content.data
    #         news.is_private = form.is_private.data
    #         db_sess.commit()
    #         return redirect('/')
    #     else:
    #         abort(404)
    # return render_template('news.html', title='Редактирование новости', form=form)