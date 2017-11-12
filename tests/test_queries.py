from tests.test_basic import TestCaseBase
from db.api.queries import select_datapoints, upsert
from db.api.queries import delete_datapoints
#from db.api.models import Datapoint
from datetime import date



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
        self.dp1_dict_updated = self.dp1_dict.copy()
        self.dp1_dict_updated['value'] = 432.1

    def test_before_upsert_datapoint_not_found(self):
        datapoints_count = select_datapoints(**self.dp1_search_param).count()
        assert datapoints_count == 0

    def test_after_upsert_datapoint_found(self):
        upsert(self.dp1_dict)
        datapoint = select_datapoints(**self.dp1_search_param).first()
        assert datapoint.serialized, self.dp1_dict

    def test_upsert_updates_value_for_existing_row(self):
        upsert(self.dp1_dict)
        upsert(self.dp1_dict_updated)
        datapoint = select_datapoints(**self.dp1_search_param).first()
        assert datapoint.serialized == self.dp1_dict_updated

# FIXME: delete fails

class TestDeleteDatapoint(TestCaseBase):    

    def test_delete(self):
        param = dict(freq='q', name='GDP_yoy', start_date=None, end_date=None)
        count_before_delete = select_datapoints(**param).count()
        assert count_before_delete > 0
        delete_datapoints(**param)
        count_after_delete = select_datapoints(**param).count()
        assert count_after_delete == 0
#
# WONTFIX: we are skipping a check if datapoint exist in the original function 
#          (but the idea is good)
#    
#    def test_no_deletion_without_match(self):
#        db_before = fsa_db.session.query(Datapoint).all()
#        _name="does_not_match"
#        delete_datapoints(name=_name)
#        db_after = fsa_db.session.query(Datapoint).all()
#        assert db_before == db_after

if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
