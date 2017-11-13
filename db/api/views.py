import json
from flask import Blueprint, request, abort, jsonify, current_app, Response

from db import db
from db.api.errors import CustomError400
from db.api.queries import All, Allowed, DatapointOperations, DateRange
from db.api.parameters import RequestArgs, RequestFrameArgs, SimplifiedArgs

import db.api.utils as utils
import db.helper.label as label


api = Blueprint('api', __name__, url_prefix='/api')


@api.errorhandler(422)
def handle_validation_error(error):
    
    # error 422 is raised by webargs, on two accasions:
    # 1. argument check on input (eg required argument missing)
    #    webarg raises some exception internally
    # 2. argument check inside parser class (eg start date must be before or equal end date)
    #    we raise ArgError(ValidationError)    
    
    # when custom class ArgError is raised we will have 'kwargs.['load']' available 
    view_dict = error.exc.kwargs.get('load', {}) 
    # other validation paths for error 422 in webargs will just have .messages
    view_dict['messages'] = error.exc.messages
    # send combination of the above to user screen
    response = jsonify(view_dict)
    response.status_code = error.exc.status_code
    return response


@api.errorhandler(CustomError400)
def handle_invalid_usage(error):
    """Generate a json object of a custom error"""
    response = jsonify(error.dict)
    response.status_code = error.status_code
    return response


def authorise():
    token_to_check = request.args.get('API_TOKEN') or request.headers.get('API_TOKEN')
    if token_to_check != current_app.config['API_TOKEN']:
        return abort(403)


def no_download(csv_str):
    """Show document in browser, do not start a download dialog."""
    return Response(response=csv_str, mimetype='text/plain')

        
def publish_csv(data):
    csv_str = utils.to_csv([row.serialized for row in data])
    return no_download(csv_str)

        
def publish_json(data):
    return jsonify([row.serialized for row in data])

    
# FIXME: change this to class + restore swagger documentation
# https://github.com/mini-kep/db/issues/69
# http://flask.pocoo.org/docs/0.12/views/
@api.route('/datapoints', methods=['POST', 'GET', 'DELETE'])
def datapoints_endpoint():
    if request.method == 'POST':
       return upload_data()
    elif request.method == 'DELETE':
       return delete_datapoints()
    else:    
       return get_datapoints()
        
def upload_data():
    """
    Upload incoming data to database.
    ---
    tags:
       - datapoints
    parameters:
       - name: API_TOKEN
         in: query
         type: string
         required: true
         description: API key
       - name: data
         in: query
         type: list
         required: true
         description: list of dictionaries to upload, each of dicts is one datapoint obsrevation
    responses:
        403:
            description: Failed to authenticate correctly.
        200:
            description: Returns empty dictionary on success.
    """
    # authorisation
    authorise()
    # upload data
    try:
        data = json.loads(request.data)
        for datapoint in data:
            DatapointOperations.upsert(datapoint)
        db.session.commit()
        return jsonify({})
    except:
        db.session.rollback()
        return abort(400)


def get_datapoints():
    """
    Select and return time series as csv or json
    ---
    tags:
      - datapoints
    parameters:
      - name: name
        in: query
        type: string
        required: true
      - name: freq
        in: query
        type: string
        required: true
        description: a, q, or d
      - name: start_date
        in: query
        type: string
        required: false
      - name: end_date
        in: query
        type: string
        required: false
      - name: format
        in: query
        type: string
        required: false
        description: 'csv'(default) or 'json'
    responses:
        422:
            description: bad arguments, eg start_date > end_date
        200:
            description: sent json or csv
   """
    args = RequestArgs()
    data = DatapointOperations.select(**args.query_param)
    if args.format == 'json':
        return publish_json(data)
    else:
        return publish_csv(data)        

def delete_datapoints():
    """
    Delete datapoints.
    ---
    tags:
        -delete
    parameters:
      - name: name
        in: query
        type: string
        required: false
      - name: freq
        in: query
        type: string
        required: false
        description: a, q, or d
      - name: start_date
        in: query
        type: string
        required: false
      - name: end_date
        in: query
        type: string
        required: false
    responses:
        403:
            description: Failed to authenticate correctly
        400:
            description: Returns {'exit': 0}
            
    """
    authorise()
    args = SimplifiedArgs()
    DatapointOperations.delete(**args.query_param)
    return jsonify({'exit': 0})
    
# end FIXME -------------------------------------------------------------------


# api/frame?freq=a&name=GDP_yoy,CPI_rog&start_date=2013-12-31
@api.route('/frame', methods=['GET'])
def get_dataframe():
    args = RequestFrameArgs()
    param = args.query_param
    if not args.names:
         param['names'] = Allowed.names(args.freq)    
    data = DatapointOperations.select_frame(**param)
    csv_str = utils.CSV_Maker(data).to_csv()
    return no_download(csv_str)


@api.route('/freq', methods=['GET'])
def get_freq():
    return jsonify(All.frequencies())


@api.route('/names', methods=['GET'])
def get_all_variable_names():
    return jsonify(All.names())


@api.route('/names/<freq>', methods=['GET'])
def get_all_variable_names_for_frequency(freq):
    """
    Gets all possible names to a given freq
    ---
    tags:
        - name

    parameters:
      - name: freq
        in: path
        type: string
        required: true
        description: freq to get names for. Choose from [a, d, m, q]

    responses:
        200:
            description: Returns a list of names
    """
    return jsonify(Allowed.names(freq))

# experimental: variable infprmation, response dict may change
  
@api.route('/info', methods=['GET'])
def variable_info():
    """
    Gets a json with start_date and end_date of a give name and frequency pair
    ---
    tags:
        - info

    parameters:
        - name: name
          in: query
          type: string
          required: true
          description: the datapoint name
        - name: freq
          in: query
          type: string
          required: true
          description: frequency from [a, d, m, q]

    responses:
        400:
            description: Request lacks either freq or name argument or start_date greater than end_date.
        200:
            description: Returns a start_date and end_date json.

    """
    name = request.args.get('name')  
    freq = request.args.get('freq')  
    var, unit = label.split_label(name)
    result = dict(name = name,
                  var = {'id': var, 'en': 'reserved', 'ru': 'reserved'},
                  unit = {'id': unit, 'en': 'reserved', 'ru': 'reserved'}
                  )
    dr = DateRange(freq=freq, name=name)
    result[freq] = {'start_date': dr.min, 
                    'latest_date': dr.max,
                    'latest_value': 'reserved'}   
    return jsonify(result)    
