from flask import Flask, render_template, redirect, jsonify
from loginform import LoginForm, RegisterForm
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Very_Very_secret_key'


def main():
    db_session.global_init("db/libs.db")
    user = User()
    user.name = "Пользователь 1"
    user.about = "биография пользователя 1"
    user.email = "email@email.ru"
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()
    app.run()


@app.route('/')
def home_page():
    return render_template('home_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/profile')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect('/profile')
    return render_template('register.html', title='Регистрация', form=form)


#@app.route('/profile')
#@login.required
#def profile():
    #return render_template('profile.html')


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
