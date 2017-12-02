import json

import pytest

from tests.test_basic import TestCaseBase


class Test_API_Info(TestCaseBase):
    """Test custom API '/info' finalizer"""

    def query_get_start_and_end_date(self, path):
        return self.client.get(path)

    def get_dates(self):
        data = self._subset_test_data('CPI_NONFOOD_rog', 'm')
        return sorted([row['date'] for row in data])

    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_response_code_200(self):
        response = self.query_get_start_and_end_date(
            'oil/series/CPI_NONFOOD_rog/m/bln_rub/2016/info')
        assert response.status_code == 200

    # NOT TODO: may be parametrised
    def test_get_start_end_date_for_CPI_NONFOOD_rog_returns_proper_dates(self):
        # call
        response = self.query_get_start_and_end_date(
            'oil/series/CPI_NONFOOD_rog/m/bln_rub/2016/info')
        data = response.get_data().decode('utf-8')
        result = json.loads(data)
        # expected
        dates = self.get_dates()
        # check
        assert result['m']['start_date'] == dates[0]
        assert result['m']['latest_date'] == dates[-1]


if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
