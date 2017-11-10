import json
from flask import Blueprint, request, abort, jsonify, current_app, Response
from db import db
import db.api.utils as utils
from db.api.errors import CustomError400
import db.api.queries as queries


api = Blueprint('api', __name__, url_prefix='/api')


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
    params = utils.DatapointParameters(request.args).get()
    data = queries.select_datapoints(**params)
    fmt = request.args.get('format')
    return get_datapoints_response(data, fmt)

def get_datapoints_response(data, output_format: str):
    """
    Returns data formatted to csv or json.
    ---
    tags:
        - util
    """
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
    dp = utils.DatapointParameters(request.args)
    result = dict(start_date = dp.get_min_date(), 
                  end_date = dp.get_max_date()) 
    return jsonify(result)
