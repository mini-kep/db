import pytest

import db.custom_api.decomposer as decomposer
from db.api.errors import CustomError400
from tests.test_basic import TestCaseBase


class Test_as_date(TestCaseBase):
    @staticmethod
    def _as_date(year, month, day):
        return decomposer.as_date(year, month, day)

    def test_as_date_with_valid_date_success(self):
        assert self._as_date(2010, 5, 25) == '2010-05-25'

    def test_as_date_with_invalid_date_fails(self):
        with pytest.raises(ValueError):
            self._as_date(2010, 0, 0)


class Test_validate_frequency(TestCaseBase):
    @staticmethod
    def _validate_frequency(freq):
        return decomposer.validate_frequency(freq)

    def test_validate_frequency_with_valid_param_is_ok(self):
        self._validate_frequency('q')

    def test_validate_frequency_with_invalid_param_should_fail(self):
        with pytest.raises(CustomError400):
            self._validate_frequency('z')

    def test_validate_frequency_with_empty_string_param_should_fail(self):
        with pytest.raises(CustomError400):
            self._validate_frequency('')


class Test_validate_rate_and_agg(TestCaseBase):
    @staticmethod
    def _validate_rate_and_agg(rate, agg):
        return decomposer.validate_rate_and_agg(rate, agg)

    def test_constructor_on_both_rate_and_agg_is_ok(self):
        self._validate_rate_and_agg('r', agg=None)

    def test_constructor_on_both_rate_and_agg_fails(self):
        with pytest.raises(CustomError400):
            self._validate_rate_and_agg('r', 'a')


@pytest.mark.parametrize('elements, expected_years', [
    (['eop', '2000', 'csv'], (2000, None)),
    (['avg', '1990', '2001', 'csv'], (1990, 2001)),
    (['eop', 'csv'], (None, None))
])
def test_list_elements_years_handling(elements, expected_years):
    list_elements = decomposer.ListElements(elements)
    result_years = list_elements.get_years()
    assert result_years == expected_years


class Test_TokensArgs(TestCaseBase):
    @staticmethod
    def _today():
        from datetime import date
        return decomposer.as_date(
            date.today().year, date.today().month, date.today().day)

    def test_init_on_well_formed_inner_path_is_success(self):
        tokens = decomposer.Tokens(
            inner_path='oil/series/BRENT/m/eop/2015/2017/csv')

        assert tokens.unit is None
        assert tokens.start == '2015-01-01'
        assert tokens.end == '2017-12-31'
        assert tokens.fin == 'csv'
        assert tokens.rate is None
        assert tokens.agg is 'eop'

    def test_init_on_inner_path_with_no_years_is_success(self):
        tokens = decomposer.Tokens(inner_path='oil/series/BRENT/m/eop/csv')

        assert tokens.start is None
        assert tokens.end == self._today()

    def test_init_on_empty_inner_path(self):
        tokens = decomposer.Tokens(inner_path='')

        assert tokens.unit is None
        assert tokens.start is None
        assert tokens.end == self._today()
        assert tokens.fin is None
        assert tokens.rate is None
        assert tokens.agg is None


class Test_Indicator(TestCaseBase):
    failing_constructor_args = dict(
        domain='ru',
        varname='CPI_rog',
        freq='a',
        inner_path='eop/rog/2015/2018/csv'
    )

    def test_constructor_with_both_rate_and_agg_fails(self):
        with pytest.raises(CustomError400):
            decomposer.Indicator(**self.failing_constructor_args)


@pytest.mark.parametrize('test_input, expected_dates', [
    ('eop/2015/2018/csv', {'start': '2015-01-01', 'end': '2018-12-31'}),
    ('eop/2014/2017/csv', {'start': '2014-01-01', 'end': '2017-12-31'}),
    ('eop/2010/1970/csv', {'start': '2010-01-01', 'end': '1970-12-31'}),
])
def test_tokens_dates_on_valid_inner_path(test_input, expected_dates):
    tokens = decomposer.Tokens(test_input)
    assert tokens.start == expected_dates['start']
    assert tokens.end == expected_dates['end']


class Test_CustomEndPoint_Integration_Test(TestCaseBase):
    def test_CPI_rog_m_is_found_with_code_200(self):
        response = self.client.get('/ru/series/CPI_rog/m')
        assert response.status_code == 200

    @pytest.mark.webtest
    def test_CPI_rog_m_is_found_with_code_200_on_outer_server(self):
        import requests
        r = requests.get('http://minikep-db.herokuapp.com/ru/series/CPI_rog/m')
        assert r.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])
    t = Test_CustomEndPoint_Integration_Test()
    t.setUp()
    r = t.client.get('/ru/series/CPI_rog/m')
    print(r.data)
