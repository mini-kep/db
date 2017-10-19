"""Testing flask app

Based on tests reviewed at
    <https://github.com/mini-kep/db/issues/10>
    
and testing guidelines at
    <https://github.com/mini-kep/intro/blob/master/testing_guidelines/README.md>.

"""

import json
import unittest
import os
from random import randint

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

def subset_test_data_(name, freq):
    data = read_test_data()
    # Добавил сортировку
    filtered_data = [d for d in data if d['name'] == name and d['freq'] == freq]
    sorted_data = sorted(filtered_data, key=lambda item: utils.to_date(item['date']))
    return sorted_data
    

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
    app.config['API_TOKEN'] = 'token'
    return app 


class TestCaseBase(unittest.TestCase):
    def _prepare_db(self):
        data = read_test_data()
        for datapoint in data:
            datapoint['date'] = utils.to_date(datapoint['date'])
        fsa_db.session.bulk_insert_mappings(Datapoint, data)
        
    def _prepare_app(self):    
        self.app = make_app()               
        self.app_context = self.app.app_context()
        self.app_context.push()
        fsa_db.init_app(app=self.app)
        fsa_db.create_all()   
        
    def _mount_blueprint(self):
        self.app.register_blueprint(api_module)

    def _start_client(self):
        self.client = self.app.test_client()
        
    def setUp(self):   
        self._prepare_app()
        
    def tearDown(self):
        fsa_db.session.remove()
        fsa_db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)
        
class TestViewsDatapoints(TestCaseBase): 
    
    def setUp(self):   
        self._prepare_app()
        self._mount_blueprint()
        self._prepare_db()
        self._start_client()
        
    def query_on_name_and_freq(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m', format='json')
        return self.client.get('/api/datapoints', query_string=params)        
            
    def test_get_on_name_and_freq_is_found_with_code_200(self):        
        response = self.query_on_name_and_freq()
        assert response.status_code == 200

    def test_get_on_name_and_freq_returns_list_of_dicts_CPI_rog(self):
        response = self.query_on_name_and_freq()
        data = json.loads(response.get_data().decode('utf-8'))
        assert data[0] == {'date': '2016-06-30',
                           'freq': 'm',
                           'name': 'CPI_NONFOOD_rog',
                           'value': 100.5}
        
    # NOT TODO: may be parametrised    
    def test_test_get_on_name_and_freq_returns_list_of_dicts(self):
        response= self.query_on_name_and_freq()
        data = json.loads(response.get_data().decode('utf-8'))
        expected_data = subset_test_data_('CPI_NONFOOD_rog', 'm')
        # FIXME: order seems not guaranteed
        # EK - that's right, added sorting to subset_test_data_
        assert data == expected_data

# TODO: carefully bring tests from test_views_old.py
class Test_API_Incoming(TestCaseBase):
    def setUp(self):
        self._prepare_app()
        self._mount_blueprint()
        # Pay attention - database is not prepared in this case
        # we test insertion to it, so we don't need to prepare data upload
        self._start_client()

    def test_auth_forbidden(self):
        response = self.client.post('/api/incoming')
        assert response.status_code == 403

    def test_upload_data(self):
        response = self.client.post('/api/incoming',
                                 data=json.dumps(read_test_data()),
                                 headers=dict(API_TOKEN=self.app.config['API_TOKEN']))
        assert response.status_code == 200


# возможно потребуются дополнительные функции для Test_API_Names для валидации тела ответа,
# сейчас манипуляции с данными идут в теле теста, тут уже лучше вам сделать, как будет понятнее.
# Test /api/names/<freq>
class Test_API_Names(TestCaseBase):

    def setUp(self):
        self._prepare_app()
        self._mount_blueprint()
        self._prepare_db()
        self._start_client()

    def test_getting_full_name_list(self):
        response = self.client.get('/api/names/all')
        # Test response code is ok
        assert response.status_code == 200
        # Starting to validate response body
        data = read_test_data()
        expected_response_body = []
        for row in data:
            if row['name'] not in expected_response_body:
                expected_response_body.append(row['name'])
        # Sort expected response body
        expected_response_body = sorted(expected_response_body)
        # Compare response body and expected response body
        response_body = json.loads(response.get_data().decode('utf-8'))
        assert response_body == expected_response_body

    def test_getting_names_for_random_freq(self):
        # Read test data
        data = read_test_data()
        # Get random freq from test data
        random_freq = data[randint(0, len(data))].get('freq')
        # Send request
        response = self.client.get(f'/api/names/{random_freq}')
        # Test response code is ok
        assert response.status_code == 200
        # Starting to validate response body
        expected_response_body = []
        for row in data:
            if row['freq'] == random_freq and row['name'] not in expected_response_body:
                expected_response_body.append(row['name'])
        # Sort expected response body
        expected_response_body = sorted(expected_response_body)
        # Compare response body and expected response body
        response_body = json.loads(response.get_data().decode('utf-8'))
        assert response_body == expected_response_body


# Test /api/info?name=<name>&freq=<freq>
class Test_API_Info(TestCaseBase):
    def setUp(self):
        self._prepare_app()
        self._mount_blueprint()
        self._prepare_db()
        self._start_client()

    def test_getting_info_start_date_end_date(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m')
        response = self.client.get('/api/info', query_string=params)
        # Test response code is ok
        assert response.status_code == 200
        # Select all dates from test json file by same parameters
        data = read_test_data()
        dates_from_raw_json = [row['date'] for row in data if row['name'] == 'CPI_NONFOOD_rog' and row['freq'] == 'm']
        # Sort these dates
        sorted_dates_from_raw_json = sorted(dates_from_raw_json)
        expected_start_date = sorted_dates_from_raw_json[0]
        expected_end_date = sorted_dates_from_raw_json[-1]
        # Compare response body and expected response body
        response_body = json.loads(response.get_data().decode('utf-8'))
        assert {'start_date':expected_start_date, 'end_date':expected_end_date} == response_body


class Test_API_Errors(TestCaseBase):
    def setUp(self):
        self._prepare_app()
        self._mount_blueprint()
        self._prepare_db()
        self._start_client()

    def test_empty_params(self):
        response = self.client.get('/api/datapoints')
        assert response.status_code == 400

    def test_freq_doesnt_exist(self):
        params = dict(name='CPI_NONFOOD_rog', freq='z')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_name_doesnt_exist_for_given_freq(self):
        params = dict(name='wrong_name', freq='q')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_start_date_in_future(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q', start_date='2099-01-01')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_start_date_more_than_end_date(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q', start_date='2010-01-01', end_date='2000-01-01')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400


if __name__ == '__main__':
    unittest.main(module='test_views')
    z = read_test_data()
    t = TestViewsDatapoints()
    t.setUp()
    response = t.query_on_name_and_freq()
    data = json.loads(response.get_data().decode('utf-8'))
    a = subset_test_data_('CPI_NONFOOD_rog', 'm')
