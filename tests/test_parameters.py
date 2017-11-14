import datetime
import pytest
import arrow

from tests.test_basic import TestCaseBase
from db.api.parameters import RequestArgs, RequestFrameArgs
from werkzeug.exceptions import HTTPException


@pytest.fixture(scope='module')
def malformed_args():
    return [
        dict(name='BRENT'),
        dict(name='a', freq='q'),
        dict(name='BRENT', freq='a'),
        dict(
            name='BRENT',
            freq='d',
            start_date=arrow.get(2018, 1, 1).date(),
            end_date=arrow.get(2017, 1, 1).date()),
        dict(
            name='BRENT',
            freq='d',
            start_date=arrow.get(2017, 2, 1).date(),
            end_date=arrow.get(2017, 1, 1).date()),
    ]


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

    @pytest.mark.parametrize('malformed_args', malformed_args)
    def test_init_on_bad_args_fails(self):
        malformed_args = dict(name='BRENT')
        req = SimRequest(**malformed_args)
        with pytest.raises(HTTPException):
            RequestArgs(req)




def days_ahead(k):
    dt = datetime.date.today() + datetime.timedelta(days=k)
    return dt.strftime('%Y-%m-%d')

#
#class TestDatapointParameters(TestCaseBase):
#
#    @staticmethod
#    def _make_args(freq, name, start, end):
#        return dict(name=name,
#                    freq=freq,
#                    start_date=start,
#                    end_date=end)
#
#    def test_none_params_should_fail(self):
#        args = self._make_args(None, None, None, None)
#        with self.assertRaises(CustomError400):
#            DatapointParameters(args)
#
#    def test_date_is_transformed_correctly(self):
#        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2015-03-25', '2016-04-01')
#        dp = DatapointParameters(args)
#        assert dp.get_start() == datetime.date(year=2015, month=3, day=25)
#        assert dp.get_end() == datetime.date(year=2016, month=4, day=1)
#
#    def test_on_wrong_sequence_of_dates_fails(self):
#        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2015-10-30', '1999-10-01')
#        with self.assertRaises(CustomError400):
#            DatapointParameters(args).get_end()
#
#    def test_on_start_in_future_fails(self):
#        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', days_ahead(1), days_ahead(2))
#        with self.assertRaises(CustomError400):
#            DatapointParameters(args).get_start()
#
#    def test_on_invalid_freq_should_fail(self):
#        args = self._make_args('z', 'RETAIL_SALES_FOOD_rog', None, None)
#        with self.assertRaises(CustomError400):
#            DatapointParameters(args)
#
#    def test_on_invalid_name_should_fail(self):
#        args = self._make_args('m', 'BIBA_boba', None, None)
#        with self.assertRaises(CustomError400):
#            DatapointParameters(args)
#
#    def test_freq_exist_on_good_param(self):
#        freq_exist = DatapointParameters.validate_freq_exist('m')
#        self.assertTrue(freq_exist)
#
#    def test_freq_exist_on_bad_params_should_produce_correct_message(self):
#        with self.assertRaises(CustomError400) as fail:
#            DatapointParameters.validate_freq_exist('s')
#        self.assertEqual(fail.exception.message, 'Invalid frequency <s>')
#
#    def test_ending_date_is_optional(self):
#        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2017-05-11', None)
#        dp = DatapointParameters(args)
#        assert dp.get_start() == datetime.date(year=2017, month=5, day=11)
#        assert dp.get_end() == None



class Test_RequestFrameArgs(TestCaseBase):
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
