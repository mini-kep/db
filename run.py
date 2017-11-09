from db import create_app
from db.api.views import api as api_module
from db.custom_api.views import custom_api_bp as custom_api_module
from flasgger import Swagger


if __name__ == '__main__':
    app = create_app('config.ProductionConfig')
    app.register_blueprint(api_module)
    app.register_blueprint(custom_api_module)
    Swagger(app)
    #app.run(host="0.0.0.0")
    app.run(host="0.0.0.0", port=int(app.config['PORT']))
