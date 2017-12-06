import pytest, json
import tests
from tests.test_basic import TestCaseBase
from io import BytesIO

ENDPOINT = "api/spline"


class TestImages(TestCaseBase):

    @property
    def token(self):
        return self.app.config['API_TOKEN']

    @property
    def token_dict(self):
        return dict(API_TOKEN=self.token)

    def get(self, param):
        return self.client.get(ENDPOINT, query_string=param)


class Test_GET(TestImages):

    def query_on_name_and_freq(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m')
        return self.client.get('/api/spline', query_string=params)

    def test_get_on_name_and_freq_is_found_with_code_200(self):
        response = self.query_on_name_and_freq()
        assert response.status_code == 200

    def test_get_on_name_and_freq_returns_img_spline_CPI_rog(self):
        response = self.query_on_name_and_freq()
        assert response.headers["Content-Type"] == "image/png"


class Test_GET_Errors(TestImages):

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

    v = TestImages()
    v.setUp()

    _name = 'CPI_NONFOOD_rog'
    _freq = 'a'
    params = dict(name=_name, freq=_freq)
    resp = v.client.get('/api/spline', query_string=params)
    print(resp)

    sample = json.dumps(v.test_data[0:10])
    resp = v.client.get('/api/spline', data=sample, headers=v.token_dict)
    print(resp)

    _name = 'CPI_NONFOOD_rog'
    _freq = 'a'
    _start_date = '2099-01-01'
    params = dict(name=_name, freq=_freq, start_date=_start_date)
    resp = v.client.get('/api/spline', query_string=params)
    print(resp)