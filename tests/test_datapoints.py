import unittest
from db.api.errors import CustomError400
from db.api.views import validate_and_transform_datapoints_params, select_datapoints, _get_datapoints
from datetime import date
from db import create_app, db
from db.api.views import api as api_module
import os
import json


app = create_app('config.TestingConfig')
app.register_blueprint(api_module)

class TestCase(unittest.TestCase):
    def _read_test_data(self):
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(tests_folder, 'test_data.json')) as data_file:
            return data_file.read()

    def _prepare_database(self):
        data = self._read_test_data()
        self.app.post('/api/incoming',
                      data=data,
                      headers=dict(API_TOKEN=app.config['API_TOKEN']))

    def setUp(self):
        db.create_all(app=app)
        self.app = app.test_client()
        self._prepare_database()
        app.app_context().push()

    def tearDown(self):
        db.session.remove()
        db.drop_all(app=app)



class TestValidateAndTransform(TestCase):
    def test_none_params_should_fail(self):
        with self.assertRaises(CustomError400):
            validate_and_transform_datapoints_params(None, None, None, None)

    def test_date_is_transformed_correctly(self):
        _, _, start_date, end_date = validate_and_transform_datapoints_params('m', 'RETAIL_SALES_FOOD_rog', '2015-03-25', '2016-04-01')
        assert start_date == date(year=2015, month=3, day=25)
        assert end_date == date(year=2016, month=4, day=1)

    def test_start_date_greater_than_end_date_should_fail(self):
        with self.assertRaises(CustomError400):
            validate_and_transform_datapoints_params('m', 'RETAIL_SALES_FOOD_rog', '2015-10-25', '2015-04-01')

    def test_invalid_freq_should_fail(self):
        with self.assertRaises(CustomError400):
            validate_and_transform_datapoints_params('o', 'INVESTMENT_rog', None, None)

    def test_invalid_name_should_fail(self):
        with self.assertRaises(CustomError400):
            validate_and_transform_datapoints_params('m', 'BIBA_boba', None, None)


class TestSelectDataPoints(TestCase):
    def test_data_is_fetching(self):
        datapoint = select_datapoints(
            'm', 'CPI_ALCOHOL_rog', date(year=1999, month=1, day=1), date(year=1999, month=2, day=1)
        ).first().serialized
        self.assertEqual(
            datapoint,
            {"date": "1999-01-31", "freq": "m", "name": "CPI_ALCOHOL_rog", "value": 109.7}
        )

    def test_wrong_params_fetch_zero_results(self):
        empty_query = select_datapoints(
            'biba', 'boba',
            date(year=2005, month=1, day=1),
            date(year=2006, month=1, day=1)
        )
        self.assertEqual(
            empty_query.count(),
            0
        )


class TestGetDatapoints(TestCase):
    # actually, _get_datapoints function is tested
    def test_json_output_is_valid_and_correct(self):
        json_string = _get_datapoints('m', 'CPI_ALCOHOL_rog', '1999-01-31', '2000-01-31', 'json').data
        data = json.loads(json_string)
        self.assertEqual(
            data[0],
            {
                "date": "1999-01-31",
                "freq": "m",
                "name": "CPI_ALCOHOL_rog",
                "value": 109.7
            }
        )

    def test_csv_output_is_valid(self):
        csv_bytes = _get_datapoints('m', 'CPI_ALCOHOL_rog', '1999-01-31', '2000-01-31', 'csv').data
        self.assertIn(',CPI_ALCOHOL_rog\\n1999-01-31,109.7', str(csv_bytes))

    def test_invalid_output_format_should_fail(self):
        with self.assertRaises(CustomError400):
            _get_datapoints('m', 'CPI_ALCOHOL_rog', '1999-01-31', '2000-01-31', 'html')


if __name__ == '__main__':
    unittest.main()