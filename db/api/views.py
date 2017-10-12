import json
from flask import Blueprint, request, abort, jsonify, current_app, Response

import utils
from utils import to_date, to_csv
from db import db
from db.api.models import Datapoint
from db.api.errors import Custom_error_code_400


api = Blueprint('api', __name__, url_prefix='/api')


@api.errorhandler(Custom_error_code_400)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api.route('/datapoints', methods=['GET'])
def get_datapoints():
    try:
        name = request.args['name']
        freq = request.args['freq']
    except:
        raise Custom_error_code_400("Following parameters are required: name, freq")        
    # Validate freq
    utils.validate_freq_exist(freq)
    # Validate name exist for given freq
    utils.validate_name_exist_for_given_freq(freq, name)
    # Filter by necessary parameters
    data = Datapoint.query.filter(Datapoint.name == name).filter(Datapoint.freq == freq).order_by(Datapoint.date)
    # init start and end_dates
    start_date, end_date = None, None
    # get optional parameters as strings 
    start_date_str = request.args.get('start_date')  
    end_date_str = request.args.get('end_date')  
    # process start date
    if start_date_str:        
        start_date = to_date(start_date_str)
        utils.validate_start_is_not_in_future(start_date)
        data = data.filter(Datapoint.date >= start_date)
    # process end date
    if end_date_str:
        end_date = to_date(end_date_str)
        if start_date:
             utils.validate_end_date_after_start_date(start_date, end_date)
        data = data.filter(Datapoint.date <= end_date)
    # Format result to CSV or JSON
    output_format = request.args.get('format')
    # By default return csv
    if output_format == 'csv' or not output_format:
        csv_str = to_csv([row.serialized for row in data.all()])
        return Response(response=csv_str, mimetype='text/plain')
    elif output_format == 'json':
        return jsonify([row.serialized for row in data.all()])
    # return error if parameter format is different from 'json' or 'csv'
    else:
        raise Custom_error_code_400(f"Wrong value for parameter 'format': {output_format}")


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
            datapoint['date'] = to_date(datapoint['date'])
        db.session.bulk_insert_mappings(Datapoint, data)
    except:
        return abort(400)
    db.session.commit()
    return jsonify({})

