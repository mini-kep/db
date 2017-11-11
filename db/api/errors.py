# Custom exception implemented by Flask pattern 
# http://flask.pocoo.org/docs/0.12/patterns/apierrors/

class CustomError400(Exception):
    status_code = 400

    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload

    @property     
    def dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
