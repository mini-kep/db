import json
from flask import Blueprint, request, abort, jsonify, current_app, Response

from db import db
import db.api.utils as utils
from db.api.models import Datapoint
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
    # FIXME: refactor, maybe use finally + separate function to write to db
    
    # upload data
    try:
        data = json.loads(request.data)
        for datapoint in data:
            # FIXME: move upsert function to queries.py
            existing_datapoint = Datapoint.query.\
                filter(Datapoint.freq==datapoint['freq']).\
                filter(Datapoint.name==datapoint['name']).\
                filter(Datapoint.date==datapoint['date']).\
                first()
            if existing_datapoint:
                existing_datapoint.value = datapoint['value']
            else:
                db.session.add(Datapoint(**datapoint))
            # ----------------------------------------------------   
    except:
        return abort(400)
    db.session.commit()
    
    # ------------------------------------ 
    return jsonify({})


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
