import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Location(Base):
    __tablename__ = 'locations'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class Serie(Base):
    __tablename__ = 'series'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    code = sa.Column(sa.Integer)
    text = sa.Column(sa.String)


class Code(Base):
    __tablename__ = 'codes'

    id = sa.Column(sa.Integer, primary_key=True)
    location_id = sa.Column(sa.Integer, sa.ForeignKey(Location.id))
    serie_id = sa.Column(sa.Integer, sa.ForeignKey(Serie.id))
    code = sa.Column(sa.String, nullable=False)

    text = sa.Column(sa.String)
    last_update = sa.Column(sa.Integer)
    real_date = sa.Column(sa.Integer)

    location = relationship(Location)
    serie = relationship(Serie)


class Value(Base):
    __tablename__ = 'values'

    id = sa.Column(sa.Integer, primary_key=True)
    code_id = sa.Column(sa.String, sa.ForeignKey(Code.code))
    year = sa.Column(sa.Integer)
    period = sa.Column(sa.Integer)
    value = sa.Column(sa.Float)

    code = relationship(Code)


def createDB():
    engine = sa.create_engine('sqlite:///db.db', encoding='latin1', echo=False)
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine
