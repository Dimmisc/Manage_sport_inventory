from datetime import datetime as dt
import os
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from forms.news import AsortimentForm, RequestForm, IdtypeForm
from forms.user import RegisterForm, LoginForm, EU, IU, PurchasePlanForm
from data.news import Asortiment, Request, PurchasePlan
from data.category import Idtype
from data.users import Users
from sqlalchemy import create_engine
from data import db_session

UPLOAD_FOLDER = 'static/images'
sqlite_database = "sqlite:///blogs.db"
engine = create_engine(sqlite_database, echo=True)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'mysecurytiname'
login_manager.login_view = 'login'


def Check_free(date_start, date_end, id):
    date_start = str(date_start)
    date_end = str(date_end)
    db_sess = db_session.create_session()
    dates = db_sess.query(Request).filter(Request.id_item == id).all()
    if dates:
        for p in dates:
            if date_start >= p.date_start and date_start <= p.date_end and date_end <= p.date_end and date_end >= p.date_start:
                return False
            if date_start <= p.date_start and date_start <= p.date_end and date_end <= p.date_end and date_end >= p.date_start:
                return False
            if date_start >= p.date_start and date_start <= p.date_end and date_end >= p.date_end and date_end >= p.date_start:
                return False
    if date_start > date_end:
        return False
    return True


def check_out(db_sess):
    requests = db_sess.query(Request).all()
    date = str(dt.today()).split()[0]
    
    for request in requests:
        print("somne", request.approved, date, request.date_start, request.id)
        if (request.approved == False or request.approved == None) and date >= request.date_start:

            db_sess.delete(request)
        elif request.approved == True and date >= request.date_start:
            if request.approved == True and date >= request.date_end:
                if "Завершён" != request.type:
                    db_sess.query(Request).filter_by(id=request.id).update({'type': "Завершён"})
            else:
                db_sess.query(Request).filter_by(id=request.id).update({'type': "Идёт"})
    db_sess.commit()
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


@app.route('/Unconfirm_request/<int:id_request>', methods=['GET', 'POST'])
@login_required
def Unconfirm_request(id_request):
    if current_user.user_access == "baned":
        abort(404)
    else:
        db_sess = db_session.create_session()
        reques = db_sess.query(Request).filter(Request.id == id_request).first()
        if reques:
            db_sess.delete(reques)
            db_sess.commit()
            update_requests(db_sess)
        else:
            abort(404)
        return redirect('/arrended')


@app.route("/report_request/<int:id_request>", methods=['GET', 'POST'])
@login_required
def report_request(id_request):
    if current_user.user_access == "baned":
        abort(404)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
        form = RequestForm()
        db_sess = db_session.create_session()
        request = db_sess.query(Request).filter_by(id=id_request).first()
        if form.validate_on_submit():
            db_sess.query(Request).filter_by(id=id_request).update({'description': form.description.data,})
            db_sess.commit()
            print("soem")
            return redirect("/admin_panel")
        return render_template("reportR.html", form=form, request=request, title="Отзыв о аренде")


@app.route('/delete_item/<int:id_item>', methods=['GET', 'POST'])
@login_required
def delete_item(id_item):
    if current_user.user_access == "baned":
        abort(404)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
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
    if current_user.user_access == "baned":
        abort(404)
    else:
        db_sess = db_session.create_session()
        item = db_sess.query(Asortiment).filter_by(id=id_item).first()
        form = RequestForm()
        if form.validate_on_submit():
            if Check_free(form.datetime_start.data, form.datetime_end.data, id_item) == True:
                request = Request(id_item=id_item,
                                id_user=current_user.id,
                                user=db_sess.query(Users).filter_by(id=current_user.id).one(),
                                date_start=str(form.datetime_start.data),
                                date_end=str(form.datetime_end.data),
                                description=form.description.data,
                                type="Не одобрен"
                                )
                db_sess.add(request)
                db_sess.commit()
                return redirect("/")
            else:
                return render_template("request.html",
                                    form=form,
                                    item=item,
                                    message="Товар занят в указаное вами время или вы указали неверно промежуток!",
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
        check_out(db_sess)
        if current_user.is_authenticated:
            if current_user.user_access == "baned":
                abort(404)
            else:
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
    if current_user.user_access == "baned":
        abort(403)
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
    if current_user.user_access == "baned":
        abort(404)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
        db_sess = db_session.create_session()
        if current_user.user_access == "admin":
            items = db_sess.query(Asortiment).all()
            requests = db_sess.query(Request).all()
            users = db_sess.query(Users).all()
            types = db_sess.query(Idtype).all()
            for request in requests:
                print(request.approved, request.type)
                print(request.approved == False and request.type != "Идёт", request.type != "Идёт", request.type == "Завершён", request.type == "")
            return render_template("admin_panel.html", 
                                items=items, 
                                requests=requests, 
                                types=types, 
                                users=users, 
                                title="Управление сайтом"
                                )
        else:
            return redirect("/")


@app.route('/purchase_plan', methods=['GET', 'POST'])
@login_required
def purchase_plan():
    if current_user.user_access != "admin":
        abort(403)

    db_sess = db_session.create_session()
    plan_items = db_sess.query(PurchasePlan).all()
    form = PurchasePlanForm()
    assortiments = db_sess.query(Asortiment).all()
    form.asortiment_id.choices = [(0, "Нет в ассортименте")] + [(a.id, a.name) for a in assortiments]
    if form.validate_on_submit():
        if form.asortiment_id.data == 0:
            if not form.item_name.data:
                return render_template('purchase_plan.html',
                                       title='План закупок',
                                       form=form, 
                                       plan_items=plan_items,
                                       message="Укажите название товара"
                                       )
            new_plan_item = PurchasePlan(item_name = form.item_name.data,
                                         quantity=form.quantity.data,
                                         price=form.price.data,
                                         supplier=form.supplier.data
                                         )
        else:
            asortiment = db_sess.query(Asortiment).get(form.asortiment_id.data)
            if not asortiment:
                abort(404)
            new_plan_item = PurchasePlan(asortiment_id=asortiment.id,
                                         quantity=form.quantity.data,
                                         price=form.price.data,
                                         supplier=form.supplier.data
                                         )
            
        db_sess.add(new_plan_item)
        db_sess.commit()
        return redirect('/purchase_plan')

    return render_template('purchase_plan.html', title='План закупок', form=form, plan_items=plan_items)


@app.route('/purchase_plan/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def purchase_plan_delete(id):
    if current_user.user_access != "admin":
        abort(403)

    db_sess = db_session.create_session()
    plan_item = db_sess.query(PurchasePlan).get(id)
    if not plan_item:
        abort(404)

    db_sess.delete(plan_item)
    db_sess.commit()
    return redirect('/purchase_plan')


@app.route('/purchase_plan/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def purchase_plan_edit(id):
     if current_user.user_access != "admin":
        abort(403)
     
     db_sess = db_session.create_session()
     plan_item = db_sess.query(PurchasePlan).get(id)

     if not plan_item:
        abort(404)
     
     form = PurchasePlanForm()

     assortiments = db_sess.query(Asortiment).all()
     form.asortiment_id.choices = [(0, "Нет в ассортименте")] + [(a.id, a.name) for a in assortiments]

     if form.validate_on_submit():
        if form.asortiment_id.data == 0:
            if not form.item_name.data:
                 return render_template('purchase_plan_edit.html', 
                                        title='Редактирование плана закупок',
                                        form=form,  
                                        plan_item=plan_item,
                                        message="Укажите название товара"
                                        )
            plan_item.item_name = form.item_name.data
            plan_item.asortiment_id = None
                
        else:
            plan_item.asortiment_id = form.asortiment_id.data
            plan_item.item_name = None
        
        plan_item.quantity = form.quantity.data
        plan_item.price = form.price.data
        plan_item.supplier = form.supplier.data

        db_sess.commit()
        return redirect('/purchase_plan')

     if request.method == "GET":

        if plan_item.asortiment:
             form.asortiment_id.data = plan_item.asortiment_id
        else:
             form.item_name.data = plan_item.item_name
             form.asortiment_id.data = 0

        form.quantity.data = plan_item.quantity
        form.price.data = plan_item.price
        form.supplier.data = plan_item.supplier
    
     return render_template('purchase_plan_edit.html', 
                            title='Редактирование плана закупок', 
                            form=form, 
                            plan_item=plan_item
                            )


@app.route("/edit_item/<int:id_item>", methods=["GET", "POST"])
@login_required
def edit_item(id_item):
    if current_user.user_access == "baned":
        abort(403)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
        db_sess = db_session.create_session()
        form = IU()
        if form.validate_on_submit():
            db_sess.query(Asortiment).filter(Asortiment.id == id_item).update({'name': form.name.data, 'status': form.status.data})
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
    if current_user.user_access == "baned":
        abort(403)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
        form = AsortimentForm()
        db_sess = db_session.create_session()
        types = db_sess.query(Idtype.name).all()
        choices = [[types[i][0], types[i][0]] for i in range(len(types))] 
        form.type.choices = choices
        if form.validate_on_submit():
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
    if current_user.user_access == "baned":
        abort(403)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
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
    if current_user.user_access == "baned":
        abort(403)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter_by(id=id_user).first()  
        form = EU()
        if form.validate_on_submit():
            db_sess.query(Users).filter_by(id=id_user).update({'user_access': form.access.data,
                                                            'about': form.status.data}, 
                                                            )
            db_sess.commit()
            return redirect("/admin_panel")
        form.status.data = user.about
        return render_template("edit_user.html", 
                            form=form, 
                            user=user, 
                            title="Изменение пользователя")


@app.route("/confirm_request/<int:id_request>", methods=["GET", "POST"])
@login_required
def confirm_request(id_request):
    if current_user.user_access == "baned":
        abort(403)
    elif current_user.user_access == "User":
        return redirect("/")
    else:
        form = RequestForm()
        db_sess = db_session.create_session()
        if form.validate_on_submit():
            if form.confirmed.data == True:
                db_sess.query(Request).filter_by(id=id_request).update({'description': form.description.data,
                                                                    'approved': form.confirmed.data,
                                                                    'type': 'Одобрен'}
                                                                    )
            else:
                db_sess.query(Request).filter_by(id=id_request).update({'description': form.description.data,
                                                                    'approved': form.confirmed.data,
                                                                    'type': 'Не одобрен'}
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
