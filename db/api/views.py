import json
from flask import Blueprint, request, abort, jsonify, current_app, Response

import db.api.utils as utils
from db import db
from db.api.models import Datapoint
from db.api.errors import CustomError400


api = Blueprint('api', __name__, url_prefix='/api')


@api.errorhandler(CustomError400)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def validate_and_transform_datapoints_params(freq, name, start_date_str, end_date_str):
    # Validate freq
    utils.validate_freq_exist(freq)
    # Validate name exist for given freq
    utils.validate_name_exist_for_given_freq(freq, name)
    # init start and end_dates
    start_date, end_date = None, None
    # process start date
    if start_date_str:
        start_date = utils.to_date(start_date_str)
        utils.validate_start_is_not_in_future(start_date)
    # process end date
    if end_date_str:
        end_date = utils.to_date(end_date_str)
        if start_date:
            utils.validate_end_date_after_start_date(start_date, end_date)
    return freq, name, start_date, end_date


def select_datapoints(freq, name, start_date, end_date):
    # Filter by necessary parameters
    data = Datapoint.query.filter_by(name=name, freq=freq).order_by(Datapoint.date)
    if start_date:
        data = data.filter(Datapoint.date >= start_date)
    if end_date:
        data = data.filter(Datapoint.date <= end_date)
    return data


def _get_datapoints(freq, name, start_date_str, end_date_str, output_format):
    transformed_params = validate_and_transform_datapoints_params(freq, name, start_date_str, end_date_str)
    data = select_datapoints(*transformed_params)

    # By default return csv
    if output_format == 'csv' or not output_format:
        csv_str = utils.to_csv([row.serialized for row in data.all()])
        return Response(response=csv_str, mimetype='text/plain')
    elif output_format == 'json':
        return jsonify([row.serialized for row in data.all()])
    # return error if parameter format is different from 'json' or 'csv'
    else:
        raise CustomError400(f"Wrong value for parameter 'format': {output_format}")



@api.route('/datapoints', methods=['GET'])
def get_datapoints():
    name = request.args.get('name')
    freq = request.args.get('freq')
    if not name or not freq:
        raise CustomError400("Following parameters are required: name, freq")
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    output_format = request.args.get('format')
    return _get_datapoints(freq, name, start_date_str, end_date_str, output_format)


@api.route('/incoming', methods=['POST'])
def upload_data():
    # Authorisation
    token_to_check = request.args.get('API_TOKEN') or request.headers.get('API_TOKEN')
    if token_to_check != current_app.config['API_TOKEN']:
        return abort(403)
    # Upload data
    try:
        data = json.loads(request.data)
        for datapoint in data:
            datapoint['date'] = utils.to_date(datapoint['date'])
        db.session.bulk_insert_mappings(Datapoint, data)
    except:
        return abort(400)
    db.session.commit()
    return jsonify({})


@api.route('/names/<freq>', methods=['GET'])
def get_possible_names(freq):
    # Get all names
    if freq == 'all':
        possible_names_values = Datapoint.query.\
            group_by(Datapoint.name).\
            order_by(Datapoint.name).\
            values(Datapoint.name)
    # Get names by freq
    else:
        utils.validate_freq_exist(freq)
        possible_names_values = Datapoint.query.\
            filter(Datapoint.freq==freq).\
            group_by(Datapoint.name). \
            order_by(Datapoint.name). \
            values(Datapoint.name)
    return jsonify([row.name for row in possible_names_values])


@api.route('/info', methods=['GET'])
def get_date_range():
    name = request.args.get('name')
    freq = request.args.get('freq')
    if not name or not freq:
        raise CustomError400("Following parameters are required: name, freq")
    # Validate freq
    utils.validate_freq_exist(freq)
    # Validate name exist for given freq
    utils.validate_name_exist_for_given_freq(freq, name)
    # Extract dates from table
    start_date, end_date = utils.get_first_and_last_date(freq, name)
    return jsonify({'start_date':start_date, 'end_date':end_date})
