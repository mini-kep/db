# coding: utf-8
"""Testing flask app


Testing guidelines at
    <https://github.com/mini-kep/testing_guidelines/blob/master/README.md>.

"""

import pytest
import json

from tests.test_basic import TestCaseBase


## TODO - must separate which code is which
#ERROR_CODES = (422, 400, 403)
#
#class Test_api_Names(TestCaseBase):
#
#
#    def test_get_all_names_response_code_200(self):
#        response = self.query_names('all')
#        assert response.status_code == 200
#
#    def test_get_all_names_returns_sorted_list_of_all_names(self):
#        # call
#        response = self.query_names('all')
#        result = json.loads(response.get_data().decode('utf-8'))
#        # expected result
#        names = set([x['name'] for x in self.test_data])
#        expected_result = sorted(list(names))
#        # check
#        assert result == expected_result


class Test_API_Names(TestCaseBase):
    """Endpoint under test: /api/names/<freq>"""

    def query_names(self, freq):
        return self.client.get('/api/names/{freq}'.format(freq=freq))

    def test_get_names_returns_sorted_list_of_names_for_given_freq(self):
        for freq in ['a', 'q', 'm', 'd']:
            response = self.query_names(freq=freq)
            assert response.status_code == 200
            result = json.loads(response.get_data().decode('utf-8'))
            # expected result
            names = set([d['name'] for d in self.test_data if d['freq']==freq])
            expected_result = sorted(list(names))
            # check
            assert result == expected_result


class Test_API_Info(TestCaseBase):
    """API under test: /api/info/?name=<name>"""

    def query_get_start_and_end_date(self, _name='CPI_NONFOOD_rog', _freq='m'):
        params = dict(name=_name, freq=_freq)
        return self.client.get('/api/info', query_string=params)

    def get_dates(self, _name='CPI_NONFOOD_rog', _freq='m'):
        data = self._subset_test_data('CPI_NONFOOD_rog', 'm')
        return sorted([row['date'] for row in data])

    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_response_code_200(self):
        response = self.query_get_start_and_end_date()
        assert response.status_code == 200

    # NOT TODO: may be parametrised
    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_proper_dates(self):
        # call
        response = self.query_get_start_and_end_date('CPI_NONFOOD_rog', 'm')
        data = response.get_data().decode('utf-8')
        result = json.loads(data)
        # expected
        dates = self.get_dates('CPI_NONFOOD_rog', 'm')
        # check
        assert result['m']['start_date'] == dates[0]
        assert result['m']['latest_date'] == dates[-1]


#TODO: these test should relate to something else not covered in query.py

#class TestGetResponseDatapoints(TestCaseBase):
#
#    data_dicts = [{"date": "1999-01-31", "freq": "m", "name": "CPI_ALCOHOL_rog", "value": 109.7},
#                  {"date": "1999-01-31", "freq": "m",
#                      "name": "CPI_FOOD_rog", "value": 110.4},
#                  {"date": "1999-01-31", "freq": "m", "name": "CPI_NONFOOD_rog", "value": 106.2}]
#
#    def _make_sample_datapoints_list(self):
#        return [Datapoint(**params) for params in self.data_dicts]
#
#    def test_json_serialising_is_valid(self):
#        data = self._make_sample_datapoints_list()
#        response = get_datapoints_response(data, 'json')
#        parsed_json = json.loads(response.data)
#        self.assertEqual(self.data_dicts, parsed_json)
#
#    def test_csv_serialising_is_valid(self):
#        data = self._make_sample_datapoints_list()
#        response = get_datapoints_response(data, 'csv')
#        csv_string = str(response.data, 'utf-8')
#        self.assertEqual(
#            ',CPI_ALCOHOL_rog\n1999-01-31,109.7\n1999-01-31,110.4\n1999-01-31,106.2\n', csv_string)
#
#    def test_invalid_output_format_should_fail(self):
#        data = self._make_sample_datapoints_list()
#        with self.assertRaises(CustomError400):
#            get_datapoints_response(data, 'html')


if __name__ == '__main__': # pragma: no cover
    pytest.main([__file__])
    
    v = TestCaseBase()
    v.setUp()
    resp = v.client.get('/ru/series/CPI_rog/a')
    print(resp)
 
    token = dict(API_TOKEN=v.app.config['API_TOKEN'])
    data = json.dumps(v.test_data[0:10])
    resp = v.client.post('/api/datapoints', data=data, headers=token)
    print(resp)
    
    _name='CPI_NONFOOD_rog'
    _freq='m'
    params = dict(name=_name, freq=_freq)
    resp = v.client.get('/api/info', query_string=params)
    print(resp)
    
    
    dict(name="BRENT")
    
    # class werkzeug.EnvironBuilder(path='/', base_url=None, query_string=None, method='GET', input_stream=None, content_type=None, content_length=None, errors_stream=None, multithread=False, multiprocess=False, run_once=False, headers=None, data=None, environ_base=None, environ_overrides=None, charset='utf-8')
    
    
    
