import json
from pathlib import Path

# ----------- db.__init__.py -----------
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config.from_object('config.DevelopmentConfig')
# db = SQLAlchemy(app)
# --------------------------------------

# importing db from db.__init__ - we have a SQLAlchemy(app) instance in this module
# 'from db' is folder name, 'import db' is SQLAlchemy instance
from db import db
from db import create_app
# we need to import models here explicitly, otherwise the tables created
# will be empty
from db.api import models
from db.api.views import api
from db.api.utils import to_date

# this creates tables specified in db.api.models
# the tables will be created in
# config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI

# create app
app = create_app('config.DevelopmentConfig')
app.register_blueprint(api)
# create tables for models
db.create_all(app=app)

# populate database
p = Path(__file__).parent / 'tests' / 'test_data' / 'test_data_2016H2.json'

data = json.loads(p.read_text())
for datapoint in data:
    datapoint['date'] = to_date(datapoint['date'])

with app.app_context():
    # delete everything as we will be unable to insert + commit
    for item in models.Datapoint.query.all():
        db.session.delete(item)
    db.session.commit()
    # add from file
    db.session.bulk_insert_mappings(models.Datapoint, data)
    db.session.commit()
