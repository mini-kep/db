# EP: comments to help understand the flask project flow

# ----------- db.__init__.py -----------
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config.from_object('config.DevelopmentConfig')
# db = SQLAlchemy(app)
# --------------------------------------

# EP: once we are importing db from db.__init__ we have a SQLAlchemy(app) instance in this module
from db import db

# EP: we need to import models here explicitly, otherwise the tables created will be empty
from db.api import models

# EP: this creates tables speciified in db.api.models
# EP: the tables will be created in config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI
db.create_all()


# EP (question): the  prescription is to run db_init.py before the first run of each configuration (Development, Production)? 
# EK (answer): yes, that's right
