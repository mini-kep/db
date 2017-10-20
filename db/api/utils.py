from datetime import datetime
from db.api.models import Datapoint
from db.api.errors import CustomError400
import db.api.queries as queries


def to_date(date_str: str):
    """Convert YYYY-MM-DD *date_str* to datetime.date object.
       Raises error if *date_str* not in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise CustomError400(f'Invalid date parameter {date_str}')

def date_as_str(dt):
    """Convert datetime.date object *dt* to YYYY-MM-DD string."""
    return datetime.strftime(dt.date, "%Y-%m-%d")

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
    """Wrapper for yield_csv_row()"""
    if dicts:
        rows = list(yield_csv_row(dicts))
        return '\n'.join(rows)
    else:
        return ''


class DatapointParameters:
    """Parameter handler for api\datapoints endpoint."""    
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
    
    def _get_boundary(self, direction):
        query = queries.get_boundary_date(self.freq, self.name, direction)
        return date_as_str(query)       
    
    def get_min_date(self):
        return self._get_boundary(direction='start')

    def get_max_date(self):
        return self._get_boundary(direction='end')
    
    def get(self):
        """Return query parameters as dictionary."""
        return dict(name=self.name,
                    freq=self.freq,
                    start_date=self.get_start(),
                    end_date=self.get_end())

    @staticmethod
    def validate_freq_exist(freq):
        allowed = list(queries.select_unique_frequencies())
        if freq in allowed:
            return True
        else:     
            raise CustomError400(message='Invalid frequency <{freq}>',
                                 payload={'allowed': allowed})
    
    @staticmethod
    def validate_name_exist_for_given_freq(freq, name):
        possible_names = queries.possible_names_values(freq)
        if name in possible_names:
            return True
        else:
            msg = f'No such name <{name}> for <{freq}> frequency.'
            raise CustomError400(message=msg,
                                 payload={"allowed": possible_names})
    
    @staticmethod
    def validate_start_is_not_in_future(start_date):
        current_date = datetime.date(datetime.utcnow())
        #TODO: test on date = today must pass
        if start_date > current_date:
            raise CustomError400('Start date cannot be in future')
        else:
            return True            
    
    @staticmethod
    def validate_end_date_after_start_date(start_date, end_date):
        if end_date < start_date:
            raise CustomError400('End date must be after start date')          
        else:
            return True


if __name__ == '__main__': # pragma: no cover
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
        assert set(['a', 'd', 'm', 'q']) == \
               set(queries.select_unique_frequencies())
        
