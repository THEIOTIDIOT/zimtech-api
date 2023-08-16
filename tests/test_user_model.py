import unittest
from flask_testing import TestCase
from zimtechapi.models import WebAppUser
from base import BaseTestCase


class TestUserModel(BaseTestCase):
    pass

    # def test_encode_auth_token(self):
    #     user = WebAppUser(email="test@test.com", password="test")
    #     db.session.add(user)
    #     db.session.commit()
    #     auth_token = user.encode_auth_token(user.id, 5)
    #     print(auth_token)
    #     self.assertTrue(isinstance(auth_token, str))

    # def test_decode_auth_token(self):
    #     user = WebAppUser(email="test@test.com", password="test")
    #     db.session.add(user)
    #     db.session.commit()
    #     auth_token = user.encode_auth_token(user.id, 5)
    #     self.assertTrue(isinstance(auth_token, str))
    #     self.assertTrue(WebAppUser.decode_auth_token(auth_token) == 1)


if __name__ == "__main__":
    unittest.main()
