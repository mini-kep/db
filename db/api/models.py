from datetime import datetime
from db import db


class Datapoint(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    # COMMENT (EP): for id we had a lot of properties, not sure about all, but we are liekly to need 'autoincrement=True'  
    
    #    id = Column(Integer, nullable=False, 
    #                     unique=True, 
    #                     autoincrement=True, 
    #                      primary_key=True) 
    
    freq = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    value =db.Column(db.Float, nullable=False)

    # COMMENT (EP): I think we will need a <freq-name-date> composite key in order to work with existing vs new values in the database 
    # from https://github.com/mini-kep/db/blob/master/demo/sqlalchemy/datapoint.py#L10-L12 :
    #    __table_args__ = (
    #             UniqueConstraint("freq", "name", "date"),
    #              )
    
    @property
    def serialize(self): # Add serialize method for jsonify
       return {
           'freq': self.freq,
           'name': self.name,
           'date': datetime.strftime(self.date, "%Y-%m-%d"),
           'value':self.value
       }   
    
