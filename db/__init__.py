from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _app():
    return Flask(__name__)

def create_app(config=None):
    app = Flask(__name__)
    # make config optioal - easier for debugging.
    if config:
        app.config.from_object(config)
    db.init_app(app)
    return app
