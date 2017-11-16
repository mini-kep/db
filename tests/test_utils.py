import unittest

from db.api import queries
from db.api.utils import DictionaryRepresentation
from tests.test_basic import TestCaseBase


class Test_DictionaryRepresentation(TestCaseBase):
    def test_header_property_is_string(self):
        names = ['CPI_rog', 'EXPORT_GOODS_bln_usd']
        sample_query = queries.DatapointOperations.select_frame('q', names, None, None)
        m = DictionaryRepresentation(sample_query)
        assert m.header == ',CPI_rog,EXPORT_GOODS_bln_usd'

    def test_to_csv_with_quarterly_frequency_is_csv(self):
        names = ['CPI_rog', 'EXPORT_GOODS_bln_usd']
        sample_query = queries.DatapointOperations.select_frame('q', names, None, None)
        m = DictionaryRepresentation(sample_query)

        assert m.to_csv() == ",CPI_rog,EXPORT_GOODS_bln_usd\n" \
                             "2016-06-30,101.2,67.9\n" \
                             "2016-09-30,100.7,70.9\n" \
                             "2016-12-31,101.3,82.6\n"

    def test_yield_data_rows_with_daily_frequency_for_period(self):
        names = ['BRENT', 'USDRUR_CB']
        sample_query = queries.DatapointOperations.select_frame('d', names, '2016-06-01',
                                                                '2016-06-07')
        m = DictionaryRepresentation(sample_query)
        rows = m.yield_data_rows()

        assert next(rows) == ['2016-06-01', 48.81, 65.9962]
        assert next(rows) == ['2016-06-02', 49.05, 66.6156]
        assert next(rows) == ['2016-06-03', 48.5, 66.7491]
        assert next(rows) == ['2016-06-04', '', 66.8529]
        assert next(rows) == ['2016-06-06', 48.94, '']
        assert next(rows) == ['2016-06-07', 49.76, 65.7894]


if __name__ == '__main__':
    unittest.main()
