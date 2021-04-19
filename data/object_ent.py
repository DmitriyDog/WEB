import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

association_table = sqlalchemy.Table(
    'association',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('entertain', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('entertain.id'))
)


class Entertain(SqlAlchemyBase):
    __tablename__ = 'entertain'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    rate = sqlalchemy.Column(sqlalchemy.Float, nullable=False, default=0)
    count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
