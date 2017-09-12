# -*- coding: utf-8 -*-

from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Datapoint(Base):
    __tablename__ = 'datapoints'

    # TODO: there may be some related table having additional information (source path, date of update, etc)
    id = Column(Integer, primary_key=True)
    freq = Column(String, nullable=False)
    name = Column(String, nullable=False)
    # TODO: maybe date column should have Date type?
    date = Column(String, nullable=False)
    value = Column(String, nullable=False)

    def __repr__(self):
        return "<Datapoint(id='%s', freq='%s', name='%s', date='%s', value='%s')>" % (
            self.id, self.freq, self.name, self.date, self.value)
