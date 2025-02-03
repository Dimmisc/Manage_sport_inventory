import os
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from forms.news import AsortimentForm, RequestForm
from forms.user import RegisterForm, LoginForm
from data.news import Asortiment, Request
from data.category import Idtype
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
login_manager.login_view = 'login'


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


def main():
    db_session.global_init("db/blogs.db")
    app.run(debug=True)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(Users, user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        user = db_sess.query(Users).filter_by(id=current_user.id).first()
        news = db_sess.query(Asortiment).filter((Asortiment.users == current_user) | (Asortiment.is_private != True))
    else:
        news = db_sess.query(Asortiment).filter(Asortiment.is_private != True)
        user = db_sess.query(Users).filter(Users.id == current_user)
    return render_template("index.html", news=news, user=user)


@app.route("/admin_panel")
@login_required
def admin_panel():
    db_sess = db_session.create_session()
    if current_user.user_access == "admin":
        items = db_sess.query(Asortiment).all()
        requests = db_sess.query(Request).all()
        users = db_sess.query(Users).all()
        types = db_sess.query(Idtype)
        return render_template("admin_panel.html", items=items, requests=requests, types=types, users=users, title="Управление сайтом")
    else:
        return redirect("/")


@app.route("/edit_item/<int:id_item>", methods=["GET", "POST"])
@login_required
def edit_item(id_item):
    db_sess = db_session.create_session()
    form = AsortimentForm()
    item = db_sess.query(Asortiment).filter_by(id=id_item).first()
    if form.validate_on_submit():
        print("one")
    return render_template("edit_item.html", title="Редактирование предмета", form=form, item=item)


@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_news():
    form = AsortimentForm()
    print(False)
    if form.validate_on_submit():
        print(True)
        db_sess = db_session.create_session()
        news = Asortiment()
        news.name = form.name.data
        news.status = form.status.data
        img_file = secure_filename(form.photo.data.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], img_file)
        form.photo.data.save(path)
        news.photo_href = path
        db_sess.add(news)
        db_sess.commit()
        return redirect('/')
    return render_template("add_item.html", form=form, title="Добавить объект")
    

# @app.route("/edit_user/<int:id_item>", methods=["GET", "POST"])
# @login_required
# def edit_item(id_item):
#     return render_template("edit_user.html")


# @app.route("/confirm_request/<int:id_item>", methods=["GET", "POST"])
# @login_required
# def edit_item(id_item):
#     return render_template("confirm_request.html")


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
        user = Users(name=form.name.data,
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