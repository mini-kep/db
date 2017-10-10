import json
from flask import Blueprint, request, abort, jsonify, current_app
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
    # Filter by necessary parameters
    data = Datapoint.query.filter(Datapoint.name == name).filter(Datapoint.freq == freq).order_by(Datapoint.date)
    # Filter by optional parameters
    start_date, end_date = request.args.get('start_date'), request.args.get('end_date')
    if start_date:
        data = data.filter(Datapoint.date >= to_date(start_date))
    if end_date:
        data = data.filter(Datapoint.date <= to_date(end_date))
    # Format result to CSV or JSON
    output_format = request.args.get('format')
    # By default return json
    if output_format == 'json' or not output_format:
        return jsonify([row.serialize for row in data.all()])
    elif output_format == 'csv':
        return to_csv([row.serialize for row in data.all()])
    # IF parameter format is different from 'json' or 'csv' - return error
    else:
        raise Custom_error_code_400(f"Wrong value for parameter 'format': {output_format}")


@api.route('/incoming', methods=['POST'])
def upload_data():
    #Auth
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
