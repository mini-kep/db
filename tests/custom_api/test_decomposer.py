import pytest

import db.custom_api.decomposer as decomposer
from db.api.errors import CustomError400
from tests.test_basic import TestCaseBase


class Test_as_date(TestCaseBase):
    def test_as_date_with_valid_date_success(self):
        assert decomposer.as_date(2010, 5, 25) == '2010-05-25'

    def test_as_date_with_invalid_date_fails(self):
        with pytest.raises(ValueError):
            decomposer.as_date(2010, 0, 0)


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

# # NOT TODO: may parametrise this test


class Test_ListElements_years_handling(TestCaseBase):
    def test_get_years_on_one_year_returns_start_year(self):
        assert decomposer.ListElements(tokens=['2000']).get_years() == (2000, None)

    def test_on_two_years_returns_start_end_years(self):
        assert decomposer.ListElements(tokens=['2005', '2007']).get_years() == \
               (2005, 2007)


class Test_TokensArgs(TestCaseBase):
    @staticmethod
    def _today():
        from datetime import date
        return decomposer.as_date(
            date.today().year, date.today().month, date.today().day)

    def test_init_on_well_formed_args_is_success(self):
        inner_path = 'oil/series/BRENT/m/eop/2015/2017/csv'
        tokens = decomposer.Tokens(inner_path)

        assert tokens.unit is None
        assert tokens.start == '2015-01-01'
        assert tokens.end == '2017-12-31'
        assert tokens.fin == 'csv'
        assert tokens.rate is None
        assert tokens.agg is 'eop'

    def test_init_on_args_with_no_years_is_success(self):
        inner_path = 'oil/series/BRENT/m/eop/csv'
        tokens = decomposer.Tokens(inner_path)

        assert tokens.start is None
        assert tokens.end == self._today()

    def test_init_on_no_args(self):
        inner_path = ''
        tokens = decomposer.Tokens(inner_path)

        assert tokens.unit is None
        assert tokens.start is None
        assert tokens.end == self._today()
        assert tokens.fin is None
        assert tokens.rate is None
        assert tokens.agg is None


# class Test_TokenHelper:

    # def test_get_dates_dict(self, _tokens):
        # dates = custom_api.TokenHelper(tokens=_tokens).get_dates_dict()
        # assert 'start_date' in dates.keys()
        # assert dates['start_date'] == '2000-01-01'

    # def test_fin(self, _tokens):
        # assert custom_api.TokenHelper(tokens=_tokens).fin() == 'csv'

    # def test_fin_actially_pops_element(self):
        # helper = custom_api.TokenHelper(tokens=['csv'])
        # _ = helper.fin()
        # assert helper.tokens == []

    # def test_agg(self, _tokens):
        # assert custom_api.TokenHelper(tokens=_tokens).agg() == 'eop'

    # def test_rate(self, _tokens):
        # assert custom_api.TokenHelper(tokens=_tokens).rate() is None


# class Test_InnerPath:
    # def test_constructor_on_both_rate_and_agg_fails(self):
        # with pytest.raises(CustomError400):
            # custom_api.InnerPath('eop/rog')


# @pytest.mark.parametrize("test_input,expected_dates,expected_unit", [
    #     ('eop/2015/2018/csv', {'start_date': '2015-01-01', 'end_date': '2018-12-31'}, None),
    #     ('eop/2014/2017/csv', {'start_date': '2014-01-01', 'end_date': '2017-12-31'}, None),
    #     ('eop/2010/1970/csv', {'start_date': '2010-01-01', 'end_date': '1970-12-31'}, None),
# ])
# def test_get_dict_on_valid_inner_path(test_input, expected_dates, expected_unit):
    #     path = custom_api.InnerPath(test_input)
    #     assert path.get_dates() == expected_dates
    #     assert path.get_unit() == expected_unit


# class TestCustomGET(TestCaseBase):

    # def test_get_csv_on_valid_params_fetches_data_for_CPI(self):
        # getter = custom_api.CustomGET('ru', 'CPI_rog', 'm', '')
        # api_csv_str = str(getter.get_csv_response().data, 'utf-8')
        # assert api_csv_str

    # def test_get_csv_on_valid_params_fetches_data(self):
        # getter = custom_api.CustomGET('ru', 'USDRUR_CB', 'd', '2016')
        # api_csv_str = str(getter.get_csv_response().data, 'utf-8')
        # assert '2016-06-24,64.3212\n' in api_csv_str

    # def test_get_csv_on_bad_params_should_fail(self):
        # getter = custom_api.CustomGET(domain=None,
                                      # varname='ZZZ',
                                      # freq='d',
                                      # inner_path='')
        # with pytest.raises(CustomError400):
            # _ = getter.get_csv_response()

    # def test_make_name(self):
        # assert custom_api.CustomGET.make_name('varname', 'unit') == 'varname_unit'


class Test_CustomEndPoint_Integration_Test(TestCaseBase):
    def test_CPI_rog_m_is_found_with_code_200(self):
        response = self.client.get('/ru/series/CPI_rog/m')
        assert response.status_code == 200

    @pytest.mark.skip
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
