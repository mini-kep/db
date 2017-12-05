import pytest
from tests.test_basic import TestCaseBase

API_SERIES_URL = 'api/series'
BAD_PARAMETERS_STATUS_CODE = 422

sample_valid_params = dict(
    freq='a',
    name='GDP_yoy')
expected_output = ',GDP_yoy\n2016-12-31,99.8\n'

sample_valid_params_with_dates = dict(
    freq='m',
    name='CPI_FOOD_rog',
    start_date='2016-11-01',
    end_date='2017-01-01')
expected_output_with_dates = """,CPI_FOOD_rog
2016-11-30,100.8
2016-12-31,100.6'
"""

sample_invalid_params_start_date_gt_end_date = dict(
    freq='m',
    name='CPI_FOOD_rog',
    start_date='2017-01-01',
    end_date='2016-01-01')


class Test_Api_Series(TestCaseBase):
    def test_get_method_without_params_should_fail(self):
        response = self.client.get(API_SERIES_URL)
        assert response.status_code == BAD_PARAMETERS_STATUS_CODE

    def test_get_method_on_valid_params_is_ok(self):
        response = self.client.get(API_SERIES_URL, query_string=sample_valid_params)
        data = response.get_data().decode('utf-8')
        assert data == expected_output

    def test_calling_on_valid_params_with_dates_is_ok(self):
        response = self.client.get(API_SERIES_URL, query_string=sample_valid_params_with_dates)
        data = response.get_data().decode('utf-8')
        assert data == expected_output_with_dates

    def test_calling_on_invalid_params_start_date_gt_end_date_should_fail(self):
        response = self.client.get(API_SERIES_URL, query_string=sample_invalid_params_start_date_gt_end_date)
        assert response.status_code == BAD_PARAMETERS_STATUS_CODE
