"""Testing flask app

Based on tests reviewed at
    <https://github.com/mini-kep/db/issues/10>

and testing guidelines at
    <https://github.com/mini-kep/intro/blob/master/testing_guidelines/README.md>.

"""

import json
import unittest
# import os

# from flask import current_app

from . import TestCaseBase

# from db import get_app
# from db import db as fsa_db
# from db.api import utils
# from db.api.models import Datapoint
# from db.api.views import api as api_module
# from db.custom_api.views import custom_api_bp


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
    unittest.main(module='test_basic')
    # z = read_test_data()
    # q = TestViewsDatapoints()
    # q.setUp()
    # response = q.query_on_name_and_freq()
    # resp = q.client.get('/ru/series/CPI_rog/a')
    # print(resp.data)
