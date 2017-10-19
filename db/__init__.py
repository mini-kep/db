from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_app():
    return Flask(__name__)


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    return app
