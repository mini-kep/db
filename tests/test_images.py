#FIXME: msut use https://github.com/mini-kep/guidelines/blob/master/testing.md

import pytest
import json

from tests.test_basic import TestCaseBase


# FIXME: by Test_GET you cannot understand what is being tested  
class Test_API_Spline(TestCaseBase):
 
    # EP: so bad - params should bot be inside method
    def query_on_name_and_freq(self, params):
        return self.client.get('/api/spline', query_string=params)

    def test_get_on_name_and_freq_is_found_with_code_200(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m')
        response = self.query_on_name_and_freq(params)
        assert response.status_code == 200

    #EP: same anout params   
    def test_get_on_name_and_freq_returns_img_spline_CPI_rog(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m', start_date="2016-10-29", end_date="2016-12-31")
        response = self.query_on_name_and_freq(params)
        assert response.headers["Content-Type"] == "image/png"


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
