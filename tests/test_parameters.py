import pytest
from db.api.parameters import RequestArgs, RequestFrameArgs


class Test_RequestArgs():
    
    def test_success(self):
        pass
        # incoming_args = dict(name='BRENT', freq='d', start_date='2017-01-01') 
        # args = DatapointArgs(incoming_args, DummyValidator)
        # assert args.freq == 'd'
        # assert args.name == 'BRENT'
        # assert args.start == to_date('2017-01-01')
        # assert args.end is None

if __name__ == '__main__':
    pytest.main([__file__])
