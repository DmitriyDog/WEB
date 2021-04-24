from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class Rate(FlaskForm):
    rating = SelectField('Выберите оценку',
                         choices=[(None, 'Не завершено'), (10, 'Шедевр(10)'), (9, 'Великолепно(9)'),
                                  (8, 'Очень хорошо(8)'), (7, 'Хорошо(7)'),
                                  (6, 'Неплохо(6)'), (5, 'Нормально(5)'),
                                  (4, 'Не очень(4)'), (3, 'Плохо(3)'),
                                  (2, 'Ужасно(2)'), (1, 'Отвратительно(1)')])
    submit = SubmitField('Подтвердить выбор')
