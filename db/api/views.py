import json
from datetime import datetime
from flask import Blueprint, request, abort, jsonify, current_app
from db.api.models import Datapoint
from db import db


api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/datapoints', methods=['GET'])
def get_datapoints():
    try:
        name = request.args['name']
        freq = request.args['freq']
    except:
        return abort(400)
    # Filter by necessary parameters
    data = Datapoint.query.filter(Datapoint.name == name).filter(Datapoint.freq == freq).order_by(Datapoint.date)
    # Filter by optional parameters
    start_date, end_date = request.args.get('start_date'), request.args.get('end_date')
    if start_date:
        data = data.filter(Datapoint.date >= datetime.strptime(start_date, "%Y-%M-%d").date())
    if end_date:
        data = data.filter(Datapoint.date <= datetime.strptime(start_date, "%Y-%M-%d").date())
    return jsonify([row.serialize for row in data.all()])


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
            datapoint['date'] = datetime.strptime(datapoint['date'], "%Y-%m-%d").date()
        db.session.bulk_insert_mappings(Datapoint, data)
    except:
        return abort(400)
    db.session.commit()
    return jsonify({})
