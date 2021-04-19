from flask import Flask, render_template, redirect, url_for
from loginform import LoginForm, RegisterForm
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Very_Very_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/libs.db")


@app.route('/')
def home_page():
    return render_template('home_page.html', title='Добро пожаловать!')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/profile")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/profile')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/entertain/<tp>/')
def films(tp):
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
    return render_template('entertain.html', data=data, data_n=data_n, number=number, length=length, image=image,
                           title_h=title_h, tp=tp)


@app.route('/entertain/<tp>/<name>/')
def find_page(tp, name):
    if tp != "films" and tp != "books" and tp != "TV-series":
        return redirect('/')
    with open('db/entertain.json', encoding='utf-8') as f:
        data = json.load(f)
    for i in data[f"{tp}"].keys():
        if i == name:
            return render_template('info_page.html', data=data[f"{tp}"][name], name=name)


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
