# coding: utf-8
import pytest
import json

from tests.test_basic import TestCaseBase

# ERROR_CODES:
# 422 - bad parameters
# 403 - not authorised


ENDPOINT = "api/datapoints" 

class TestDatapoints(TestCaseBase):
        
    @property
    def token(self):
        return self.app.config['API_TOKEN']
    
    @property
    def token_dict(self):
        return dict(API_TOKEN=self.token)
    
    def post(self, data):
        return self.client.post(ENDPOINT, data=data, 
                                headers=self.token_dict)

    def get(self, param):    
        return self.client.get(ENDPOINT, query_string=param)
        
    def delete(self, param): 
        return self.client.delete(ENDPOINT, query_string=param,
                                  headers=self.token_dict)    
    

class Test_POST(TestDatapoints):

    def test_on_no_auth_token_returns_forbidden_status_error_code(self):
        response = self.client.post('/api/datapoints')
        assert response.status_code == 403
    
    def test_on_new_data_upload_successfull_with_code_200(self):
        upload_json = json.dumps(self.test_data)
        response = self.post(data=upload_json)
        assert response.status_code == 200

    def test_on_existing_data_upload_successfull_with_code_200(self):
        upload_json = json.dumps(self.test_data[0:10])
        response = self.post(data=upload_json)
        # second call
        response = self.post(data=upload_json)
        assert response.status_code == 200

    def test_on_broken_data_upload_returns_error_code(self):
        response = self.post(data="___broken_json_data__")
        assert response.status_code == 400
        

class Test_GET(TestDatapoints):

    
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
    def test_get_on_name_and_freq_returns_list_of_dicts(self):
        response = self.query_on_name_and_freq()
        data = json.loads(response.get_data().decode('utf-8'))
        expected_data = self._subset_test_data('CPI_NONFOOD_rog', 'm')
        assert data == expected_data


    def test_on_name_parameter_not_specified_fails(self):
        params = dict(freq='m', format='json')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 422

    def test_on_freq_parameter_not_specified_fails(self):
        params = dict()
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 422

#FIXME: this should not be a separate testing class
class Test_GET_Errors(TestDatapoints):

    def test_datapoints_empty_params_returns_error(self):
        response = self.client.get('/api/datapoints')
        assert response.status_code == 422

    def test_datapoints_wrong_freq_returns_error(self):
        params = dict(name='CPI_NONFOOD_rog', freq='wrong_freq')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 422

    def test_datapoints_wrong_name_returns_error(self):
        params = dict(name='wrong_name', freq='q')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 422

    def test_datapoints_start_date_in_future_returns_error(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q',
                      start_date='2099-01-01')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 422

    def test_datapoints_end_date_after_start_date_returns_error(self):
        params = dict(name='CPI_NONFOOD_rog', freq='q', start_date='2010-01-01',
                      end_date='2000-01-01')
        response = self.client.get('/api/datapoints', query_string=params)
        assert response.status_code == 422


class Test_DELETE(TestDatapoints):
    """Testing /api/delete"""
    
   
    def test_on_no_auth_token_returns_forbidden_status_code_403(self):
        response = self.client.delete(ENDPOINT,
                                      headers=dict(API_TOKEN='000'))
        assert response.status_code == 403
        
    def test_on_no_data_returns_invalid_entry_error_422(self):
        response = self.delete({})
        assert response.status_code == 422
    
    # FIXME: may parametrise        
    def test_on_name_delete_successfull_200(self):
        param = dict(name="BRENT")
        response = self.delete(param)
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '--maxfail=1'])
    
    v = TestDatapoints()
    v.setUp()
    
    sample = json.dumps(v.test_data[0:10])
    resp = v.client.post('/api/datapoints', data=sample, headers=v.token_dict)
    print(resp)
    
    _name='CPI_NONFOOD_rog'
    _freq='m'
    params = dict(name=_name, freq=_freq)
    resp = v.client.get('/api/info', query_string=params)
    print(resp)

    resp = v.client.delete('/api/datapoints', 
                           query_string={'name':'DRENT'}, 
                           headers=v.token_dict)
    print(resp)

    
    _name='CPI_NONFOOD_rog'
    _freq='m'
    params = dict(name=_name, freq=_freq)
    resp = v.client.get('/api/info', query_string=params)
    print(resp)
