from datetime import datetime
from db import db


class Datapoint(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    freq = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    value =db.Column(db.Float, nullable=False)

    @property
    def serialize(self): # Add serialize method for jsonify
       return {
           'freq': self.freq,
           'name': self.name,
           'date': datetime.strftime(self.date, "%Y-%m-%d"),
           'value':self.value
       }
