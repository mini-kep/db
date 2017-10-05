import os
basedir = os.path.abspath(os.path.dirname(__file__))


class ProductionConfig(object):
    #Config for deploying with Heroku - just create config var API_TOKEN
    DEBUG = False
    API_TOKEN = os.getenv('API_TOKEN')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT=os.getenv('PORT')


class DevelopmentConfig(object):
    DEBUG = True
    API_TOKEN = '123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT=5000
