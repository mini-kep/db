#FIXME: can this file be db/custom_api/views.py?

from flask import Blueprint, jsonify
from db.api.errors import CustomError400
import db.custom_api.custom_api as custom_api

custom_api_bp = Blueprint('custom_api', __name__, url_prefix='')


@custom_api_bp.errorhandler(CustomError400)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


BASE_URL = '/<string:domain>/series/<string:varname>'

@custom_api_bp.route(f'{BASE_URL}/<string:freq>') 
@custom_api_bp.route(f'{BASE_URL}/<string:freq>/<path:inner_path>')
def time_series_api_interface(domain, varname, freq, inner_path=''):
    return custom_api.CustomGET(domain, varname, freq, inner_path).get_csv_response()
