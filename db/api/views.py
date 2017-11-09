import json
from flask import Blueprint, request, abort, jsonify, current_app, Response

from db import db
import db.api.utils as utils
from db.api.errors import CustomError400
import db.api.queries as queries


api = Blueprint('api', __name__, url_prefix='/api')


@api.errorhandler(CustomError400)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api.route('/incoming', methods=['POST'])
def upload_data():
    # authorisation
    token_to_check = request.args.get('API_TOKEN') or request.headers.get('API_TOKEN')
    if token_to_check != current_app.config['API_TOKEN']:
        return abort(403)

    # upload data
    try:
        data = json.loads(request.data)
        for datapoint in data:
            queries.upsert(datapoint)
        db.session.commit()
        return jsonify({})
    except:
        db.session.rollback()
        return abort(400)


@api.route('/datapoints', methods=['GET'])
def get_datapoints():    
    params = utils.DatapointParameters(request.args).get()
    data = queries.select_datapoints(**params)
    fmt = request.args.get('format')
    return get_datapoints_response(data, fmt)

def get_datapoints_response(data, output_format: str):
    if output_format == 'csv' or not output_format:
        csv_str = utils.to_csv([row.serialized for row in data])
        return Response(response=csv_str, mimetype='text/plain')
    elif output_format == 'json':
        return jsonify([row.serialized for row in data])
    else:
        msg = (f"Wrong value for parameter 'format': <{output_format}>."
                "\n'csv' (default) or 'json' expected")
        raise CustomError400(msg)


@api.route('/names/<freq>', methods=['GET'])
def get_possible_names(freq):
    possible_names = queries.possible_names_values(freq)
    return jsonify(possible_names)


@api.route('/info', methods=['GET'])
def get_date_range():
    dp = utils.DatapointParameters(request.args)
    result = dict(start_date = dp.get_min_date(), 
                  end_date = dp.get_max_date()) 
    return jsonify(result)


# api/dataframe?freq=a&name=GDP_yoy,CPI_rog&start_date=2013-12-31
@api.route('/dataframe', methods=['GET'])
def get_dataframe():
    params = utils.DataframeParameters(request.args).get()
    if params.get('names') is None:
        # if no name is given, acts like get_possible_names
        possible_names = queries.possible_names_values(params['freq'])
        csv_names = ','.join(possible_names) + '\n'
        return Response(response=csv_names, mimetype='text/plain')
    data = queries.select_dataframe(**params)
    csv_str = utils.dataframe_to_csv(data, params.get('names'))
    return Response(response=csv_str, mimetype='text/plain')