import db.api.utils as utils
from tests.test_basic import TestCaseBase
import db.api.queries as queries

param1 = dict(freq='q', names=['CPI_rog', 'EXPORT_GOODS_bln_usd'],
              start_date = '2016-06-30', end_date = '2016-12-31')

#must extract:
# ,CPI_rog,EXPORT_GOODS_bln_usd
# 2016-06-30,101.2,67.9
# 2016-09-30,100.7,70.9
# 2016-12-31,101.3,82.6

param2 = dict(freq='d', names=['BRENT', 'USDRUR_CB'],
              start_date='2016-06-01', end_date='2016-06-07')

           
class Test_DictionaryRepresentation(TestCaseBase):

    def make(self, freq, names, start_date, end_date):
        query = queries.DatapointOperations \
                       .select_frame(freq, names, start_date, end_date)
        return utils.DictionaryRepresentation(query)

    def test_names_propery_on_valid_args_returns_names_parameter(self):
        assert self.make(**param1).names == ['CPI_rog', 'EXPORT_GOODS_bln_usd']
        assert self.make(**param2).names == ['BRENT', 'USDRUR_CB']
 
    def test_headers_property_on_valid_args_returns_string(self):
        assert self.make(**param1).header == ',CPI_rog,EXPORT_GOODS_bln_usd'
        assert self.make(**param2).header == ',BRENT,USDRUR_CB'        

    def test_yield_data_rows_yields_lists_of_strings(self):
        rows = self.make(**param1).yield_data_rows()
        next(rows) == ['2016-06-30', 101.2, 67.9]
        next(rows) == ['2016-09-30', 100.7, 70.9]
        next(rows) == ['2016-12-31', 101.3, 82.6]
 
    def test_to_csv_on_param1_equals_string(self):
        s = self.make(**param1).to_csv()
        assert ',CPI_rog,EXPORT_GOODS_bln_usd' in s
        assert '2016-06-30,101.2,67.9' in s
        assert '2016-09-30,100.7,70.9' in s
        assert '2016-12-31,101.3,82.6' in s
        # NOT TODO: can also pop from string        
        
    def test_to_csv_on_param2_equals_string(self):
        _x = self.make(**param2)
        # EP: testing like below is risky as strign constant is unstable
        # - you may be getting errors on little unprinted symbol
        assert _x.to_csv() == """,BRENT,USDRUR_CB
2016-06-01,48.81,65.9962
2016-06-02,49.05,66.6156
2016-06-03,48.5,66.7491
2016-06-04,,66.8529
2016-06-06,48.94,
2016-06-07,49.76,65.7894
"""

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '--maxfail=1'])
    z = Test_DictionaryRepresentation()
    z.setUp()
    a = z.make(**param1).to_csv()