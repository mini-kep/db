from db import create_app
from db.api.views import api as api_module
from db.custom_api.views import custom_api_bp as custom_api_module
from flasgger import Swagger


if __name__ == '__main__':
    app = create_app('config.DevelopmentConfig')
    app.register_blueprint(api_module)
    app.register_blueprint(custom_api_module)
    Swagger(app)
    #app.run(host="127.0.0.1", port=int(app.config['PORT']))
    app.run(host='127.0.0.1', port=8080, debug=True)
