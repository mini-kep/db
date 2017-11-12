from datetime import datetime

import flask 
from webargs.flaskparser import parser
from webargs import fields, ValidationError

from db.api.queries import Allowed, All


class ArgError(ValidationError):
    """Custom class for errors when user arguments do not pass validation.
       Uses error *message* and *load* dictionary to describe error.
       
       In a slighlty covered way 'webargs' will create will an 
       UnprocessableEntity instance after 'raise ValidationError' or
       'raise ArgError(...)'. 
       
       The exception itself will be an '.exc' attribute of UnprocessableEntity. 
       This is important for views.py @api.errorhandler().

       Status code 422 is default for 'webargs.ValidationError'

       Again, in a very opaque way one can learn that for the pruposes 
       of testing UnprocessableEntity raises 
       'werkzeug.exceptions import HTTPException'. How would we had to guess?
       
    """ 
    def __init__(self, message, load):
        super().__init__(message, status_code = 422, load=load)

class Check:    
    """
    """
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
                load = dict(start_date=self.start_date, 
                            current_date=current_date)
                raise ArgError('Start date cannot be in future', load)
                
    def end_date_after_start_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                load = dict(start_date=self.start_date, end_date=self.end_date)
                raise ArgError('End date must be after start date', load) 

    def freq_exist(self):
        all_freq = All.frequencies()
        if self.freq not in all_freq:
            load = dict(freq=self.freq, allowed=all_freq)
            raise ArgError('Invalid frequency', load)
    
    def _name_exists(self, name):
        possible_names = Allowed.names(self.freq)
        if name not in possible_names:
            load = dict(name=name, freq=self.freq, allowed=possible_names) 
            raise ArgError('Name does not exist for this frequency)',
                           load)
                           
    # NOTE: this will reveal errors one at a time, 
    #       not all list of wrong names
    def names_are_valid(self):
        if self.names:
            names = self.names.split(',')
            for name in names:
                self._name_exists(name)

    def name_is_valid(self):
        self._name_exists(self.name)

def get_func(func_name):
    return lambda args: getattr(Check(args), func_name)()  

def make_func_list(func_names):
    return [get_func(func_name) for func_name in func_names]
    
DATAPOINT_ARGS = {
    'freq': fields.Str(required=True),
    'name': fields.Str(required=True),
    'start_date': fields.Date(required=False),
    'end_date': fields.Date(required=False),
    'format': fields.Str(missing='csv'),                      
}

DATAPOINT_VALIDATION_FUNCTIONS = make_func_list(
                      ['start_is_not_in_future', 
                       'end_date_after_start_date',
                       'freq_exist',
                       'name_is_valid'])

class RequestArgs:    

    schema = DATAPOINT_ARGS
    validate_with = DATAPOINT_VALIDATION_FUNCTIONS
    query_keys = ['name', 'freq', 'start_date', 'end_date']
        
    def __init__(self, request = flask.request):        
        self._args = parser.parse(self.schema, 
                                  req=request, 
                                  validate=self.validate_with)
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


FRAME_VALIDATION_FUNCTIONS = make_func_list(
                      ['start_is_not_in_future', 
                       'end_date_after_start_date',
                       'freq_exist',
                       'names_are_valid'])

    
class RequestFrameArgs(RequestArgs):    

    schema = DATAFRAME_ARGS
    validate_with = FRAME_VALIDATION_FUNCTIONS
    query_keys = ['names', 'freq', 'start_date', 'end_date']    

    def __init__(self, request = flask.request):        
        self._args = parser.parse(self.schema, 
                                  req=request, 
                                  validate=self.validate_with)
        names = self._args.get('names')
        if names:
             self._args['names'] = names.split(',')


if __name__ == "__main__":
    msg_str = 'Start date cannot be in future'
    load_dict = dict(start_date=123, today=456)
    z = ArgError(message = msg_str, load = load_dict)
    assert z.kwargs['load']
 
    # this was moved to test_parameters.py  
    class SimRequest:  
        mimetype = None
        json = None        
        
        def __init__(self, **kwargs):
            self._dict = kwargs
        
        @property
        def args(self):     
            return self._dict 
            
      
    import arrow
    ins = dict(name="GDP_yoy", freq='a')
    req = SimRequest(**ins)   
    args = RequestArgs(req)
    assert args.name == 'GDP_yoy'
    assert args.freq == 'a'
    assert args.start_date is None
    assert args.end_date is None
    assert args.format == 'csv'
        
    incoming_args = dict(name='BRENT', 
                         freq='d', 
                         start_date='2017-01-01', 
                         end_date='2017-02-28') 
    req = SimRequest(**incoming_args)   
    args = RequestArgs(req)
    assert args.freq == 'd'
    assert args.name == 'BRENT'
    assert args.start_date == arrow.get(2017, 1, 1).date()
    assert args.end_date == arrow.get(2017, 2, 28).date() 
    assert args.query_param


    import pytest
    from werkzeug.exceptions import HTTPException
    malformed_args = dict(name='BRENT') 
    req = SimRequest(**malformed_args)
    with pytest.raises(HTTPException):
        args = RequestArgs(req)
        
    incoming_args = dict(names="GDP_yoy,CPI_rog", freq='a')
    req = SimRequest(**incoming_args)   
    args = RequestFrameArgs(req)  
    
    
    
    