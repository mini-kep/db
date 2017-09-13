# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Float, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Datapoint(Base):

    __tablename__ = 'datapoints'

    id = Column(Integer, nullable=False, 
                         unique=True, 
                         autoincrement=True, 
                         primary_key=True)    
    freq = Column(String, nullable=False)
    name = Column(String, nullable=False)
    
    # FIXME: maybe date column should have Date type? 
    #        how the conversion is made?
    #        is it ok to for incoming json to be YYYY-MM-DD string?
    date = Column(String, nullable=False)
    # end
    
    value = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("freq", "name", "date"),
    )

    def __repr__(self):        
        args = (('freq', self.freq), 
                ('name', self.name),
                ('date', self.date), 
                ('value', self.value))
        args_str = [f'{k}={v}' for k, v in args] 
        return "Datapoint({})".format(", ".join(args_str ))
    
# NOT TODO: there can be a second table with additional information 
#          (parser name, timestamp, inserted)

if __name__=='__main__':
    d = Datapoint(freq='m', name='BRENT', date='2017-09-20', value=50.25)
    assert isinstance(d.freq, str)
    assert isinstance(d.name, str)
    assert isinstance(d.value, float)
    # likely fails
    assert isinstance(d.date, str)    
    