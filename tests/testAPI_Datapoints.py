import json
import unittest
from random import randint
from utils import to_date
from tests import app, db, TestCase


class TestAPI_Datapoints(TestCase):
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

    # FIXME: test name not inofrmative with respect what the test
    def test_json_output_format(self):
        # ERROR: must check contents of test_data.json and regenerate it as
        #        this variable is invalid in actual dataset since 2016?
        #        need to use more generic example
        #        name='INVESTMENT_rog', freq='m'
        params = dict(name='INVESTMENT_rog', freq='m', format='json')
        response = self.app.get('/api/datapoints', query_string=params)
        assert response.status_code == 200

    # FIXME: very convoluted test, need simplfy, rename with respect to what is tested and result expected
    def test_json_output_format_part2(self):
        params = dict(name='INVESTMENT_rog', freq='m', format='json')
        response = self.app.get('/api/datapoints', query_string=params)
        # FIXME: why not use response.json()?
        response_body = json.loads(response.get_data().decode('utf-8'))

        # FIXME: this test has the benefit of fuller coverage of dataset,
        #        but htis is more of a integration test as opposed to unit test
        #        we need fail-quick unit tests before integration tests
        # Select data from test json file by same parameters
        data = self._read_test_data()
        expected_response = [row for row in json.loads(data) if row['name'] == 'INVESTMENT_rog' and row['freq'] == 'm']
        # Sort by date
        expected_response = sorted(expected_response, key=lambda item: to_date(item['date']))
        # --------------------------------------------------------------------
        assert response_body == expected_response

    # FIXME: very nested test, need refactor
    def test_csv_output_format(self):
        # Read test data
        data = self._read_test_data()
        # Get response
        params = dict(name='INVESTMENT_rog', freq='m', format='csv')
        response = self.app.get('/api/datapoints', query_string=params)
        response_body = response.get_data().decode('utf-8')
        # Get random data from raw JSON with same parameters as in request
        raw_data = [row for row in json.loads(data) if row['name'] == 'INVESTMENT_rog' and row['freq'] == 'm']
        random_data_point = raw_data[randint(0, len(raw_data))]
        # Format random data to like we have in response csv
        random_data_to_check = f'{random_data_point["date"]},{random_data_point["value"]}'
        # Check if random datapoint exists in csv
        assert random_data_to_check in response_body.split('\n')

        # TODO: we do not have tests for getting datapoints yet

if __name__ == '__main__':
    unittest.main()