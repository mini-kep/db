from db import create_app
from db.api.views import api as api_module


if __name__ == '__main__':
    app = create_app('config.ProductionConfig')
    app.register_blueprint(api_module)
    app.run(host="0.0.0.0", port=int(app.config['PORT']))
