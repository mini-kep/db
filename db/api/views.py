import json
from flask import Blueprint, request, abort, jsonify, current_app, Response

from db import db
import db.api.utils as utils
import db.api.queries as queries
from db.api.parameters import RequestArgs, RequestFrameArgs, Allowed


api = Blueprint('api', __name__, url_prefix='/api')


# Return validation errors as JSON
@api.errorhandler(422)
def handle_validation_error(err):
    exc = err.exc
    return jsonify({'errors': exc.messages}), 422


@api.route('/incoming', methods=['POST'])
def upload_data():
    # authorisation
    token_to_check = RequestArgs()['API_TOKEN']
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
    args = RequestArgs()
    data = queries.select_datapoints(**args.query_param)
    if args.format == 'json':
        return publish_json(data)
    else:
        return publish_csv(data)        


def no_download(csv_str):
    return Response(response=csv_str, mimetype='text/plain')

        
def publish_csv(data):
    csv_str = utils.to_csv([row.serialized for row in data])
    return no_download(csv_str)

        
def publish_json(data):
    return jsonify([row.serialized for row in data])


@api.route('/frequencies', methods=['GET'])
def get_freq(freq):
    return jsonify(Allowed.frequencies())


@api.route('/names/<freq>', methods=['GET'])
def get_possible_names(freq):
    return jsonify(Allowed.names(freq))


@api.route('/info', methods=['GET'])
def get_date_range():
    args = RequestArgs()    
    dr = queries.DataRange(freq=args.freq, name=args.name)
    result = dict(start_date = dr.min, end_date = dr.max) 
    return jsonify(result)

# api/dataframe?freq=a&name=GDP_yoy,CPI_rog&start_date=2013-12-31
@api.route('/dataframe', methods=['GET'])
def get_dataframe():
    args = RequestFrameArgs()
    param = args.query_param
    if not args.names:
         param['names'] = Allowed.names(args.freq)    
    data = queries.select_dataframe(**param)
    csv_str = utils.dataframe_to_csv(data, param['names'])
    return no_download(csv_str)

