import unittest
from tests.test_basic import TestCaseBase
from db.api.errors import CustomError400
from db.api.utils import DatapointParameters
import datetime


def days_ahead(k):
    dt = datetime.date.today() + datetime.timedelta(days=k)
    return dt.strftime('%Y-%m-%d')


class TestDatapointParameters(TestCaseBase):

    @staticmethod
    def _make_args(freq, name, start, end):
        return dict(name=name,
                    freq=freq,
                    start_date=start,
                    end_date=end)

    def test_none_params_should_fail(self):
        args = self._make_args(None, None, None, None)
        with self.assertRaises(CustomError400):
            DatapointParameters(args)

    def test_date_is_transformed_correctly(self):
        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2015-03-25', '2016-04-01')
        dp = DatapointParameters(args)
        assert dp.get_start() == datetime.date(year=2015, month=3, day=25)
        assert dp.get_end() == datetime.date(year=2016, month=4, day=1)

    def test_on_wrong_sequence_of_dates_fails(self):
        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2015-10-30', '1999-10-01')
        with self.assertRaises(CustomError400):
            DatapointParameters(args).get_end()

    def test_on_start_in_future_fails(self):
        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', days_ahead(1), days_ahead(2))
        with self.assertRaises(CustomError400):
            DatapointParameters(args).get_start()

    def test_on_invalid_freq_should_fail(self):
        args = self._make_args('z', 'RETAIL_SALES_FOOD_rog', None, None)
        with self.assertRaises(CustomError400):
            DatapointParameters(args)

    def test_on_invalid_name_should_fail(self):
        args = self._make_args('m', 'BIBA_boba', None, None)
        with self.assertRaises(CustomError400):
            DatapointParameters(args)

    def test_freq_exist_on_good_param(self):
        freq_exist = DatapointParameters.validate_freq_exist('m')
        self.assertTrue(freq_exist)

    def test_freq_exist_on_bad_params_should_produce_correct_message(self):
        with self.assertRaises(CustomError400) as fail:
            DatapointParameters.validate_freq_exist('s')
        self.assertEqual(fail.exception.message, 'Invalid frequency <s>')

    def test_ending_date_is_optional(self):
        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2017-05-11', None)
        dp = DatapointParameters(args)
        assert dp.get_start() == datetime.date(year=2017, month=5, day=11)
        assert dp.get_end() == None



if __name__ == '__main__':
    unittest.main()
