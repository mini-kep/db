import pytest
import arrow

from tests.test_basic import TestCaseBase
from db.api.parameters import RequestArgs, RequestFrameArgs
from werkzeug.exceptions import HTTPException


def days_ahead(k):
    return arrow.utcnow().shift(days=k).format('YYYY-MM-DD')


BAD_ARGS_LIST = [
    # caught by argument inspection
    # parameters are required
    (None, None, None, None), (None, 'BRENT', None, None), ('q', None, None, None)    # date type
    # start and end date must be parsable
    # caught by parser validation functions
    , ('q', 'BRENT', 'today', 'tomorrow')    # args must be real variables
    # no such var at 'm' frequency
    , ('q', 'ZZZZ', None, None), ('m', 'BIBA_boba', None, None), ('z', 'BRENT', None, None), ('holdays', 'soon', None, None), ('m', 'GDP_yoy', None, None)    # !start after end
    # !start in the future
    , ('m', 'RETAIL_SALES_FOOD_rog', '2015-10-30', '1999-10-01'), ('d', 'BRENT', days_ahead(-1), days_ahead(-7)), ('d', 'BRENT', days_ahead(1), None)
]


@pytest.fixture(scope="module", params=BAD_ARGS_LIST)
def malformed_args(request):
    keys = ['freq', 'name', 'start_date', 'end_date']
    return {k: v for k, v in zip(keys, request.param) if v}


class SimRequest:
    """Mocks incoming user *request*."""
    mimetype = None
    json = None

    def __init__(self, **kwargs):
        self._dict = kwargs

    @property
    def args(self):
        return self._dict


class Test_RequestArgs(TestCaseBase):
    def test_init_on_well_formed_args_without_dates_is_success(self):
        incoming_args = dict(name="GDP_yoy", freq='a')
        req = SimRequest(**incoming_args)
        args = RequestArgs(req)
        assert args.name == 'GDP_yoy'
        assert args.freq == 'a'
        assert args.start_date is None
        assert args.end_date is None

    def test_init_on_well_formed_args_with_valid_dates_is_success(self):
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
        
        
    # TypeError: test_init_on_bad_args_fails() missing 1 required 
    # positional argument: 'malformed_args'    
    
    def test_init_on_bad_args_fails(self, malformed_args):
        req = SimRequest(**malformed_args)
        with pytest.raises(HTTPException):
            RequestArgs(req)

class Test_RequestFrameArgs(TestCaseBase):
    def test_init_on_name_with_comma_is_success(self):
        incoming_args = dict(name="GDP_yoy,CPI_rog", freq='a')
        req = SimRequest(**incoming_args)
        args = RequestFrameArgs(req)
        assert args.names == ['GDP_yoy', 'CPI_rog']
        assert args.freq == 'a'
        assert args.start_date is None
        assert args.end_date is None

    def test_init_without_names_is_fine(self):
        incoming_args = dict(freq='a')
        req = SimRequest(**incoming_args)
        args = RequestFrameArgs(req)
        assert isinstance(args.names, list)

    def test_init_on_bad_args_fails(self):
        malformed_args = dict(name="GDP_yoy,DING_dong", freq='a')
        req = SimRequest(**malformed_args)
        with pytest.raises(HTTPException):
            RequestFrameArgs(req)


# TODO: simple args class not testsed

if __name__ == '__main__':
    pytest.main([__file__, '--maxfail=1'])
