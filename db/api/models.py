from datetime import datetime
from db import db
from db.api.errors import Custom_error_code_400
import utils
from utils import to_date, to_csv


class Datapoint(db.Model):
    __table_args__ = (
        db.UniqueConstraint("name", "freq", "date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    freq = db.Column(db.String, nullable=False)    
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    
    @property
    def serialized(self): # Add serialize method for jsonify
       return {
           'freq': self.freq,
           'name': self.name,
           'date': datetime.strftime(self.date, "%Y-%m-%d"),
           'value':self.value
       }

    @staticmethod
    def process_query(freq, name, start_date_str, end_date_str):
        # Validate freq
        utils.validate_freq_exist(freq)
        # Validate name exist for given freq
        utils.validate_name_exist_for_given_freq(freq, name)
        # Filter by necessary parameters
        data = Datapoint.query.filter_by(name=name, freq=freq).order_by(Datapoint.date)
        # init start and end_dates
        start_date, end_date = None, None
        # process start date
        if start_date_str:
            start_date = to_date(start_date_str)
            utils.validate_start_is_not_in_future(start_date)
            data = data.filter(Datapoint.date >= start_date)
        # process end date
        if end_date_str:
            end_date = to_date(end_date_str)
            if start_date:
                utils.validate_end_date_after_start_date(start_date, end_date)
            data = data.filter(Datapoint.date <= end_date)
        return data
