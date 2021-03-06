from flask import Flask, render_template, redirect, url_for, request
from loginform import LoginForm, RegisterForm
from data import db_session
from data.users import User
from data.object_ent import Entertain
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import json
from Rate import Rate
import os

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
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
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
    films_user = []
    books_user = []
    tv_series_user = []
    films_rates = []
    books_rates = []
    tv_rates = []
    db_sess = db_session.create_session()
    db_sess.commit()
    for i in current_user.related:
        if i.type == 'films':
            films_user.append(i)
            for j in i.critics.split():
                if str(current_user.id) == j.split('-')[0]:
                    films_rates.append(j.split('-')[1])  # можно не добавлять
                    # break так как пользователь ставит только одну оценку на блок
    for i in current_user.related:
        if i.type == 'books':
            books_user.append(i)
            for j in i.critics.split():
                if str(current_user.id) == j.split('-')[0]:
                    books_rates.append(j.split('-')[1])
    for i in current_user.related:
        if i.type == 'TV series':
            tv_series_user.append(i)
            for j in i.critics.split():
                if str(current_user.id) == j.split('-')[0]:
                    tv_rates.append(j.split('-')[1])
    date = str(current_user.created_date)[:10]
    length_b = len(books_user)
    length_t = len(tv_series_user)
    length_f = len(films_user)
    return render_template('profile.html', title=current_user.name, films=films_user, books=books_user,
                           TV_series=tv_series_user, films_rates=films_rates, tv_rates=tv_rates,
                           books_rates=books_rates, length_f=length_f, length_b=length_b, length_t=length_t,
                           date=date)


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
                user = db_sess.query(User).filter(User.id == current_user.id).first()
                if form.rating.data != 'None':
                    now.rate = now.rate + float(form.rating.data)
                    for j in list_crit:
                        if str(current_user.id) == j.split('-')[0]:
                            now.rate -= float(j.split('-')[1])
                            list_crit.remove(j)
                            now.count = now.count - 1
                            user.related.remove(now)
                    user.related.append(now)
                    list_crit.append(f'{current_user.id}-{form.rating.data}')
                    now.count = now.count + 1
                elif form.rating.data == 'None':
                    for j in list_crit:
                        if str(current_user.id) == j.split('-')[0]:
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


@app.route('/redact', methods=['GET', 'POST'])
@login_required
def redact():
    if request.method == 'POST':
        name = request.form['name']
        about = request.form['about']
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if ''.join(name.split()) != '':
            user.name = name
        user.about = about
        db_sess.commit()
        return redirect('/profile')
    return render_template('redact.html', title='Изменение профиля')


if __name__ == '__main__':
    main()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
