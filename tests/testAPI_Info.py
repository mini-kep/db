import json
import unittest
import tests
from tests import app, db, TestCase


# Test /api/info?name=<name>&freq=<freq>
class TestAPI_Info(TestCase):
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

    def test_getting_info_start_date_end_date(self):
        params = dict(name='INVESTMENT_rog', freq='m')
        response = self.app.get('/api/info', query_string=params)
        # Test response code is ok
        assert response.status_code == 200
        # Select data from test json file by same parameters
        data = json.loads(self._read_test_data())
        dates_from_raw_json = [row['date'] for row in data if row['name'] == 'INVESTMENT_rog' and row['freq'] == 'm']
        # Sort
        sorted_dates_from_raw_json = sorted(dates_from_raw_json)
        expected_start_date = sorted_dates_from_raw_json[0]
        expected_end_date = sorted_dates_from_raw_json[-1]
        # Compare response body and expected response body
        response_body = json.loads(response.get_data().decode('utf-8'))
        assert {'start_date':expected_start_date, 'end_date':expected_end_date} == response_body


if __name__ == '__main__':
    unittest.main()