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
    sorter_func = lambda item: utils.to_date(item['date'])
    sorted_data = sorted(filtered_data, key=sorter_func)
    return sorted_data
    
def make_app():
    # _app() returns Flask(__name__) with __name__ as db/__init__.py'
    app = get_app()
    app.testing = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['API_TOKEN'] = 'token'
    return app 


class TestCaseBase(unittest.TestCase):
    """Base class for testing flask application.    
    
    Use to compose setUp method: 
        self._prepare_app()
        self._mount_blueprint()
        self._prepare_db()
        self._start_client()
    
    """
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

class Test_API_Incoming(TestCaseBase):
    def setUp(self):
        self._prepare_app()
        self._mount_blueprint()
        self._start_client()

    #FIXME: test name should tell what is happening, why it fails
    def test_on_no_auth_token_returns_forbidden_status_code(self):
        response = self.client.post('/api/incoming')
        assert response.status_code == 403

    def test_upload_data_successful(self):
        _token_dict = dict(API_TOKEN=self.app.config['API_TOKEN'])
        _data = json.dumps(read_test_data())
        response = self.client.post('/api/incoming',
                                    data=_data,
                                    headers=_token_dict)
        assert response.status_code == 200


class TestCaseQuery(TestCaseBase): 
    """Prepare database for queries/GET method testing"""    
    def setUp(self):   
        self._prepare_app()
        self._mount_blueprint()
        self._prepare_db()
        self._start_client()

        
class Test_API_Datapoints(TestCaseQuery): 
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
        assert data == expected_data


# возможно потребуются дополнительные функции для Test_API_Names для валидации
# тела ответа,
# сейчас манипуляции с данными идут в теле теста, тут уже лучше вам сделать, 
# как будет понятнее.
# Test /api/names/<freq>
class Test_API_Names(TestCaseQuery):
    def query_names_for_freq(self, freq):
        return self.client.get(f'/api/names/{freq}')

    def query_random_freq_from_test_data(self):
        data = read_test_data()
        return data[randint(0, len(data))].get('freq')

    def test_get_all_names_response_code_200(self):
        response = self.query_names_for_freq(freq='all')
        assert response.status_code == 200

    def test_get_all_names_returns_sorted_list_of_all_names(self):
        # call
        response = self.query_names_for_freq(freq='all')
        result = json.loads(response.get_data().decode('utf-8'))
        # expected result
        names = set([x['name'] for x in read_test_data()])
        expected_result = sorted(list(names))
        # check
        assert result == expected_result

    def test_get_random_freq_response_code_200(self):
        random_freq = self.query_random_freq_from_test_data()
        response = self.query_names_for_freq(freq=random_freq)
        assert response.status_code == 200

    def test_get_names_on_random_freq_returns_sorted_list_of_names_for_given_random_freq(self):
        random_freq = self.query_random_freq_from_test_data()
        response = self.query_names_for_freq(freq=random_freq)
        result = json.loads(response.get_data().decode('utf-8'))
        # expected result
        expected_result = []
        for row in read_test_data():
            if row['freq'] == random_freq and row['name'] not in expected_result:
                expected_result.append(row['name'])
        expected_result = sorted(expected_result)
        # check
        assert result == expected_result


# Test /api/info?name=<name>&freq=<freq>
class Test_API_Info(TestCaseQuery):

    def query_get_start_and_end_date(self):
        params = dict(name='CPI_NONFOOD_rog', freq='m')
        return self.client.get('/api/info', query_string=params)

    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_response_code_200(self):
        response = self.query_get_start_and_end_date()
        # check
        assert response.status_code == 200

    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_dict_with_such_dates(self):
        response = self.query_get_start_and_end_date()
        result = json.loads(response.get_data().decode('utf-8'))
        # Select all dates from test json file by same parameters
        data = read_test_data()
        dates_from_raw_json = [row['date'] for row in data if row['name'] == 'CPI_NONFOOD_rog' and row['freq'] == 'm']
        # Sort these dates
        sorted_dates_from_raw_json = sorted(dates_from_raw_json)
        expected_start_date = sorted_dates_from_raw_json[0]
        expected_end_date = sorted_dates_from_raw_json[-1]
        # check
        assert result == {'start_date':expected_start_date, 'end_date':expected_end_date}

# NOT TODO: may be paarmetrised
class Test_API_Errors(TestCaseBase):
    def setUp(self):
        self._prepare_app()
        self._mount_blueprint()
        self._prepare_db()
        self._start_client()

    def test_datapoints_empty_params_returns_400(self):
        response = self.client.get('/api/datapoints')
        assert response.status_code == 400

    def test_datapoints_wrong_freq_returns_400(self):
        params = dict(name='CPI_NONFOOD_rog', freq='wrong_freq')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_datapoints_wrong_name_returns_400(self):
        params = dict(name='wrong_name', freq='q')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_datapoints_start_date_in_future_returns_400(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q', start_date='2099-01-01')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_datapoints_end_date_after_start_date_returns_400(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q', start_date='2010-01-01', 
                      end_date='2000-01-01')
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
