import unittest
from tests import app, TestCase

class TestAPI_Incoming(TestCase):

    def test_auth_forbidden(self):
        response = self.app.post('/api/incoming')
        assert response.status_code == 403

    def test_upload_data(self):
        data = self._read_test_data()
        response = self.app.post('/api/incoming',
                                 data=data,
                                 headers=dict(API_TOKEN=app.config['API_TOKEN']))
        assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()