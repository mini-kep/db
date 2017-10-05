from db import app
from db.api.views import api as api_module


if __name__ == '__main__':
    app.register_blueprint(api_module)
    app.run(host="0.0.0.0", port=app.config['PORT'])
