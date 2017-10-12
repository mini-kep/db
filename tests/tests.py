import json
import os
from random import randint
import unittest

from db import create_app, db
from db.api.views import api as api_module
from utils import to_date

# EP: must have repo root on path, but why exactly are we doing this? 
#     I ran the tests without path tweaking and they worked locally
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

# create test app
app = create_app('config.TestingConfig')
app.register_blueprint(api_module)

class TestCase(unittest.TestCase):

    def _read_test_data(self):
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(tests_folder,'test_data.json')) as data_file:
            return data_file.read()    
    
    def setUp(self):
        db.create_all(app=app)
        self.app = app.test_client()        

    def tearDown(self):
        db.session.remove()
        db.drop_all(app=app)

class TestAPI_Incoming(TestCase):

    def test_auth_forbidden(self):
        response = self.app.post('/api/incoming')
        assert response.status_code == 403

    def test_upload_data(self):
        data = self._read_test_data()
        response = self.app.post('/api/incoming',
                                 data=data,
                                 headers=dict(API_TOKEN=app.config['API_TOKEN']))
        assert response.status_code == 200

    # methods below may not pass  <https://github.com/mini-kep/intro/wiki/Testing-guidelines#checklist>  
    
    # FIXME: this should be two tests with one assert per test, may not pass  <https://github.com/mini-kep/intro/wiki/Testing-guidelines#checklist>     
    def test_json_output_format(self):
        # Upload data
        data = self._read_test_data()
        self.app.post('/api/incoming',
                      data=data,
                      headers=dict(API_TOKEN=app.config['API_TOKEN']))
        # Check response
        params = dict(name='INVESTMENT_rog', freq='m', format='json')
        response = self.app.get('/api/datapoints', query_string=params)
        response_body = json.loads(response.get_data().decode('utf-8'))
        # Select data from test json file by same parameters
        expected_response = [row for row in json.loads(data) if row['name']=='INVESTMENT_rog' and row['freq']=='m']
        # Sort by date
        expected_response = sorted(expected_response, key=lambda item: to_date(item['date']))
        assert response.status_code == 200
        assert response_body == expected_response

    # FIXME: this is such a nested test, need refactor 
    def test_csv_output_format(self):
        # Upload data
        data = self._read_test_data()
        self.app.post('/api/incoming',
                      data=data,
                      headers=dict(API_TOKEN=app.config['API_TOKEN']))
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
