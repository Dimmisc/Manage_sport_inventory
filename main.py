import os
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from forms.news import AsortimentForm, RequestForm, IdtypeForm
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
    date_start = str(date_start)
    date_end = str(date_end)
    db_sess = db_session.create_session()
    dates = db_sess.query(Request).all()
    if dates:
        for p in dates:
            if date_start > p.date_start and date_start < p.date_end and date_end < p.date_end and date_end > p.date_start:
                return False
            if date_start < p.date_start and date_start < p.date_end and date_end < p.date_end and date_end > p.date_start:
                return False
            if date_start > p.date_start and date_start < p.date_end and date_end > p.date_end and date_end > p.date_start:
                return False
    return True


def update_requests(db_sess):
    items = db_sess.query(Request).all()
    for item in items:
        if item.asortiment == None:
            db_sess.delete(item)
    db_sess.commit()
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


@app.route('/delete_item/<int:id_item>', methods=['GET', 'POST'])
@login_required
def delete_item(id_item):
    db_sess = db_session.create_session()
    item = db_sess.query(Asortiment).filter(Asortiment.id == id_item).first()
    if item:
        db_sess.delete(item)
        db_sess.commit()
        update_requests(db_sess)
    else:
        abort(404)
    return redirect('/admin_panel')


@app.route('/request/<int:id_item>', methods=['GET', 'POST'])
@login_required
def edit_news(id_item):
    db_sess = db_session.create_session()
    item = db_sess.query(Asortiment).filter_by(id=id_item).first()
    form = RequestForm()
    print(form, item)
    if form.validate_on_submit():
        if Check_free(form.datetime_start.data, form.datetime_end.data) == True:
            print("notsome")
            request = Request(id_item=id_item,
                              id_user=current_user.id,
                              user=db_sess.query(Users).filter_by(id=current_user.id).one(),
                              date_start=str(form.datetime_start.data),
                              date_end=str(form.datetime_end.data),
                              description="None"
                              )
            db_sess.add(request)
            db_sess.commit()
            return redirect("/")
        else:
            print("some")
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
        item = db_sess.query(Asortiment).all()
    else:
        item = db_sess.query(Asortiment).all()
        user = None
    return render_template("index.html", 
                           news=item, 
                           user=user, 
                           title="Главная"
                           )


@app.route("/arrended")
@login_required
def arrended():
    db_sess = db_session.create_session()
    items = db_sess.query(Request).filter_by(id_user=current_user.id).all()
    trtp = len(items) != 0
    return render_template("arrended.html",
                           items=items,
                           trtp=trtp,
                           title="Ваши арендованые предметы"
                           )


@app.route("/admin_panel")
@login_required
def admin_panel():
    db_sess = db_session.create_session()
    if current_user.user_access == "admin":
        items = db_sess.query(Asortiment).all()
        requests = db_sess.query(Request).all()
        users = db_sess.query(Users).all()
        types = db_sess.query(Idtype).all()
        return render_template("admin_panel.html", 
                               items=items, 
                               requests=requests, 
                               types=types, 
                               users=users, 
                               title="Управление сайтом"
                               )
    else:
        return redirect("/")


@app.route("/edit_item/<int:id_item>", methods=["GET", "POST"])
@login_required
def edit_item(id_item):
    db_sess = db_session.create_session()
    form = AsortimentForm()
    if form.validate_on_submit():
        print(form.status.data, form.name.data)
        db_sess.query(Asortiment).filter_by(id=id_item).update({'name': form.name.data, 'status':form.status.data})
        db_sess.commit()
        return redirect("/admin_panel")
    item = db_sess.query(Asortiment).filter_by(id=id_item).first()
    form.name.data = item.name
    form.status.data = item.status
    return render_template("edit_item.html",
                           title="Редактирование предмета",
                           form=form,
                           item=item,
                           )


@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = AsortimentForm()
    print(False)
    if form.validate_on_submit():
        print(True)
        db_sess = db_session.create_session()
        item = Asortiment()
        item.name = form.name.data
        item.status = form.status.data
        img_file = secure_filename(form.photo.data.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], img_file)
        form.photo.data.save(path)
        item.photo_href = path
        type = db_sess.query(Idtype).filter_by(name=form.type.data).first()
        user = db_sess.query(Users).filter_by(id=current_user.id).first()
        item.users = user
        if type:
            item.idtype = type
        db_sess.add(item)
        db_sess.commit()
        return redirect('/admin_panel')
    return render_template("add_item.html", form=form, title="Добавить объект")


@app.route('/add_type', methods=['GET', 'POST'])
@login_required
def add_type():
    form = IdtypeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        type = Idtype(name=form.name.data,
                      description=form.description.data,
                      )
        db_sess.add(type)
        db_sess.commit()
        return redirect("/admin_panel")
    return render_template("add_type.html", form=form, title="Добавление типов")


@app.route("/edit_user/<int:id_user>", methods=["GET", "POST"])
@login_required
def edit_user(id_user):
    form = LoginForm()
    db_sess = db_session.create_session()
    user = db_sess.query(Users).filter_by(id=id_user).first()
    types = db_sess.query(Idtype.name).all()
    print([(types[i][0], types[i][0]) for i in range(len(types))] ,len(types))
    choices = [[types[i][0], types[i][0]] for i in range(len(types))]
    form.choces = choices
    form.email.data = user.email
    form.password.data = 'd'
    if form.validate_on_submit():
        print(form.access.data)
        db_sess.query(Users).filter_by(id=id_user).update({'user_access': form.access.data,
                                                          'about': form.status.data}, 
                                                          )
        db_sess.commit()
        return redirect("/admin_panel")
    
    form.access.data = user.user_access
    form.status.data = user.about
    return render_template("edit_user.html", form=form, user=user, title="Изменение пользователя")


@app.route("/confirm_request/<int:id_request>", methods=["GET", "POST"])
@login_required
def confirm_request(id_request):
    form = RequestForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        db_sess.query(Request).filter_by(id=id_request).update({'description': form.description.data,
                                                               'approved': form.confirmed.data},
                                                               )
        db_sess.commit()
        return redirect("/admin_panel")
    request = db_sess.query(Request).filter_by(id=id_request).first()
    form.description.data = request.description
    form.confirmed.data = request.approved
    return render_template("confirm_request.html",
                           form=form, 
                           request=request, 
                           title="Одобрение запроса"
                           )


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