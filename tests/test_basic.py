"""Testing flask app

Based on tests reviewed at
    <https://github.com/mini-kep/db/issues/10>
    
and testing guidelines at
    <https://github.com/mini-kep/intro/blob/master/testing_guidelines/README.md>.

"""

import json
import unittest
import os

from flask import current_app

from db import get_app
from db import db as fsa_db
from db.api import utils  
from db.api.models import Datapoint
from db.api.views import api as api_module

def read_test_data(filename = 'test_data_2016H2.json'):
    tests_folder = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(tests_folder, filename)
    with open(path) as file:
        return json.load(file)

# db/__init__.py --------------------------------------------------------------
#
# db = SQLAlchemy()
#
#def get_app():
#    return Flask(__name__)
#
#def create_app(config=None):
#    app = Flask(__name__)
#    app.config.from_object(config)
#    db.init_app(app)
#    return app
# -----------------------------------------------------------------------------
    

def make_app():
    # _app() returns Flask(__name__) with __name__ as db/__init__.py'
    app = get_app()
    app.testing = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        
    return app 


class TestCaseBase(unittest.TestCase):
    def prepare_db(self, filename=None):
        if filename is None:
            data = read_test_data() # use default parameter in function
        else:
            data = read_test_data(filename)
        for datapoint in data:
            datapoint['date'] = utils.to_date(datapoint['date'])
        fsa_db.session.bulk_insert_mappings(Datapoint, data)
        
    def prepare_app(self):    
        self.app = make_app()               
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        fsa_db.init_app(app=self.app)
        fsa_db.create_all()   
        
    def mount_blueprint(self):
        self.app.register_blueprint(api_module)
        
    def setUp(self):   
        self.prepare_app()
        
    def tearDown(self):
        fsa_db.session.remove()
        fsa_db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)
        
class TestViewsDatapoints(TestCaseBase): 
    
    def setUp(self):   
        self.prepare_app()
        self.prepare_db()
        self.mount_blueprint()
        
    def query_on_name_and_freq(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m', format='json')
        return self.client.get('/api/datapoints', query_string=params)        
            
    def test_get_on_name_and_freq_is_found_with_code_200(self):        
        response = self.query_on_name_and_freq()
        assert response.status_code == 200

    def test_get_on_name_and_freq_returns_list_of_dicts(self):
        response = self.query_on_name_and_freq()
        data = json.loads(response.get_data().decode('utf-8'))
        assert data[0] == {'date': '2016-06-30',
                           'freq': 'm',
                           'name': 'CPI_NONFOOD_rog',
                           'value': 100.5}
 

if __name__ == '__main__':
    unittest.main(module='test_basic')
    z = read_test_data()
    t = TestViewsDatapoints()
    t.setUp()
    response = t.query_on_name_and_freq()
