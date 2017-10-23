import pytest
import db.custom_api.custom_api as custom_api
from db.api.errors import CustomError400
from tests.test_basic import TestCaseBase

class Test_make_freq:
    def test_make_freq_with_valid_param_is_ok(self):
        assert custom_api.make_freq('q') == 'q'

    def test_make_freq_with_invalid_param_should_fail(self):
        with pytest.raises(CustomError400):
            custom_api.make_freq('z')

    def test_make_freq_with_empty_string_param_should_fail(self):
        with pytest.raises(CustomError400):
            custom_api.make_freq('')


def test_custom_error_is_initable():
    assert CustomError400(message='text').to_dict() == \
        dict(message='text')


@pytest.fixture
def _tokens():
    return ['eop', '2000', 'csv']

# NOT TODO: may parametrise this test


class Test_TokenHelper_year_handling:
    def test_years(self, _tokens):
        assert custom_api.TokenHelper(tokens=['2000'])._find_years() == \
            ('2000', None)

    def test_on_two_years(self):
        assert custom_api.TokenHelper(
            tokens=[
                '2005',
                '2007'])._find_years() == (
            '2005',
            '2007')


class Test_TokenHelper:

    def test_get_dates_dict(self, _tokens):
        dates = custom_api.TokenHelper(tokens=_tokens).get_dates_dict()
        assert 'start_date' in dates.keys()
        assert dates['start_date'] == '2000-01-01'

    def test_fin(self, _tokens):
        assert custom_api.TokenHelper(tokens=_tokens).fin() == 'csv'

    def test_fin_actially_pops_element(self):
        helper = custom_api.TokenHelper(tokens=['csv'])
        _ = helper.fin()
        assert helper.tokens == []

    def test_agg(self, _tokens):
        assert custom_api.TokenHelper(tokens=_tokens).agg() == 'eop'

    def test_rate(self, _tokens):
        assert custom_api.TokenHelper(tokens=_tokens).rate() is None


class Test_as_date(object):
    def test_as_date_with_valid_date(self):
        as_date = custom_api.TokenHelper._as_date('2010', 5, 25)
        assert as_date == '2010-05-25'

    def test_as_date_with_invalid_date(self):
        with pytest.raises(ValueError):
            custom_api.TokenHelper._as_date('2010', 0, 0)


class Test_InnerPath:
    def test_get_dict_on_valid_inner_path(self):
        path = custom_api.InnerPath('eop/2015/2018/csv')
        assert path.get_dict() == {
            'start_date': '2015-01-01',
            'end_date': '2018-12-31',
            'fin': 'csv',
            'rate': None,
            'agg': 'eop',
            'unit': None
        }

    def test_constructor_on_both_rate_and_agg_fails(self):
        with pytest.raises(CustomError400):
            custom_api.InnerPath('eop/rog')


class TestCustomGET(TestCaseBase):
    def setUp(self):
        self.prepare_app()
        self.prepare_db()
        self.mount_blueprint()

    def test_get_csv_on_valid_params_fetches_data(self):
        getter = custom_api.CustomGET('ru', 'USDRUR_CB', 'd', '2016')
        api_csv_str = str(getter.get_csv_response().data, 'utf-8')
        assert '2016-06-24,64.3212\n' in api_csv_str

    def test_get_csv_on_bad_params_should_fail(self):
        getter = custom_api.CustomGET(domain=None,
                                      varname='ZZZ',
                                      freq='d',
                                      inner_path='')
        with pytest.raises(CustomError400):
            _ = getter.get_csv_response()


if __name__ == '__main__':
    pytest.main([__file__])
