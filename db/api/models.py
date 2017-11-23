from datetime import datetime
from db import db


class Datapoint(db.Model):
    __table_args__ = (
        db.UniqueConstraint("name", "freq", "date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    freq = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    domain = db.Column(db.String, nullable=True) # should be changed later to nullable=False

    def __init__(self, name, freq, date, value, domain=None):
        self.name = name
        self.freq = freq
        self.date = datetime.strptime(date, "%Y-%m-%d").date()
        # actually, utils.to_date should be called
        # but if we import utils, we get import recursion
        self.value = value
        self.domain = domain

    @property
    def serialized(self):  # Add serialize method for jsonify
        return {
            'freq': self.freq,
            'name': self.name,
            'date': datetime.strftime(self.date, "%Y-%m-%d"),
            'value': self.value,
            'domain': self.domain
        }
