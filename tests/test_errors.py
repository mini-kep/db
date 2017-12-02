from db.api.errors import CustomError400
from tests.test_basic import TestCaseBase


class Test_CustomError(TestCaseBase):
    def test_custom_error_is_initable(self):
        assert CustomError400(message='text').dict == dict(message='text')
