from flask import Blueprint, jsonify
from db.api.errors import CustomError400
from db.api.queries import DatapointOperations
from db.api.utils import variable_info
from db.api.views import publish_csv
from db.custom_api.decomposer import Indicator

custom_api_bp = Blueprint('custom_api', __name__, url_prefix='')


@custom_api_bp.errorhandler(CustomError400)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


BASE_URL = '/<string:domain>/series/<string:varname>'


@custom_api_bp.route(f'{BASE_URL}/<string:freq>', strict_slashes=False)
@custom_api_bp.route(f'{BASE_URL}/<string:freq>/<path:inner_path>')
def time_series_api_interface(domain, varname, freq, inner_path=''):
    this_variable = Indicator(domain, varname, freq, inner_path)
    data = DatapointOperations.select(**this_variable.query_param)
    return publish_csv(data)


@custom_api_bp.route(f'{BASE_URL}/<string:freq>/info')
@custom_api_bp.route(f'{BASE_URL}/<string:freq>/<path:inner_path>/info')
def info(varname, freq, **kwargs):
    data = variable_info(varname, freq)
    return jsonify(data)
