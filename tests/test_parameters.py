import pytest
import arrow


from db.api.parameters import RequestArgs, RequestFrameArgs
from werkzeug.exceptions import HTTPException


class SimRequest:  
    """Mocks incoming user *request*."""
    mimetype = None
    json = None        
    
    def __init__(self, **kwargs):
        self._dict = kwargs
    
    @property
    def args(self):     
        return self._dict


class Test_RequestArgs():
    def test_init_on_well_formed_args_without_dates_is_success(self):
        incoming_args = dict(name="GDP_yoy", freq='a')
        req = SimRequest(**incoming_args)   
        args = RequestArgs(req)
        assert args.name == 'GDP_yoy'
        assert args.freq == 'a'
        assert args.start_date is None
        assert args.end_date is None
        assert args.format == 'csv'

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
        assert args.query_param

    #TODO: this needs to be parametrised to touch all validation functions
    #      see pytest parametrisation example
    #      https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions
    def test_init_on_bad_args_fails(self):            
        malformed_args = dict(name='BRENT') 
        req = SimRequest(**malformed_args)
        with pytest.raises(HTTPException):
            RequestArgs(req)


class Test_RequestFrameArgs():
    def test_init_on_well_formed_args_is_success(self):
        incoming_args = dict(names="GDP_yoy,CPI_rog", freq='a')
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
        assert args.names is None
        
    def test_init_on_bad_args_is_fails(self):
        malformed_args = dict(names="GDP_yoy,DING_dong", freq='a')
        req = SimRequest(**malformed_args)
        with pytest.raises(HTTPException):
            RequestArgs(req)


if __name__ == '__main__':
    pytest.main([__file__])
