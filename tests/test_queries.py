import unittest
from tests.test_basic import TestCaseBase
from db.api.queries import select_datapoints, upsert
from datetime import date
import copy


class TestSelectDataPoints(TestCaseBase):

    def test_data_is_fetching(self):
        params = dict(freq='m',
                      name='CPI_ALCOHOL_rog',
                      start_date=date(year=2016, month=6, day=1),
                      end_date =date(year=2016, month=7, day=1))
        datapoint = select_datapoints(**params).first()
        self.assertEqual(
            datapoint.serialized,
            {"date": "2016-06-30", "freq": "m", "name": "CPI_ALCOHOL_rog", "value": 100.6}
        )

    def test_wrong_params_fetch_zero_results(self):
        params = dict(
            freq='biba',
            name='boba',
            start_date=date(year=2005, month=1, day=1),
            end_date=date(year=2006, month=1, day=1)
        )
        number_of_results = select_datapoints(**params).count()
        self.assertEqual(number_of_results, 0)


class TestUpsertDatapoint(TestCaseBase):

    def setUp(self):
        super().setUp()
        self.dp1_dict = dict(date="2016-04-21", freq='q', name="CPI_rog", value=123.4)
        self.dp1_search_param = dict(freq=self.dp1_dict['freq'],
                                     name=self.dp1_dict['name'],
                                     start_date=self.dp1_dict['date'],
                                     end_date=self.dp1_dict['date'])
        # new value
        self.dp1_dict_updated = copy.copy(self.dp1_dict)
        self.dp1_dict_updated['value'] = 234.5        

    def test_before_upsert_datapoint_not_found(self):
        datapoints_count = select_datapoints(**self.dp1_search_param).count()
        self.assertEqual(datapoints_count, 0)

    def test_after_upsert_datapoint_found(self):
        upsert(self.dp1_dict)
        datapoint = select_datapoints(**self.dp1_search_param).first()
        self.assertEqual(datapoint.serialized, self.dp1_dict)

    def test_upsert_updates_value_for_existing_row(self):        
        upsert(self.dp1_dict)
        upsert(self.dp1_dict_updated)
        datapoint = select_datapoints(**self.dp1_search_param).first()
        self.assertEqual(datapoint.serialized, self.dp1_dict_updated)

if __name__ == '__main__':
    unittest.main()
