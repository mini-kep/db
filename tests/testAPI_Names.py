import json
import unittest
from random import randint
import tests
from tests import app, db, TestCase


# Test /api/names/<freq>
class TestAPI_Names(TestCase):
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


if __name__ == '__main__':
    unittest.main()