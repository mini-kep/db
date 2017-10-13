import os
basedir = os.path.abspath(os.path.dirname(__file__))


class ProductionConfig(object):
    #Config for deploying with Heroku 
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    PORT=os.getenv('PORT')
    # NOTE: must create config var API_TOKEN at heroku
    API_TOKEN = os.getenv('API_TOKEN')


class DevelopmentConfig(object):
    DEBUG = True
    API_TOKEN = 'developer'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database_dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT=5000


class TestingConfig(object):
    DEBUG = True
    API_TOKEN = 'test'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database_test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT=5000
