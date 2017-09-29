from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Datapoint(Base):

    __tablename__ = 'datapoints'
    
    __table_args__ = (
        UniqueConstraint("freq", "name", "date"),
    )

    id = Column(Integer, nullable=False, 
                         unique=True, 
                         autoincrement=True, 
                         primary_key=True)    
    freq = Column(String, nullable=False)
    name = Column(String, nullable=False)
    
    # FIXME: maybe date column should have Date type? 
    #        how the conversion is made?
    #        is it ok for incoming json to be YYYY-MM-DD string?
    date = Column(String, nullable=False)
    # issue end ---------------------------------------
    
    value = Column(Float, nullable=False)    

    def __eq__(self, x):   
        return all([self.id == x.id, 
                    self.freq == x.freq,
                    self.name == x.name,                   
                    self.date == x.date,
                    self.value == x.value])

    def __repr__(self):   
        args = (('id', self.id),
                ('freq', quoted(self.freq)), 
                ('name', quoted(self.name)),
                ('date', quoted(self.date)), 
                ('value', self.value))
        args_str = [f"{k}={v}" for k, v in args] 
        return "Datapoint({})".format(", ".join(args_str ))
    
def quoted(s):
    s = str(s)
    return f"'{s}'" 


if __name__=='__main__':
    x = dict(freq='m', name='BRENT', date='2017-09-20', value=50.25)
    d = Datapoint(**x)
    # testing __e__q method
    assert d == d
    assert isinstance(d.freq, str)
    assert isinstance(d.name, str)
    assert isinstance(d.value, float)
    # likely fails after date type change
    assert isinstance(d.date, str) 
    # id not assigned before insert
    assert d.id is None