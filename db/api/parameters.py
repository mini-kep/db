from datetime import datetime

import flask
from flask import json
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
        super().__init__(message, status_code=422, load=load)


def convert_name_string_to_list(name_str):
    if not name_str:
        return []
    elif ',' in name_str:
        return name_str.split(',')
    else:    
        return [name_str]
    

class Check:
    """Collectin of argument validation functions."""

    def __init__(self, args):
        self.names = convert_name_string_to_list(args.get('name'))
        self.freq = args.get('freq')        
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

    def _name_exists(self, name, possible_names):
        if name not in possible_names:
            load = dict(name=name, freq=self.freq, allowed=possible_names)
            raise ArgError('Variable name does not exist in this frequency)',
                           load)
                    
    def names_validated(self):                
        possible_names = Allowed.names(self.freq)
        for name in self.names:
            self._name_exists(name, possible_names)

    def not_all_are_none(self):
        is_none = [
            (x is None) for x in [
                self.freq,
                self.names,
                self.start_date,
                self.end_date]]
        return not all(is_none)


def get_func(func_name):
    return lambda args: getattr(Check(args), func_name)()


def make_func_list(func_names):
    return [get_func(foo) for foo in func_names]


class RequestArgs:
    schema = {
        'freq': fields.Str(required=True),
        'name': fields.Str(required=True),
        'start_date': fields.Date(required=False),
        'end_date': fields.Date(required=False)
        }

    validate_with = make_func_list(
        ['start_is_not_in_future',
         'end_date_after_start_date',
         'freq_exist',
         'names_validated'])

    query_keys = ['name', 'freq', 'start_date', 'end_date']

    def __init__(self, request=flask.request):
        self.arg_dict = parser.parse(self.schema, req=request,
                                     validate=self.validate_with)
            
    def _make_dict(self, varnames):
        return {key: self.arg_dict.get(key) for key in varnames}           

    def get_query_parameters(self):
        return self._make_dict(self.query_keys)
   
    def __getattr__(self, x):
        return self.arg_dict.get(x)

class RequestFrameArgs(RequestArgs):
    schema = {
        'freq': fields.Str(required=True),
        'name': fields.Str(required=False),
        'start_date': fields.Date(required=False),
        'end_date': fields.Date(required=False)
        }

    validate_with = make_func_list([
        'start_is_not_in_future',
        'end_date_after_start_date',
        'freq_exist',
        'names_validated'
    ])

    query_keys = ['names', 'freq', 'start_date', 'end_date']


    def __init__(self, request=flask.request):
        super().__init__(request)
        # convert names
        name_str = self.arg_dict.get('name')
        names = convert_name_string_to_list(name_str)
        if not names:
            names = Allowed.names(self.freq)
        self.arg_dict['names'] = names


class SimplifiedArgs(RequestArgs):
    schema = {
        'freq': fields.Str(required=False),
        'name': fields.Str(required=False),
        'start_date': fields.Date(required=False),
        'end_date': fields.Date(required=False),
    }
    validate_with = make_func_list(['not_all_are_none'])
    query_keys = ['name', 'freq', 'start_date', 'end_date']


class DescriptionArgs:

    @staticmethod
    def process_json(response):
        data = response.get_data()
        if data:
            return json.loads(data.decode('utf-8'))

    @staticmethod
    def validate_abbr(abbr):
        load = {'abbr': abbr}
        if not abbr:
            raise ArgError('Error: abbr parameter should be given', load)

    @staticmethod
    def get_and_delete_params():
        # params should be like 'abbr=GDP'
        abbr = flask.request.args.get('abbr')
        return {
            'abbr': abbr
        }

    @staticmethod
    def post_params():
        """
        Payload should be like
        [
            dict(abbr='BRENT', ru='Цена нефти Brent', en='Brent oil price'),
            dict(abbr='GDP', ru='Валовый внутренний продукт', en='Gross domestic product'),
            dict(abbr='rog', ru='темп роста к пред. периоду', en='rate of growth to previous period'),
            dict(abbr='yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')
        ]
        """
        descriptions = DescriptionArgs.process_json(flask.request)
        if not descriptions:
            raise ArgError('Error: no data given.', descriptions)
        for description in descriptions:
            abbr = description.get('abbr')
            DescriptionArgs.validate_abbr(abbr)
            ru = description.get('ru')
            en = description.get('en')
            if not (ru or en):
                raise ArgError("Error: at least one of 'ru' or 'en' keys required.",
                               description)
            description['abbr'] = abbr
        return descriptions


if __name__ == "__main__":  # pragma: no cover

    msg_str = 'Start date cannot be in future'
    load_dict = dict(start_date=123, today=456)
    z = ArgError(message=msg_str, load=load_dict)
    assert z.kwargs['load']

    # code below was moved to test_parameters.py
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

    incoming_args = dict(name='BRENT',
                         freq='d',
                         start_date='2017-01-01',
                         end_date='2017-02-28')
    req = SimRequest(**incoming_args)
    args = RequestArgs(req)
    assert args.name == 'BRENT'
    assert args.freq == 'd'
    assert args.start_date == arrow.get(2017, 1, 1).date()
    assert args.end_date == arrow.get(2017, 2, 28).date()
    assert args.get_query_parameters()
    

    import pytest
    from werkzeug.exceptions import HTTPException
    malformed_args = dict(name='BRENT')
    req = SimRequest(**malformed_args)
    with pytest.raises(HTTPException):
        args = RequestArgs(req)

    incoming_args = dict(name="GDP_yoy,CPI_rog", freq='a')
    req = SimRequest(**incoming_args)
    args = RequestArgs(req)
    assert args.names == ['GDP_yoy', 'CPI_rog']
