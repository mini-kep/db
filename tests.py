import os
import unittest
from flask import Flask
from db import app, db
from db.api.views import api as api_module
from config import basedir

# FIXME (EP):  move tests.py and test_josn to /tests folder?


class TestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)        
        # FIXME (EP): maybe better have a separate test config?        
        app.config.from_object('config.DevelopmentConfig')
        app.register_blueprint(api_module)
        db.create_all()
        db.init_app(app)
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_upload_data(self):
        with open(os.path.join(basedir,'test_data.json')) as data_file:
            data = data_file.read()
        response = self.app.post('/api/incoming',
                                 data=data,
                                 headers=dict(API_TOKEN=app.config['API_TOKEN']))
        assert response.status_code == 200
        
    # FIXME: I suggest the test name to be extended to reflect if it a good or bad result   
    def test_auth(self):
        response = self.app.post('/api/incoming')
        assert response.status_code == 403

    # FIXME: maybe also check for some values, not jeust response code?    
    def test_get_request(self):
        params = dict(name='BRENT', freq='d')
        response = self.app.get('/api/datapoints', query_string=params)
        assert response.status_code == 200

if __name__ == '__main__':
    unittest.main()
