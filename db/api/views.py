import json
from flask import Blueprint, request, abort, jsonify, current_app, Response
from flask.views import MethodView

import db.api.utils as utils
from db import db
from db.api.errors import CustomError400
from db.api.parameters import RequestArgs, RequestFrameArgs, SimplifiedArgs
from db.api.queries import All, Allowed, DatapointOperations

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')


@api_bp.errorhandler(422)
def handle_validation_error(error):

    # error 422 is raised by webargs, on two accasions:
    # 1. argument check on input (eg required argument missing)
    #    webarg raises some exception internally
    # 2. argument check inside parser class (eg start date must be before or equal end date)
    #    we raise ArgError(ValidationError)

    # when custom class ArgError is raised we will have 'kwargs.['load']'
    # available
    view_dict = error.exc.kwargs.get('load', {})
    # other validation paths for error 422 in webargs will just have .messages
    view_dict['messages'] = error.exc.messages
    # send combination of the above to user screen
    response = jsonify(view_dict)
    response.status_code = error.exc.status_code
    return response


@api_bp.errorhandler(CustomError400)
def handle_invalid_usage(error):
    """Generate a json object of a custom error"""
    response = jsonify(error.dict)
    response.status_code = error.status_code
    return response

# PROPOSED ENHANCEMENT: Can use this fucntion as decorator for DatapointsAPI.post() amd .delete methods()
#                       Currently authorise() used inside these methods. 
#                       Decorator can help abstract database logic inside a method from access infrastructure
#
#                       Current problem - not sure how to add a decorator to individual class methods. 
#                       <http://flask.pocoo.org/docs/0.12/views/#decorating-views> has example on how 
#                       to add decorators to all of class, but warns the 'traditional' decoraots wont 
#                       work on individual methods:
#                             
#                                class UserAPI(MethodView):
#                                    decorators = [user_required]
#
#                                > Due to the implicit self from the caller’s perspective you cannot use 
#                                > regular view decorators on the individual methods of the view 
#                                > <http://flask.pocoo.org/docs/0.12/views/#decorating-views>
#
#  Decision: for now plain call to authorise seems cleanest available solution.

def authorise():
    token_to_check = request.args.get(
        'API_TOKEN') or request.headers.get('API_TOKEN')
    if token_to_check != current_app.config['API_TOKEN']:
        return abort(403)


def no_download(csv_str):
    """Show document in browser, do not start a download dialog."""
    return Response(response=csv_str, mimetype='text/plain')


def publish_csv(data):
    """Convert *data* iterator to csv string."""
    csv_str = utils.to_csv([row.serialized for row in data])
    return no_download(csv_str)


def publish_json(data):
    """Convert *data* iterator to json."""
    return jsonify([row.serialized for row in data])


class DatapointsAPI(MethodView):

    def get(self):
        """
        Select time series data as csv or json.

        Responses:
            422:
                Bad arguments, eg start_date > end_date
            200:
                Sent json or csv.
       """
        args = RequestArgs()
        data = DatapointOperations.select(**args.query_param)
        if args.format == 'json':
            return publish_json(data)
        else:
            return publish_csv(data)

    def delete(self):
        """Delete datapoints.

        Responses:
            403:
                Failed to authenticate correctly.
            200:
                Returns empty dictionary on success.
        """

        authorise()
        args = SimplifiedArgs()
        DatapointOperations.delete(**args.query_param)
        return jsonify({})

    def post(self):
        """Upload incoming data to database.

        Responses:
            400:
                Something went wrong in during query.
            403:
                Failed to authenticate correctly.
            200:
                Returns empty dictionary on success.
        """
        authorise()
        try:
            data = json.loads(request.data)
            for datapoint in data:
                DatapointOperations.upsert(datapoint)
            db.session.commit()
            return jsonify({})
        except BaseException:
            db.session.rollback()
            return abort(400)


api_bp.add_url_rule(
    '/datapoints',
    view_func=DatapointsAPI.as_view('datapoints_view'))


@api_bp.route('/frame', methods=['GET'])
def get_dataframe():
    """Get csv file readable as pd.DataFrame based on many of all variabel names.

    URL examples:

         api/frame?freq=a&names=GDP_yoy,CPI_rog&start_date=2013-12-31
         api/frame?freq=a&start_date=2013-12-31
         api/frame?freq=a

    FIXME:
        Application hangs on a large query like

        api/frame?freq=q
    """
    args = RequestFrameArgs()
    param = args.query_param
    if not args.names:
        param['names'] = Allowed.names(args.freq)
    data = DatapointOperations.select_frame(**param)
    csv_str = utils.DictionaryRepresentation(data, param['names']).to_csv()
    return no_download(csv_str)


@api_bp.route('/freq', methods=['GET'])
def get_freq():
    """Get list of frequencies."""
    return jsonify(All.frequencies())


@api_bp.route('/names', methods=['GET'])
def get_all_variable_names():
    """Get all variable names in a dataset.

    Responses:
        200:  Returns a list of names
    """
    return jsonify(All.names())


@api_bp.route('/names/<freq>', methods=['GET'])
def get_all_variable_names_for_frequency(freq):
    """Get variable names for frequency *freq*

    Responses:
        200:  Returns a list of names
    """
    return jsonify(Allowed.names(freq))


@api_bp.route('/info', methods=['GET'])
def info():
    varname = request.args.get('name')
    freq = request.args.get('freq')
    return utils.variable_info(varname, freq)


# TODO:
    # POST varname
    # POST unit
