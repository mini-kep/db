# coding: utf-8
"""Testing flask app

Based on tests reviewed at
    <https://github.com/mini-kep/db/issues/10>

and testing guidelines at
    <https://github.com/mini-kep/intro/blob/master/testing_guidelines/README.md>.

"""

import json
import unittest

from db.api.models import Datapoint
from db.api.errors import CustomError400
from db.api.views import get_datapoints_response

from . import TestCaseBase


class Test_API_Incoming(TestCaseBase):

    def get_response(self, data, headers):
        return self.client.post('/api/incoming', data=data, headers=headers)

    def test_on_no_auth_token_returns_forbidden_status_code_403(self):
        response = self.client.post('/api/incoming')
        assert response.status_code == 403

    def test_on_new_data_upload_successfull_with_code_200(self):
        _token_dict = dict(API_TOKEN=self.app.config['API_TOKEN'])
        _data = json.dumps(self._read_test_data())
        response = self.get_response(data=_data, headers=_token_dict)
        assert response.status_code == 200

    def test_on_existing_data_upload_successfull_with_code_200(self):
        _token_dict = dict(API_TOKEN=self.app.config['API_TOKEN'])
        _data = json.dumps(self._read_test_data()[0:10])
        response = self.get_response(data=_data, headers=_token_dict)
        assert response.status_code == 200

#FIXME: should empty test case be deleted?
class TestCaseQuery(TestCaseBase):
    """Prepare database for queries/GET method testing"""
    pass


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
        response = self.query_on_name_and_freq()
        data = json.loads(response.get_data().decode('utf-8'))
        expected_data = self._subset_test_data('CPI_NONFOOD_rog', 'm')
        assert data == expected_data


class Test_API_Names(TestCaseQuery):
    """Endpoint under test: /api/names/<freq>"""

    def query_names_for_freq(self, freq):
        return self.client.get('/api/names/{freq}'.format(freq=freq))

    def test_get_all_names_response_code_200(self):
        response = self.query_names_for_freq(freq='all')
        assert response.status_code == 200

    def test_get_all_names_returns_sorted_list_of_all_names(self):
        # call
        response = self.query_names_for_freq(freq='all')
        result = json.loads(response.get_data().decode('utf-8'))
        # expected result
        names = set([x['name'] for x in self._read_test_data()])
        expected_result = sorted(list(names))
        # check
        assert result == expected_result

    def test_get_names_returns_sorted_list_of_names_for_given_freq(self):
        for freq in ['a', 'q', 'm', 'w', 'd']:
            response = self.query_names_for_freq(freq=freq)
            assert response.status_code == 200
            result = json.loads(response.get_data().decode('utf-8'))
            # expected result
            expected_result = []
            for row in self._read_test_data():
                if row['freq'] == freq and row['name'] not in expected_result:
                    expected_result.append(row['name'])
            expected_result = sorted(expected_result)
            # check
            assert result == expected_result


class Test_API_Info(TestCaseQuery):
    """API under test: /api/info?name=<name>&freq=<freq>"""

    def query_get_start_and_end_date(self, _name='CPI_NONFOOD_rog', _freq='m'):
        params = dict(name=_name, freq=_freq)
        return self.client.get('/api/info', query_string=params)

    def get_dates(self, _name='CPI_NONFOOD_rog', _freq='m'):
        data = self._subset_test_data('CPI_NONFOOD_rog', 'm')
        return sorted([row['date'] for row in data])

    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_response_code_200(self):
        response = self.query_get_start_and_end_date()
        # check
        assert response.status_code == 200

    # NOT TODO: may be parametrised
    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_proper_dates(self):
        # call
        response = self.query_get_start_and_end_date('CPI_NONFOOD_rog', 'm')
        result = json.loads(response.get_data().decode('utf-8'))
        # expected
        dates = self.get_dates('CPI_NONFOOD_rog', 'm')
        # check
        assert result['start_date'] == dates[0]
        assert result['end_date'] == dates[-1]

# NOT TODO: may be paarmetrised


class Test_API_Errors(TestCaseBase):

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
        params = dict(name='CPI_NONFOOD_rog', freq='q',
                      start_date='2099-01-01')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400

    def test_datapoints_end_date_after_start_date_returns_400(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q', start_date='2010-01-01',
                      end_date='2000-01-01')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 400


class TestGetResponseDatapoints(TestCaseBase):

    data_dicts = [{"date": "1999-01-31", "freq": "m", "name": "CPI_ALCOHOL_rog", "value": 109.7},
                  {"date": "1999-01-31", "freq": "m",
                      "name": "CPI_FOOD_rog", "value": 110.4},
                  {"date": "1999-01-31", "freq": "m", "name": "CPI_NONFOOD_rog", "value": 106.2}]

    def _make_sample_datapoints_list(self):
        return [Datapoint(**params) for params in self.data_dicts]

    def test_json_serialising_is_valid(self):
        data = self._make_sample_datapoints_list()
        response = get_datapoints_response(data, 'json')
        parsed_json = json.loads(response.data)
        self.assertEqual(self.data_dicts, parsed_json)

    def test_csv_serialising_is_valid(self):
        data = self._make_sample_datapoints_list()
        response = get_datapoints_response(data, 'csv')
        csv_string = str(response.data, 'utf-8')
        self.assertEqual(
            ',CPI_ALCOHOL_rog\n1999-01-31,109.7\n1999-01-31,110.4\n1999-01-31,106.2\n', csv_string)

    def test_invalid_output_format_should_fail(self):
        data = self._make_sample_datapoints_list()
        with self.assertRaises(CustomError400):
            get_datapoints_response(data, 'html')

if __name__ == '__main__':
    unittest.main(module='test_views')
