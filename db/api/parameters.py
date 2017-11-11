from datetime import datetime

import flask 
from webargs.flaskparser import parser
from webargs import fields, ValidationError
from db.api.queries import Allowed


class Check:    
    def __init__(self, args):
        self.freq = args['freq']
        self.name = args.get('name')
        self.names = args.get('names')
        self.start_date = args.get('start_date')
        self.end_date = args.get('end_date')                
        
    def start_is_not_in_future(self):
        if self.start_date: 
            current_date = datetime.date(datetime.utcnow())
            if self.start_date > current_date:
                raise ValidationError(f'Start date <start_date>'
                                       'cannot be in future')
    
    def end_date_after_start_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(f'End date <end_date> must be after '
                                      f'start date <start_date>')  

    def freq_exist(self):
        allowed = Allowed.frequencies()
        if self.freq not in allowed:
            raise ValidationError(f'Invalid frequency <{self.freq}>')
    
    def _name_exists(self, name):
        possible_names = Allowed.names(self.freq)
        if name not in possible_names:
            raise ValidationError(f'No such name <{name}> ' 
                                  f'for <{self.freq}> frequency.')
            
    # NOTE: this will reveal errors one at a time, not all list of wrong names
    def names_are_valid(self):
        if self.names:
            names = self.names.split(',')
            for name in names:
                self._name_exists(name)

    def name_is_valid(self):
        self._name_exists(self.name)



DATAPOINT_ARGS = {
    'freq': fields.Str(required=True),
    'name': fields.Str(required=True),
    'start_date': fields.Date(required=False),
    'end_date': fields.Date(required=False),
    'format': fields.Str(missing='csv'),                      
}



def get_func(fname):
    return lambda args: getattr(Check(args), fname)()  


class RequestArgs:    
    
    query_keys = ['name', 'freq', 'start_date', 'end_date']
    validate_func_names = ['start_is_not_in_future', 
                            'end_date_after_start_date',
                            'freq_exist',
                            'name_is_valid']
    schema = DATAPOINT_ARGS
        
    def __init__(self, request = flask.request):        
        self._args = parser.parse(self.schema, 
                                  req=request, 
                                  validate=self.validate_funcs)
    @property
    def validate_funcs(self):
        return [get_func(fn) for fn in self.validate_func_names]     
    
    @property
    def query_param(self): 
        return {key:self._args.get(key) for key in self.query_keys} 

    def __getattr__(self, x):
        return self._args.get(x)

        

DATAFRAME_ARGS = {
    'freq': fields.Str(required=True),
    'names': fields.Str(required=False),
    'start_date': fields.Date(required=False),
    'end_date': fields.Date(required=False),
}


class RequestFrameArgs(RequestArgs):    

    query_keys = ['names', 'freq', 'start_date', 'end_date']
    validate_func_names = ['start_is_not_in_future', 
                           'end_date_after_start_date',
                           'freq_exist',
                           'names_are_valid']
    schema = DATAFRAME_ARGS
    
    def __init__(self):
         super().__init__()
         names = self._args.get('names')
         if names:
             self._args['names'] = names.split(',')

    
## not todo: convert to test
#incoming_args = dict(name='BRENT', freq='d', start_date='2017-01-01') 
#args = RequestArgs(incoming_args)
#assert args.freq == 'd'
#assert args.name == 'BRENT'
#assert args.start == to_date('2017-01-01')
#assert args.end is None   

