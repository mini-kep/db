import json
import os
import unittest
from random import randint
from db import create_app, db
from db.api.views import api as api_module
from db.api.utils import to_date


# create test app
app = create_app('config.TestingConfig')
app.register_blueprint(api_module)


class TestCase(unittest.TestCase):
    def _read_test_data(self):
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(tests_folder, 'test_data.json')) as data_file:
            return data_file.read()

    def setUp(self):
        db.create_all(app=app)
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all(app=app)


class Test_API_Datapoints(TestCase):
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


class Test_API_Incoming(TestCase):
    def test_auth_forbidden(self):
        response = self.app.post('/api/incoming')
        assert response.status_code == 403

    def test_upload_data(self):
        data = self._read_test_data()
        response = self.app.post('/api/incoming',
                                 data=data,
                                 headers=dict(API_TOKEN=app.config['API_TOKEN']))
        assert response.status_code == 200


# Test /api/names/<freq>
class Test_API_Names(TestCase):
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

    def test_getting_full_name_list(self):
        response = self.app.get('/api/names/all')
        # Test response code is ok
        assert response.status_code == 200
        # Validate response body
        data = json.loads(self._read_test_data())
        expected_response_body = []
        for row in data:
            if row['name'] not in expected_response_body:
                expected_response_body.append(row['name'])
        # Sort result
        expected_response_body = sorted(expected_response_body)
        # Compare response body and expected response body
        response_body = json.loads(response.get_data().decode('utf-8'))
        assert response_body == expected_response_body

    def test_getting_names_for_random_freq(self):
        # Read test data
        data = json.loads(self._read_test_data())
        # Get random freq from test data
        random_freq = data[randint(0, len(data))].get('freq')
        # Send request
        response = self.app.get(f'/api/names/{random_freq}')
        # Test response code is ok
        assert response.status_code == 200
        # Validate response body
        expected_response_body = []
        for row in data:
            if row['freq'] == random_freq and row['name'] not in expected_response_body:
                expected_response_body.append(row['name'])
        # Sort result
        expected_response_body = sorted(expected_response_body)
        # Compare response body and expected response body
        response_body = json.loads(response.get_data().decode('utf-8'))
        assert response_body == expected_response_body


# Test /api/info?name=<name>&freq=<freq>
class Test_API_Info(TestCase):
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


class Test_API_Errors(TestCase):
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