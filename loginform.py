from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(LoginForm):
    password = PasswordField('Пароль',
                             validators=[DataRequired(), EqualTo('password_check', message='Passwords must match')])
    password_check = PasswordField('Повторите пароль', validators=[DataRequired()])
