import os
import unittest

# tests fail unless repo root is on path
# COMMENT: suspicious, usually tests do not need this
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from db import create_app, db
from db.api.views import api as api_module


# create test app
app = create_app('config.TestingConfig')
app.register_blueprint(api_module)


class TestCase(unittest.TestCase):
    def _read_test_data(self):
        tests_folder = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(tests_folder, 'test_data.json')) as data_file:
            return data_file.read()

    def setUp(self):
        db.create_all(app=app)
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all(app=app)