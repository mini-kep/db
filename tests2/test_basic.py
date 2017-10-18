import unittest
from flask import current_app
from db import _app

# db/__init__.py

# db is both package name and SQLA database
# db = SQLAlchemy()
#
#def _app():
#    return Flask(__name__)
#
#def create_app(config=None):
#    app = Flask(__name__)
#    # make config optioal - easier for debugging.
#    if config:
#        app.config.from_object(config)
#    db.init_app(app)
#    return app

from db import db as fsa_db

def make_app():
    app = _app() # was: Flask(__name__)
    app.testing = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        
    return app 

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = make_app()               
        self.app_context = self.app.app_context()
        self.app_context.push()
        fsa_db.init_app(app=self.app)
        fsa_db.create_all()

    def tearDown(self):
        fsa_db.session.remove()
        fsa_db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)
 

if __name__ == '__main__':
    unittest.main(module='test_basic')