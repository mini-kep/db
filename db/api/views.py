import json
from flask import Blueprint, request, abort, jsonify, current_app, Response
from db import db
import db.api.utils as utils
import db.api.queries as queries
from db.api.parameters import RequestArgs, RequestFrameArgs, Allowed


api = Blueprint('api', __name__, url_prefix='/api')

# FIXME: possibly shuts down validation error messages

#<<<<<<< api-dataframe
# Return validation errors as JSON
#@api.errorhandler(422)
#def handle_validation_error(err):
#    exc = err.exc
#    return jsonify({'errors': exc.messages}), 422

@api.errorhandler(CustomError400)
def handle_invalid_usage(error):
    """
    Generate a json object of a custom error
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api.route('/datapoints', methods=['POST'])
def upload_data():
"""
    Upload data to database
    This endpoint is not used please use /datapoints endpoint
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
         description: list of datpoints to upload
    responses:
        403:
            description: Failed to authenticate correctly
        200:
            description: Empty dictionary
"""
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
    """
    Returns formatted data of specified name and frequency
    ---
    tags:
        - datapoints
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
      - name: start_date
        in: query
        type: string
        required: false
        description: start date.
      - name: end_date
        in: query
        type: string
        required: false
        description: end date.
      - name: format
        in: query
        type: string
        required: false
        description: csv or json 
    responses:
        400:
            description: You have one the following errors. Wrong name or frequency.
                        start date in future or end_date greater than start_date
        200:
            description:  Json or Csv response of queried data with specified format.
   """

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
    possible_names = queries.possible_names_values(freq)
    return jsonify(possible_names)


@api.route('/info', methods=['GET'])
def get_date_range():
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

