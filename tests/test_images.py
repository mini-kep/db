#FIXME: msut use https://github.com/mini-kep/guidelines/blob/master/testing.md

import pytest
from datetime import date
from io import BytesIO

import db.api.image as image
from db.api.parameters import RequestArgs
from db.api.queries import DatapointOperations

from tests.test_basic import TestCaseBase


class SimRequest:
    """Mocks incoming user *request*."""
    mimetype = None
    json = None

    def __init__(self, **kwargs):
        self._dict = kwargs

    @property
    def args(self):
        return self._dict


class Test_API_Spline(TestCaseBase):
 
    def query_spline(self, params):
        return self.client.get('/api/spline', query_string=params)

    def test_get_on_name_and_freq_is_found_with_code_200(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m')
        response = self.query_spline(params)
        assert response.status_code == 200

    def test_get_on_name_and_freq_returns_img_png_type(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m', start_date="2016-10-29", end_date="2016-12-31")
        response = self.query_spline(params)
        assert response.headers["Content-Type"] == "image/png"


class Test_Utils_Spline(TestCaseBase):

    def test_get_data_for_spline(self):
        incoming_args = dict(freq='d', name='USDRUR_CB',
                             start_date='2016-10-29', end_date='2016-12-31')
        # setup
        req = SimRequest(**incoming_args)
        args = RequestArgs(req)
        query_data = DatapointOperations.select(**args.get_query_parameters())
        # call
        data = image.get_data_for_spline(query_data)
        # check
        assert date(2016, 10, 29) in data["x"]
        assert 62.9037 in data["y"]
        assert date(2016, 12, 31) in data["x"]
        assert 60.6569 in data["y"]

    def test_make_png_spline(self):
        class Item:
            date = date(2016, 10, 29)
            value = 62.9037
        data = [Item()]
        png_output = image.make_png(data)
        params = dict(freq='d', name='USDRUR_CB',
                      start_date='2016-10-29', end_date='2016-10-29')
        response = self.client.get('/api/spline', query_string=params)
        assert response.data == png_output

    def test_create_png_from_dict_spline(self):
        data = dict(x=[date(2016, 10, 29)],
                    y=[62.9037])
        png_output = image.create_png_from_dict(data, image.SPLINE_GPARAMS)
        params = dict(freq='d', name='USDRUR_CB',
                      start_date='2016-10-29', end_date='2016-10-29')
        response = self.client.get('/api/spline', query_string=params)
        assert response.data == png_output


# FIXME: more this to parameters.py testing of arg classes
class Test_API_Spline_Errors(TestCaseBase):

    def test_images_empty_params_returns_error(self):
        response = self.client.get('/api/spline')
        assert response.status_code == 422

    def test_images_wrong_freq_returns_error(self):
        params = dict(name='CPI_NONFOOD_rog', freq='wrong_freq')
        response = self.client.get('/api/spline', query_string=params)
        assert response.status_code == 422

    def test_images_wrong_name_returns_error(self):
        params = dict(name='wrong_name', freq='q')
        response = self.client.get('/api/spline', query_string=params)
        assert response.status_code == 422

    def test_images_start_date_in_future_returns_error(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q',
                      start_date='2099-01-01')
        response = self.client.get('/api/spline', query_string=params)
        assert response.status_code == 422

    def test_images_end_date_after_start_date_returns_error(self):
        params = dict(
            name='CPI_NONFOOD_rog',
            freq='q',
            start_date='2010-01-01',
            end_date='2000-01-01')
        response = self.client.get('/api/spline', query_string=params)
        assert response.status_code == 422

if __name__ == '__main__': # pragma no cover
    pytest.main([__file__, '--maxfail=1'])
