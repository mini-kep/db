from app import db


class Datapoint(db.Model):
    __tablename__ = 'datapoints'

    id = db.Column(db.Integer, primary_key=True)
    freq = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=False)

    def __repr__(self):
        return "<Datapoint(id='%s', freq='%s', name='%s', date='%s', value='%s')>" % (
            self.id, self.freq, self.name, self.date, self.value)
