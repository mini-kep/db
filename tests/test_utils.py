import pytest
import datetime

from tests.test_basic import TestCaseBase

import db.api.queries as queries

names = ['CPI_rog', 'EXPORT_GOODS_bln_usd']
not_unique_names = ['CPI_rog', 'EXPORT_GOODS_bln_usd', 'CPI_rog']

csv_rows = [
    ['2016-06-30', 101.2, 67.9],
    ['2016-09-30', 100.7, 70.9],
    ['2016-12-31', 101.3, 82.6],
]


class TestDictionaryRepresentation(TestCaseBase):

    def _get_serialized_query(
        self,
        freq='q',
        names=['CPI_rog', 'EXPORT_GOODS_bln_usd'],
        start_date=None,
        end_date=None
    ):
        import db.api.utils as utils

        query = queries.DatapointOperations\
            .select_frame(freq, names, start_date, end_date)

        return utils.DictionaryRepresentation(query)

    def _get_serialized_query_for_daily_freq(self):
        return self._get_serialized_query(
            freq='d',
            names=['BRENT', 'USDRUR_CB'],
            start_date='2016-06-01',
            end_date='2016-06-07'
        )

    def test_query_serialized_names_returns_correct_list(self):
        query_dict = self._get_serialized_query()
        assert query_dict.names == names

    def test_query_serialized_names_are_unique(self):
        query_dict = self._get_serialized_query(names=not_unique_names)
        assert query_dict.names == sorted(list(set(not_unique_names)))

    def test_names_converted_to_header_returns_valid_string(self):
        query_dict = self._get_serialized_query()
        assert query_dict.header == ',CPI_rog,EXPORT_GOODS_bln_usd'

    def test_csv_rows_iterator_return_valid_lists(self):
        query_dict = self._get_serialized_query()
        rows = query_dict.yield_data_rows()
        for i in range(len(csv_rows)):
            next(rows) == csv_rows[i]

    def test_generated_csv_is_equal_to_expected(self):
        query_dict = self._get_serialized_query()
        query_dict.to_csv == """,CPI_rog,EXPORT_GOODS_bln_usd
                                2016-06-30,101.2,67.9
                                2016-09-30,100.7,70.9
                                2016-12-31,101.3,82.6
                                """
    def test_daily_reports_returns_expected_csv(self):
        query_dict = self._get_serialized_query_for_daily_freq()
        query_dict.to_csv == """,BRENT,USDRUR_CB
                            2016-06-01,48.81,65.9962
                            2016-06-02,49.05,66.6156
                            2016-06-03,48.5,66.7491
                            2016-06-04,,66.8529
                            2016-06-06,48.94,
                            2016-06-07,49.76,65.7894"""


if __name__ == '__main__':
    pytest.main([__file__, '--maxfail=1'])
