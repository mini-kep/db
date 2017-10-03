import requests

POST_URI = 'api/incoming'
BASE_URI = 'api/datapoints'

# for reference
# data = [{
    # 'name': 'BRENT',
    # 'freq': 'm',
    # 'date': '2018-01-01',
    # 'value': 42.0
# }]


#TODO (EP): must change this to actual data, not imaginary, both here and in SPEC.md

class TestPOST():
    # success
    def test_posting_valid_data():
        """Return an empty JSON on success"""
        data = [{ "date": "1999-03-31", "freq": "q", "name": "INVESTMENT_bln_rub", "value": 12345.6 }]
        response = requests.post(POST_URI, data=data)
        assert response.json() == {}

    # fail    
    def test_posting_data_with_empty_name_field():
        """Results in a 400 error"""
        data = [{ "date": "1999-03-31", "freq": "q", "name": "", "value": 12345.6 }]
        response = requests.post(POST_URI, data=data)
        assert response.status_code == 400


# parameter for GET method
payload = {'name': 'BRENT', 'freq': 'd'}   


class Test_GET():
    # happy paths
    def test_request_response_with_valid_params():
        """Completed successfully with OK status code"""
        response = requests.get(BASE_URI, params=payload)
        assert response.ok

    def test_getting_BRENT():
        """Return a list with items that have the requested variable"""
        response = requests.get(BASE_URI, params=payload)
        assert response.json()[0]['name'] == 'BRENT'

    # sad paths
    def test_request_with_empty_name():
        """Return 400 error with empty name parameter"""
        payload = {'name': '', 'freq': 'm'}
        response = requests.get(BASE_URI, params=payload)
        assert response.status_code == 400

    def test_request_with_empty_frequency():
        """Return 400 error with empty freq parameter"""
        payload = {'name': 'BRENT', 'freq': ''}
        response = requests.get(BASE_URI, params=payload)
        assert response.status_code == 400

    def test_getting_data_not_found():
        """Return response with empty json"""
        payload = {'name': 'FOOBAR', 'freq': 'm'}
        response = requests.get(BASE_URI, params=payload)
        assert response.json() == {}
