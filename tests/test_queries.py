import unittest
from tests.test_basic import TestCaseBase
from db.api.queries import select_datapoints, upsert
from datetime import date


class TestSelectDataPoints(TestCaseBase):
    def setUp(self):
        self.prepare_app()
        self.prepare_db()
        self.mount_blueprint()

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
        super(TestUpsertDatapoint, self).setUp()
        self.dp1_raw = dict(date="2016-04-21", freq='q', name="CPI_rog", value=123.4)
        self.dp1_params = dict(freq=self.dp1_raw['freq'],
                               name=self.dp1_raw['name'],
                               start_date=self.dp1_raw['date'],
                               end_date=self.dp1_raw['date'])

    def test_before_upsert_datapoint_not_found(self):
        datapoints_count = select_datapoints(**self.dp1_params).count()
        self.assertEqual(datapoints_count, 0)

    def test_after_upsert_datapoint_found(self):
        upsert(self.dp1_raw)
        datapoint = select_datapoints(**self.dp1_params).first()
        self.assertEqual(datapoint.serialized, self.dp1_raw)

    def test_upsert_updates_value_for_existing_row(self):
        upsert(self.dp1_raw)
        dp1_updated_value = self.dp1_raw['value'] + 4.56
        dp1_raw_with_new_value = {k: v if k != "value" else dp1_updated_value for k, v in self.dp1_raw.items()}
        upsert(dp1_raw_with_new_value)
        datapoint = select_datapoints(**self.dp1_params).first()
        self.assertEqual(datapoint.value, dp1_updated_value)


if __name__ == '__main__':
    unittest.main()
