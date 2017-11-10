from datetime import datetime
from db.api.errors import CustomError400
import db.api.queries as queries


def custom_error(msg, allowed=None):
    param = dict(message=msg) 
    if allowed:
        param['payload']= dict(allowed = allowed)
    raise CustomError400(**param)
    
    
def to_date(date_str: str, error=custom_error):
    """Convert YYYY-MM-DD *date_str* to datetime.date object.
       Raises error if *date_str* not in YYYY-MM-DD format.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        error(f'Invalid date parameter {date_str}')


def date_as_str(dt):
    """Convert datetime.date object *dt* to YYYY-MM-DD string."""
    return datetime.strftime(dt.date, "%Y-%m-%d")


class Validator:
    """Collection of validation fucntions."""
    
    def freq_exist(freq):
        allowed = list(queries.select_unique_frequencies())
        if freq not in allowed:
            custom_error(f'Invalid frequency <{freq}>', allowed)
    
    def name_exist_for_given_freq(freq, name):
        possible_names = queries.possible_names_values(freq)
        if name not in possible_names:
            msg = f'No such name <{name}> for <{freq}> frequency.'
            custom_error(msg, possible_names)
    
    def start_is_not_in_future(start_date):
        current_date = datetime.date(datetime.utcnow())
        if start_date > current_date:
            custom_error('Start date cannot be in future')
        
    def end_date_after_start_date(start_date, end_date):
        if end_date < start_date:
            custom_error('End date must be after start date')          


class DummyValidator:
    def freq_exist(freq):
        pass
    
    def name_exist_for_given_freq(freq, name):
        pass

    def start_is_not_in_future(start_date):
        pass
        
    def end_date_after_start_date(start_date, end_date):
        pass


class DateRange:
    """Apparently not used here, but keep it."""
    
    def __init__(self, freq, name):
        self.freq, self.name = freq, name
        
    def _get_boundary(self, direction):
        query = queries.get_boundary_date(self.freq, self.name, direction)
        return date_as_str(query)       
    
    def min(self):
        return self._get_boundary(direction='start')

    def max(self):
        return self._get_boundary(direction='end')


class DatapointArgs:
    """Parameter handler for api\datapoints endpoint."""    
    def __init__(self, args, validator_cls=Validator, error_func=custom_error):
        self.args = args
        self.validator = validator_cls
        self.error = error_func
        
    @property        
    def freq(self): 
        freq = self.args.get('freq')  
        if freq:
            self.validator.freq_exist(freq)
            return freq
        else:
            self.error('<freq> parameter is required')
       
    @property    
    def name(self):
        name = self.args.get('name')  
        if name:
            self.validator.name_exist_for_given_freq(self.freq, name)
            return name
        else:
            self.error('<name> parameter is required')                
        

    def get_dt(self, key: str):
        """Extract date from *self.arg* by key like *start_date*, *end_date*."""
        dt = None
        date_str = self.args.get(key)  
        if date_str:
            dt = to_date(date_str)
        return dt

    @property
    def start(self):
        start = self.get_dt('start_date')  
        if start:
            self.validator.start_is_not_in_future(start)
        return start     
    
    @property
    def end(self):
        end = self.get_dt('end_date')
        if self.start and end:
            self.validator.end_date_after_start_date(self.start, end)
        return end     

    @property
    def format(self):
        #TODO
        pass

    @property
    def dict(self):
        """Return query parameters as dictionary."""
        return dict(name=self.name,
                    freq=self.freq,
                    start_date=self.start,
                    end_date=self.end)

# todo: convert to test
incoming_args = dict(name='BRENT', freq='d', start_date='2017-01-01') 
args = DatapointArgs(incoming_args, DummyValidator)
assert args.freq == 'd'
assert args.name == 'BRENT'
assert args.start == to_date('2017-01-01')
assert args.end is None
