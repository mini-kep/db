import json

import pytest

from tests.test_basic import TestCaseBase


class Test_API_Info(TestCaseBase):
    """Test custom API '/info' finalizer"""

    def query_info(self, path):
        return self.client.get(path)

    def get_dates(self, name, freq):
        data = self._subset_test_data(name, freq)
        return sorted([row['date'] for row in data])

    def test_get_info_for_EXPORT_GOODS_bln_usd_monthly_freq_returns_response_code_200(
            self):
        response = self.query_info('ru/series/EXPORT_GOODS_bln_usd/m/info')
        assert response.status_code == 200

    # NOT TODO: may be parametrised
    def test_get_start_end_date_for_EXPORT_GOODS_bln_usd_returns_proper_dates(
            self):
        # call
        response = self.query_info('ru/series/EXPORT_GOODS_bln_usd/m/info')
        data = response.get_data().decode('utf-8')
        result = json.loads(data)
        # expected
        dates = self.get_dates('EXPORT_GOODS_bln_usd', 'm')

        assert result['m']['start_date'] == dates[0]
        assert result['m']['latest_date'] == dates[-1]

    # Tests for other variables may be added,
    # eg: 'oil/series/CPI_NONFOOD_rog/m/bln_rub/2016/info'


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
