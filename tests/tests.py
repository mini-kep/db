import os
import unittest
import json
from db import create_app, db
from db.api.views import api as api_module


app = create_app('config.TestingConfig')
app.register_blueprint(api_module)


class TestCase(unittest.TestCase):

    def setUp(self):
        db.create_all(app=app)
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all(app=app)

    # FIXME: I suggest the test name to be extended to reflect if it a good or bad result
    def test_auth_forbidden(self):
        response = self.app.post('/api/incoming')
        assert response.status_code == 403

    def test_upload_data(self):
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(tests_folder,'test_data.json')) as data_file:
            data = data_file.read()
        response = self.app.post('/api/incoming',
                                 data=data,
                                 headers=dict(API_TOKEN=app.config['API_TOKEN']))
        assert response.status_code == 200

    # FIXME: maybe also check for some values, not jeust response code?    
    def test_get_request(self):
        # Upload data
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(tests_folder, 'test_data.json')) as data_file:
            data = data_file.read()
        self.app.post('/api/incoming',
                      data=data,
                      headers=dict(API_TOKEN=app.config['API_TOKEN']))
        # Check response
        params = dict(name='INVESTMENT_rog', freq='m')
        response = self.app.get('/api/datapoints', query_string=params)
        expected_response = [row for row in json.loads(data) if row['name']=='INVESTMENT_rog' and row['freq']=='m']
        response_body = json.loads(response.get_data().decode('utf-8'))
        assert response.status_code == 200
        assert response_body == expected_response


if __name__ == '__main__':
    unittest.main()
