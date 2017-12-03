import pytest
import requests

from tests.test_basic import TestCaseBase

DESC_URL = 'http://minikep-db.herokuapp.com/api/desc'

sample_post_payload = [
    dict(abbr='test_BRENT', ru='Цена нефти Brent', en='Brent oil price'),
    dict(abbr='test_GDP', ru='Валовый внутренний продукт', en='Gross domestic product'),
    dict(abbr='test_rog', ru='темп роста к пред. периоду', en='rate of growth to previous period'),
    dict(abbr='test_yoy', ru='темп роста за 12 месяцев', en='year-on-year rate of growth')
]


class Test_ApiDesc(TestCaseBase):

    def test_get_without_params_fails(self):
        response = requests.get(DESC_URL)
        assert response.status_code != 200

    @pytest.mark.xfail
    def test_get_GDP_ru_successful_returns_valid_data(self):
        params = dict(abbr='GDP', lang='ru')
        response = requests.get(DESC_URL, params=params)
        data = response.json().decode('utf-8')

        assert response.status_code == 200
        assert data == {'abbr': 'GDP', 'ru': 'Цена нефти Brent'}

    @pytest.mark.xfail
    def test_get_rog_en_successful_returns_valid_data(self):
        params = dict(abbr='GDP', lang='ru')
        response = requests.get(DESC_URL, params=params)
        data = response.json().decode('utf-8')

        assert response.status_code == 200
        assert data == {'abbr': 'rog', 'en': 'rate of growth to previous period'}

    def test_post_without_params_fails(self):
        response = requests.post(DESC_URL)
        assert response.status_code != 200

    @pytest.mark.xfail
    def test_post_with_sample_payload_successful_with_code_200(self):
        response = requests.post(DESC_URL, json=sample_post_payload)
        assert response.status_code == 200

    def test_delete_with_empty_abbr_field_fails(self):
        params = {'abbr': ''}
        response = requests.delete(DESC_URL, params=params)
        assert response.status_code != 200

    @pytest.mark.xfail
    def test_delete_rog_successful_with_code_200(self):
        params = {'abbr': 'rog'}
        response = requests.delete(DESC_URL, params=params)
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])
