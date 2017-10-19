import json
import unittest
import os

from flask import current_app

from db import _app
from db import db as fsa_db
from db.api import utils  
from db.api.models import Datapoint

def read_test_data(filename = 'test_data_2016H2.json'):
    tests_folder = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(tests_folder, filename)
    with open(path) as file:
        return json.load(file)

# db/__init__.py

# db is both package name and SQLA database
# db = SQLAlchemy()
#
#def _app():
#    return Flask(__name__)
#
#def create_app(config=None):
#    app = Flask(__name__)
#    # make config optioal - easier for debugging.
#    if config:
#        app.config.from_object(config)
#    db.init_app(app)
#    return app
    

def make_app():
    app = _app() # was: Flask(__name__)
    app.testing = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        
    return app 


class BasicsTestCase(unittest.TestCase):
    def prepare_db(self):
        data = read_test_data()
        for datapoint in data:
            datapoint['date'] = utils.to_date(datapoint['date'])
        fsa_db.session.bulk_insert_mappings(Datapoint, data)
    
    def setUp(self):
        self.app = make_app()               
        self.app_context = self.app.app_context()
        self.app_context.push()
        fsa_db.init_app(app=self.app)
        fsa_db.create_all()

    def tearDown(self):
        fsa_db.session.remove()
        fsa_db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)
 

if __name__ == '__main__':
    unittest.main(module='test_basic')
    z = read_test_data()