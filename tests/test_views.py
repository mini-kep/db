# coding: utf-8
"""Testing flask app


Testing guidelines at
    <https://github.com/mini-kep/testing_guidelines/blob/master/README.md>.

"""

import pytest
import json

from tests.test_basic import TestCaseBase
from db.api.errors import CustomError400


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
            names = set([d['name']
                         for d in self.test_data if d['freq'] == freq])
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

    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_response_code_200(
            self):
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


# TODO: these test should relate to something else not covered in query.py

class TestDatapointsAPI(TestCaseBase):

    data_dicts = [
        {
            "date": "2016-06-01",
            "freq": "d",
            "name": "USDRUR_CB",
            "value": 65.9962
        },
        {
            "date": "2016-06-02",
            "freq": "d",
            "name": "USDRUR_CB",
            "value": 66.6156
        },
        {
            "date": "2016-06-03",
            "freq": "d",
            "name": "USDRUR_CB",
            "value": 66.7491
        }
    ]

    data_csv_string = ",USDRUR_CB\n2016-06-01,65.9962\n2016-06-02,66.6156\n2016-06-03,66.7491\n"

    params = dict(
        name='USDRUR_CB',
        freq='d',
        start_date='2016-06-01',
        end_date='2016-06-03',
        format='')

    def _get_response(self, response_format):
        self.params['format'] = response_format
        return self.client.get('api/datapoints', query_string=self.params).data

    def test_json_serialising_is_valid(self):
        # method under test: get
        # context or arguments: string, dict
        # expected result of behavior: returns valid json

        # test setup
        response_format = 'json'

        # call
        result_dict = json.loads(self._get_response(response_format))

        # check
        assert self.data_dicts == result_dict

    def test_csv_serialising_is_valid(self):
        # method under test: get
        # context or arguments: string, dict
        # expected result of behavior: returns valid csv string

        # test setup
        response_format = 'csv'

        # call
        result_string = str(self._get_response(response_format), 'utf-8')

        # check
        assert self.data_csv_string == result_string

    # def test_fails_on_invalid_format(self):
    #     # method under test: get
    #     # context or arguments: string, dict
    #     # expected result of behavior: raise HTTP exception
    #
    #     # test setup
    #     response_format = 'html'
    #
    #     # check
    #     with self.assertRaises(CustomError400):
    #
    #         # call
    #         self._get_response(response_format), 'utf-8'


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])

    v = TestCaseBase()
    v.setUp()
    resp = v.client.get('/ru/series/CPI_rog/a')
    print(resp)

    token = dict(API_TOKEN=v.app.config['API_TOKEN'])
    data = json.dumps(v.test_data[0:10])
    resp = v.client.post('/api/datapoints', data=data, headers=token)
    print(resp)

    _name = 'CPI_NONFOOD_rog'
    _freq = 'm'
    params = dict(name=_name, freq=_freq)
    resp = v.client.get('/api/info', query_string=params)
    print(resp)
