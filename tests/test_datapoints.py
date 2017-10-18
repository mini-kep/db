from datetime import date
import datetime
import os
import json

import unittest

from db.api.errors import CustomError400
from db.api.views import select_datapoints, serialise_datapoints
from db import create_app, db
from db.api.views import api as api_module
from db.api.utils import DatapointParameters, to_date
from db.api.models import Datapoint

app = create_app('config.TestingConfig')
app.register_blueprint(api_module)

class TestCase(unittest.TestCase):
    def _read_test_data(self):
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(tests_folder, 'test_data.json')) as data_file:
            return data_file.read()
        
    # NOT TODO: must populate test database without API
    # NOT TODO: must have two test classes - with empty and with full database
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


def days_ahead(k):
    dt = datetime.date.today() + datetime.timedelta(days=k)
    return dt.strftime('%Y-%m-%d')

#Code under test:
#    class DatapointParameters:

class TestDatapointParameters(TestCase):
    
    @staticmethod
    def _make_args(freq, name, start, end):
        return dict(name=name,
                    freq=freq,
                    start_date=start,
                    end_date=end)
    
    def test_none_params_should_fail(self):
        args = self._make_args(None, None, None, None)
        with self.assertRaises(CustomError400):
            DatapointParameters(args)

    def test_date_is_transformed_correctly(self):
        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2015-03-25', '2016-04-01')
        dp = DatapointParameters(args) 
        assert dp.get_start() == date(year=2015, month=3, day=25)
        assert dp.get_end() == date(year=2016, month=4, day=1)

    def test_on_wrong_sequence_of_dates_fails(self):
        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', '2015-10-30', '1999-10-01')
        with self.assertRaises(CustomError400):
             DatapointParameters(args).get_end()

    def test_on_start_in_future_fails(self):
        args = self._make_args('m', 'RETAIL_SALES_FOOD_rog', days_ahead(1), days_ahead(2))
        with self.assertRaises(CustomError400):
             DatapointParameters(args).get_start()

    def test_on_invalid_freq_should_fail(self):
        args = self._make_args('z', 'RETAIL_SALES_FOOD_rog', None, None)
        with self.assertRaises(CustomError400):
             DatapointParameters(args)

    def test_on_invalid_name_should_fail(self):
        args = self._make_args('m', 'BIBA_boba', None, None)
        with self.assertRaises(CustomError400):
             DatapointParameters(args)



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

# CODE UNDER TEST: ------------------------------------------------------------------------
#def serialise_datapoints(data, output_format: str):
#    if output_format == 'csv' or not output_format:
#        csv_str = utils.to_csv([row.serialized for row in data.all()])
#        return Response(response=csv_str, mimetype='text/plain')
#    elif output_format == 'json':
#        return jsonify([row.serialized for row in data.all()])
#    else:
#        raise CustomError400(f"Wrong value for parameter 'format': {output_format}")
# TODO: must generate a small (2-3 elements) *data* of proper type to test csv, json outputs 
# ------------------------------------------------------------------------------------------

#class TestGetDatapoints(TestCase):
#    # actually, _get_datapoints function is tested
#    def test_json_output_is_valid_and_correct(self):
#        json_string = _get_datapoints('m', 'CPI_ALCOHOL_rog', '1999-01-31', '2000-01-31', 'json').data
#        data = json.loads(json_string)
#        self.assertEqual(
#            data[0],
#            {
#                "date": "1999-01-31",
#                "freq": "m",
#                "name": "CPI_ALCOHOL_rog",
#                "value": 109.7
#            }
#        )
#
#    def test_csv_output_is_valid(self):
#        csv_bytes = _get_datapoints('m', 'CPI_ALCOHOL_rog', '1999-01-31', '2000-01-31', 'csv').data
#        self.assertIn(',CPI_ALCOHOL_rog\\n1999-01-31,109.7', str(csv_bytes))
#
#    def test_invalid_output_format_should_fail(self):
#        with self.assertRaises(CustomError400):
#            _get_datapoints('m', 'CPI_ALCOHOL_rog', '1999-01-31', '2000-01-31', 'html')

class TestSerialiseDatapoints(TestCase):
    data_dicts = [{"date": "1999-01-31", "freq": "m", "name": "CPI_ALCOHOL_rog", "value": 109.7},
                  {"date": "1999-01-31", "freq": "m", "name": "CPI_FOOD_rog", "value": 110.4},
                  {"date": "1999-01-31", "freq": "m", "name": "CPI_NONFOOD_rog", "value": 106.2}]

    @property
    def datapoints(self):
        datapoints = []
        for params in self.data_dicts:
            datapoints.append(Datapoint(
                name=params.get('name'),
                freq=params.get('freq'),
                date=to_date(params.get('date')),
                value=params.get('value')
            ))
        return datapoints

    def test_json_serialising_is_valid(self):
        serialised = serialise_datapoints(self.datapoints, 'json').data
        parsed_json = json.loads(serialised)
        self.assertEqual(self.data_dicts, parsed_json)




if __name__ == '__main__':
    unittest.main()
