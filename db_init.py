import json

# ----------- db.__init__.py -----------
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config.from_object('config.DevelopmentConfig')
# db = SQLAlchemy(app)
# --------------------------------------

# EP: once we are importing db from db.__init__ we have a SQLAlchemy(app) instance in this module
from db import db
from db import create_app
# EP: we need to import models here explicitly, otherwise the tables created will be empty
from db.api import models
from db.api.views import api 
from db.api.utils import to_date

# EP: this creates tables specified in db.api.models
# EP: the tables will be created in config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI

# create app
app = create_app('config.DevelopmentConfig') 
app.register_blueprint(api)
# create tables for models
db.create_all(app=app)

# populate database
from pathlib import Path
p = Path(__file__).parent / 'tests' / 'test_data_2016H2.json'

data = json.loads(p.read_text())
for datapoint in data:
    datapoint['date'] = to_date(datapoint['date'])

with app.app_context():
    db.session.bulk_insert_mappings(models.Datapoint, data)
    db.session.commit()