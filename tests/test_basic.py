"""Testing flask app

Based on tests reviewed at
    <https://github.com/mini-kep/db/issues/10>

and testing guidelines at
    <https://github.com/mini-kep/intro/blob/master/testing_guidelines/README.md>.

"""

import json
import unittest
import os


from db import get_app
from db.api.models import Datapoint
from db.api import utils
from db import db as fsa_db
from db.api.views import api_bp as api_module
from db.custom_api.views import custom_api_bp
from flask import current_app


class TestCaseBase(unittest.TestCase):

    def _make_app(self):
        app = get_app()
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        app.config['API_TOKEN'] = 'token'
        return app

    @property
    def test_data(self):
        return self._read_test_data()

    def _read_test_data(self, filename='test_data_2016H2.json'):
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(tests_folder, 'test_data', filename)
        with open(path) as file:
            return json.load(file)

    def _subset_test_data(self, name, freq):
        data = self._read_test_data()

        def is_var(d): return d['name'] == name and d['freq'] == freq

        def sorter_func(item): return utils.to_date(item['date'])
        return sorted(filter(is_var, data), key=sorter_func)

    def _prepare_db(self):
        data = self._read_test_data()
        for datapoint in data:
            datapoint['date'] = utils.to_date(datapoint['date'])
        fsa_db.session.bulk_insert_mappings(Datapoint, data)

    def _prepare_app(self):
        self.app = self._make_app()
        self.app.register_blueprint(api_module)
        self.app.register_blueprint(custom_api_bp)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        fsa_db.init_app(app=self.app)
        fsa_db.create_all()

    def setUp(self):
        self._prepare_app()
        self._prepare_db()

    def tearDown(self):
        fsa_db.session.remove()
        fsa_db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)


class TestViewsDatapoints(TestCaseBase):

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
    # unittest.main(module='test_basic')
    q = TestViewsDatapoints()
    q.setUp()
    response = q.query_on_name_and_freq()
    resp = q.client.get('/ru/series/CPI_rog/a')
    print(resp.data)
