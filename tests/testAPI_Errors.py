import unittest
from tests import app, db, TestCase


class TestAPI_Errors(TestCase):
    def _prepare_database(self):
        # FIXME: maybe this should not be done by posting to database,
        #        but rather connecting an existing databse
        data = self._read_test_data()
        self.app.post('/api/incoming',
                      data=data,
                      headers=dict(API_TOKEN=app.config['API_TOKEN']))

    def setUp(self):
        # this is from parent class
        db.create_all(app=app)
        self.app = app.test_client()
        self._prepare_database()

    def empty_params(self):
        response = self.app.get('/api/datapoints')
        assert response.status_code == 400

    def test_freq_doesnt_exist(self):
        params = dict(name='INVESTMENT_rog', freq='z')
        response = self.app.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_name_doesnt_exist_for_given_freq(self):
        params = dict(name='wrong_name', freq='q')
        response = self.app.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_start_date_in_future(self):
        params = dict(name='INVESTMENT_rog', freq='q', start_date='2099-01-01')
        response = self.app.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_start_date_more_than_end_date(self):
        params = dict(name='INVESTMENT_rog', freq='q', start_date='2010-01-01', end_date='2000-01-01')
        response = self.app.get('/api/datapoints', query_string=params)
        assert response.status_code == 400


if __name__ == '__main__':
    unittest.main()