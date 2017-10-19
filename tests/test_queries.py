import unittest
from tests.test_basic import TestCaseBase
from db.api.queries import select_datapoints
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


if __name__ == '__main__':
    unittest.main()
