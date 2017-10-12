import json
from flask import Blueprint, request, abort, jsonify, current_app, Response
# EP - TO DISCUSS: a) there are several validate functions, rather long import, maybe collect them in some class
#                     for shorter import? eg from utils import Input; Input.validate_freq_exist(freq), etc. 
#                     Input class can be just a collection of classmethods, like in https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/csv2df/runner.py#L82-L112
#                     Another name suggestion for such class is Helper.
# EP - TO DISCUSS: b) validate_and_convert_dates() - maybe split into two, these are different responsibilities
#                     to convert and to check
from utils import to_date, to_csv, validate_freq_exist, validate_name_exist_for_given_freq, validate_and_convert_dates
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
    validate_freq_exist(freq)
    # Validate name exist for given freq
    validate_name_exist_for_given_freq(freq, name)
    # Filter by necessary parameters
    data = Datapoint.query.filter(Datapoint.name == name).filter(Datapoint.freq == freq).order_by(Datapoint.date)
    # Filter by optional parameters
    start_date, end_date = request.args.get('start_date'), request.args.get('end_date')
    # Validate dates
    start_date, end_date = validate_and_convert_dates(start_date, end_date)
    if start_date:
        data = data.filter(Datapoint.date >= start_date)
    if end_date:
        data = data.filter(Datapoint.date <= end_date)
    # Format result to CSV or JSON
    output_format = request.args.get('format')
    # By default return csv
    if output_format == 'csv' or not output_format:
        return Response(response=to_csv([row.serialized for row in data.all()]),
                        mimetype='text/plain')
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
