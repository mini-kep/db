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

    def _get_serialized_query(self, names):
        import db.api.utils as utils
        query = queries.DatapointOperations.select_frame('q', names, None, None)
        return utils.DictionaryRepresentation(query)

    def test_query_serialized_names_is_correct(self):
        query_dict = self._get_serialized_query(names)
        assert query_dict.names == names

    def test_query_serialized_names_are_unique(self):
        query_dict = self._get_serialized_query(not_unique_names)
        assert query_dict.names == sorted(list(set(not_unique_names)))

    def test_are_names_converted_to_header_well(self):
        query_dict = self._get_serialized_query(names)
        assert query_dict.header == ',CPI_rog,EXPORT_GOODS_bln_usd'

    def test_csv_rows_iteration_works(self):
        query_dict = self._get_serialized_query(names)
        rows = query_dict.yield_data_rows()
        for i in range(len(csv_rows)):
            next(rows) == csv_rows[i]

    def test_generated_csv_is_ok(self):
        query_dict = self._get_serialized_query(names)
        query_dict.to_csv == """,CPI_rog,EXPORT_GOODS_bln_usd
                                2016-06-30,101.2,67.9
                                2016-09-30,100.7,70.9
                                2016-12-31,101.3,82.6
                                """


if __name__ == '__main__':
    pytest.main([__file__, '--maxfail=1'])
