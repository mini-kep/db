from datetime import datetime
from sqlalchemy import desc
from db.api.models import Datapoint
from db.api.errors import CustomError400


def to_date(date_str: str):
    """Convert YYYY-MM-DD *date_str* to datetime.date object.
       Raises error if *date_str* not in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise CustomError400(f'Invalid date parameter {date_str}')


def yield_csv_row(dicts):
    """Serialiser function to create CSV rows as strings.

    Arg:
       dicts - list of dictionaries like
               {'date': '1992-07-01', 'freq': 'd',
                'name': 'USDRUR_CB', 'value': 0.1253}

    Yeilds:
        csv header like ',USDRUR_CB'
        followed by rows like '1992-07-01,0.1253'
        followed by empty string at end
    """
    datapoints = list(dicts)
    name = datapoints[0]['name']
    yield ',{}'.format(name)
    for d in datapoints:
        yield '{},{}'.format(d['date'], d['value'])
    # this yield is responsible for last \n in csv
    yield ''


def to_csv(dicts):
    if dicts:
        rows = list(yield_csv_row(dicts))
        return '\n'.join(rows)
    else:
        return ''


class DatapointParameters:
    
    def __init__(self, args):
        self.args = args
        self.name = self.get_name() 
        if not self.name: 
            raise CustomError400("<name> parameter is required")
        self.freq = self.get_freq() 
        if not self.freq: 
            raise CustomError400("<freq> parameter is required")
        
    def get_freq(self): 
        freq = self.args.get('freq')  
        self.validate_freq_exist(freq)
        return freq
       
    def get_name(self):
        freq = self.get_freq()
        name = self.args.get('name')  
        self.validate_name_exist_for_given_freq(freq, name)
        return name
    
    def get_start(self):
        start_dt = self.get_dt('start_date')  
        if start_dt:
            self.validate_start_is_not_in_future(start_dt)
        return start_dt     
    
    def get_end(self):
        end_dt = self.get_dt('end_date')
        start_dt = self.get_start()
        if start_dt:
            self.validate_end_date_after_start_date(start_dt, end_dt)
        return end_dt     
    
    def get_dt(self, key: str):
        dt = None
        date_str = self.args.get(key)  
        if date_str:
            dt = to_date(date_str)
        return dt     

    def get(self):
        return dict(name=self.name,
                    freq=self.freq,
                    start_date=self.get_start(),
                    end_date=self.get_end()
                    )

    @staticmethod
    def validate_freq_exist(freq):
        allowed = list(select_unique_frequencies()) 
        if freq not in allowed:
            raise CustomError400(message='Invalid frequency <{freq}>',
                                 payload={'allowed': allowed})
    
    @staticmethod
    def validate_name_exist_for_given_freq(freq, name):
        possible_names_values = Datapoint.query.filter(Datapoint.freq == freq) \
            .group_by(Datapoint.name) \
            .values(Datapoint.name)
        # EP: redefining same variable is a bit questionable
        possible_names_values = [row.name for row in possible_names_values]
        if name not in possible_names_values:
            msg = f'No such name <{name}> for <{freq}> frequency.'
            raise CustomError400(message=msg,
                                 payload={"allowed": possible_names_values})
    
    @staticmethod
    def validate_start_is_not_in_future(start_date):
        current_time = datetime.date(datetime.utcnow())
        if start_date >= current_time:
            raise CustomError400('Start date cannot be in the future')
    
    @staticmethod
    def validate_end_date_after_start_date(start_date, end_date):
        if end_date < start_date:
            raise CustomError400('End date must be after start date')          
            

def select_unique_frequencies():
    query = Datapoint.query.group_by(Datapoint.freq) \
                           .values(Datapoint.freq)
    return [row.freq for row in query]

def get_first_and_last_date(freq, name):
    # Extract first and last dates from datapoints with given freq, names
    start_date = Datapoint.query. \
        filter(Datapoint.name == name). \
        filter(Datapoint.freq == freq). \
        order_by(Datapoint.date). \
        first()
    start_date = datetime.strftime(start_date.date, "%Y-%m-%d")
    end_date = Datapoint.query. \
        filter(Datapoint.name == name). \
        filter(Datapoint.freq == freq). \
        order_by(desc(Datapoint.date)). \
        first()
    end_date = datetime.strftime(end_date.date, "%Y-%m-%d")
    return start_date, end_date


if __name__ == '__main__':
    from db import create_app
    from db.api.views import api 

    # create test app
    app = create_app('config.DevelopmentConfig') 
    app.register_blueprint(api)
    
    #EP: works without db creation after done once
    #from db import db
    #db.create_all(app=create_app('config.DevelopmentConfig'))

    with app.app_context():
       
        z = [d.value for d in Datapoint.query.filter(Datapoint.freq == 'd').all()]

        query = Datapoint.query.filter(Datapoint.freq == 'd') \
                               .group_by(Datapoint.name) \
                               .values(Datapoint.name)
        k = [x.name for x in query]    
        assert k == ['BRENT', 'USDRUR_CB']
        assert set(['a', 'd', 'm', 'q']) == set(select_unique_frequencies())
        
