from flask import Flask, render_template, redirect, url_for, request
from loginform import LoginForm, RegisterForm
from data import db_session
from data.users import User
from data.object_ent import Entertain
from flask_login import LoginManager, login_user, login_required, logout_user
import json
from Rate import Rate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Very_Very_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
user_now = None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/libs.db")
    with open('db/entertain.json', encoding='utf-8') as f:
        data = json.load(f)
    for i in list(data.keys()):
        for j in list(data[i].keys()):
            db_sess = db_session.create_session()
            if not list(db_sess.query(Entertain).filter(Entertain.title == j)):
                ent = Entertain(
                    type=i,
                    title=j
                )
                db_sess.add(ent)
            db_sess.commit()


@app.route('/')
def home_page():
    return render_template('home_page.html', title='Добро пожаловать!')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_now
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            user_now = user
            login_user(user, remember=form.remember_me.data)
            return redirect("/profile")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global user_now
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user_now = user
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/profile')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    global user_now
    logout_user()
    user_now = None
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/entertain/<tp>/')
def category(tp):
    if tp != "films" and tp != "books" and tp != "TV-series":
        return redirect('/')
    if tp == "TV-series":
        tp = "TV series"
        title_h = "Сериалы"
    elif tp == "books":
        title_h = "Книги"
    else:
        title_h = "Фильмы"
    with open('db/entertain.json', encoding='utf-8') as f:
        data = json.load(f)
        data_n = sorted(data[tp])
        number = len(data_n) // 3
        length = len(data_n)
        image = []
        for i in range(length):
            image.append(url_for('static', filename=f'images/{data[tp][f"{data_n[i]}"]["Постер"]}'))
    if tp == "TV series":
        tp = "TV-series"
    return render_template('entertain.html', data=data, data_n=data_n, number=number, length=length, image=image,
                           title_h=title_h, tp=tp, title=title_h)


@app.route('/entertain/<tp>/<name>/', methods=['GET', 'POST'])
def find_page(tp, name):
    if tp != "films" and tp != "books" and tp != "TV-series":
        return redirect('/')
    if tp == "TV-series":
        tp = "TV series"
    with open('db/entertain.json', encoding='utf-8') as f:
        data = json.load(f)
    for i in data[f"{tp}"].keys():
        if i == name:
            form = Rate()
            image = url_for('static', filename=f'images/{data[f"{tp}"][name]["Постер"]}')
            length = len(data[f"{tp}"][name].keys()) - 1
            keys = list(data[f"{tp}"][name].keys())
            values = list(data[f"{tp}"][name].values())
            if request.method == 'POST':
                db_sess = db_session.create_session()
                now = db_sess.query(Entertain).filter(Entertain.title == i).first()
                list_crit = now.critics.split()
                user = db_sess.query(User).filter(User.id == user_now.id).first()
                if form.rating.data != 'None':
                    now.rate = now.rate + float(form.rating.data)
                    for j in list_crit:
                        if str(user_now.id) == j.split('-')[0]:
                            now.rate -= float(j.split('-')[1])
                            list_crit.remove(j)
                            now.count = now.count - 1
                            user.related.remove(now)
                    user.related.append(now)
                    list_crit.append(f'{user_now.id}-{form.rating.data}')
                    now.count = now.count + 1
                elif form.rating.data == 'None':
                    for j in list_crit:
                        if str(user_now.id) == j.split('-')[0]:
                            now.rate -= float(j.split('-')[1])
                            list_crit.remove(j)
                            now.count = now.count - 1
                            user.related.remove(now)
                now.critics = ' '.join(list_crit)
                db_sess.commit()
            db_sess = db_session.create_session()
            now = db_sess.query(Entertain).filter(Entertain.title == i).first()
            if now.count != 0:
                average = round(now.rate / now.count, 2)
            else:
                average = now.rate
            db_sess.commit()
            return render_template('info_page.html', data_keys=keys, data_values=values, name=name, image=image,
                                   length=length, form=form, title=i, average=average)


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
