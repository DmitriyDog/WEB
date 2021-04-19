import sqlalchemy

from .db_session import SqlAlchemyBase


class Entertain(SqlAlchemyBase):
    __tablename__ = 'entertain'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    rate = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
