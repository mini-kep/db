"""
# TODO: need tests for 'api/desc' post, get, delete methods using `requests` lib and base url for web endpoint


#GET api/desc?abbr=GDP

#Returns:
#   {'abbr':'GDP', 'ru':'Цена нефти Brent', 'en':'Brent oil price'}

#GET api/desc?abbr=rog

#Returns:
#    {unit:'rog', en:'rate of growth to previous period', ru='темп роста к пред. периоду'}


#POST api/desc

#Payload:
#[dict(abbr='BRENT', ru='Цена нефти Brent', en='Brent oil price')
#dict(abbr='GDP', ru='Валовый внутренний продукт', en='Gross domestic product')
#dict(abbr='rog', ru='темп роста к пред. периоду', en='rate of growth to previous period')
#dict(abbr='yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')]

#DELETE api/desc?abbr=rog
#DELETE api/desc?abbr=BRENT

"""
import pytest
import requests

DESC_URL = 'http://minikep-db.herokuapp.com/api/desc'

sample_post_payload = [
    dict(abbr='test_BRENT', ru='Цена нефти Brent', en='Brent oil price'),
    dict(abbr='test_GDP', ru='Валовый внутренний продукт', en='Gross domestic product'),
    dict(abbr='test_rog', ru='темп роста к пред. периоду', en='rate of growth to previous period'),
    dict(abbr='test_yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')
]


class Test_api_desc_GET_method():

    def test_get_without_params_fails(self):
        response = requests.get(DESC_URL)
        assert response.status_code != 200

    @pytest.mark.xfail
    def test_get_GDP_ru_successful_returns_valid_data(self):
        params = dict(abbr='GDP')
        response = requests.get(DESC_URL, params=params)
        data = response.json().decode('utf-8')

        assert response.status_code == 200
        assert data == {'abbr': 'GDP', 'ru': 'Цена нефти Brent', 'en': 'Brent oil price'}

    @pytest.mark.xfail
    def test_get_rog_en_successful_returns_valid_data(self):
        params = dict(abbr='GDP')
        response = requests.get(DESC_URL, params=params)
        data = response.json().decode('utf-8')

        assert response.status_code == 200
        assert data == {'unit': 'rog', 'en': 'rate of growth to previous period',
                        'ru': 'темп роста к пред. периоду'}

class Test_api_desc_POST_method():        
        
    def test_post_without_params_fails(self):
        response = requests.post(DESC_URL)
        assert response.status_code != 200

    @pytest.mark.xfail
    def test_post_with_sample_payload_successful_with_code_200(self):
        # FIXME: not sure this is a valid json
        response = requests.post(DESC_URL, json=sample_post_payload)
        assert response.status_code == 200

        
class Test_api_desc_DELETE_method():                
        
    def test_delete_with_empty_abbr_field_fails(self):
        params = {'abbr': ''}
        response = requests.delete(DESC_URL, params=params)
        assert response.status_code != 200

    @pytest.mark.xfail
    def test_delete_rog_successful_with_code_200(self):
        params = {'abbr': 'rog'}
        response = requests.delete(DESC_URL, params=params)
        assert response.status_code == 200

if __name__ == '__main__': # pragma no cover
    pytest.main([__file__])
    
    
# import pytest
# import requests

# APP_URL = 'http://minikep-db.herokuapp.com'
# API_DESC_URL = f'{APP_URL}/api/desc'


# # GET api/desc?head=GDP

# # Returns:
# #   {'head':'GDP', 'ru':'Цена нефти Brent'}  on head
# #   All descriptions (head and unit) without parameter

# # GET api/desc?unit=rog&lang=en

# # Returns:
# #    {unit:'rog', en:'rate of growth to previous period'}
# #    All descriptions (head and unit) without parameter

# # POST api/desc

# # Payload:
# # [dict(head='BRENT', ru='Цена нефти Brent', en='Brent oil price')
# # dict(head='GDP', ru='Валовый внутренний продукт', en='Gross domestic product')
# # dict(unit='rog', ru='темп роста к пред. периоду', en='rate of growth to previous period')
# # dict(unit='yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')]

# # DELETE api/desc?unit=rog
# # DELETE api/desc?head=BRENT

# sample_post_payload = [
    # dict(head='test_BRENT', ru='Цена нефти Brent', en='Brent oil price'),
    # dict(head='test_GDP', ru='Валовый внутренний продукт', en='Gross domestic product'),
    # dict(unit='test_rog', ru='темп роста к пред. периоду', en='rate of growth to previous period'),
    # dict(unit='test_yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')
# ]

# @pytest.mark.webtest
# class Test_ApiDesc:
    # def teardown(self):
        # pass

    # def test_get_without_params_should_fail(self):
        # response = requests.get(API_DESC_URL)
        # assert response.status_code != 200

    # def test_post_with_valid_params_is_ok(self):
        # response = requests.post(API_DESC_URL, json=sample_post_payload)
        # assert response.status_code == 200

    # def test_posting_dublicate_data_should_fail(self):
        # response = requests.post(API_DESC_URL, json=sample_post_payload)
        # assert response.status_code != 200

    # def test_getting_posted_data_is_ok(self):
        # for desc in sample_post_payload:
            # response = requests.get(API_DESC_URL, params={
                # 'head': desc.get('head'),
                # 'unit': desc.get('unit')
            # })
            # assert desc == response.json()

    # def test_deleting_posted_data_is_ok(self):
        # for desc in sample_post_payload:
            # response = requests.delete(API_DESC_URL, params={
                # 'head': desc.get('head'),
                # 'unit': desc.get('unit')
            # })
# assert response.status_code == 200    
    
    
