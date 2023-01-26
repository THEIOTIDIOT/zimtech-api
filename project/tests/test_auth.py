import unittest

from project.server import db
from project.tests.base import BaseTestCase
from project.server.models import WebAppUser, WebAppUserSession, WebAppUserCSRFSession, BlacklistToken
import json
import time
import sqlalchemy as sa

@staticmethod
def register_user(self, email, password, username):
    return self.client.post(
                "/auth/register",
                data=json.dumps(
                    dict(
                            username=username, 
                            email=email, 
                            password=password
                        )
                ),
                content_type="application/json",
            )


class TestAuthBlueprint(BaseTestCase):

    def test_registration(self):
        """Test for user registration"""
        with self.client:
            email="ben@gmail.com"
            response = register_user(self, email, "123456", "ben")
            data = json.loads(response.data)
            user_session = WebAppUserCSRFSession.get_active_user_session(email)
            
            self.assertTrue(data["csrf_token"] == user_session.csrf_token)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)
    
    def test_registered_user_login(self):
        """Test for login of registered-user login"""
        with self.client:
            # user registration
            email="ben@gmail.com"
            resp_register = register_user(self, email, "123456", "ben")
            data_register = json.loads(resp_register.data)
            self.assertTrue(data_register["status"] == "success")
            self.assertTrue(data_register["message"] == "Successfully registered.")
            self.assertTrue(resp_register.content_type == "application/json")
            self.assertEqual(resp_register.status_code, 201)
            csrf_token = data_register["csrf_token"]
            # registered user login
            response = self.client.post(
                "/auth/login",
                data=json.dumps(dict(email="ben@gmail.com", password="123456")),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged in.")
            self.assertTrue(response.content_type == "application/json")
            self.assertTrue(data["csrf_token"] != csrf_token)
            self.assertEqual(response.status_code, 200)

    def test_non_registered_user_login(self):
        """Test for login of non-registered user"""
        with self.client:
            response = self.client.post(
                "/auth/login",
                data=json.dumps(dict(email="joe@gmail.com", password="123456")),
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Unable to login.")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 404)

    def test_user_status(self):
        """Test for user status"""
        with self.client:
            # user registration
            email="ben@gmail.com"
            resp_register = register_user(self, email, "123456", "ben")
            response = self.client.get(
                "/auth/status",
                headers=dict(
                    Authorization="Bearer "
                    + json.loads(resp_register.data)["auth_token"]
                ),
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["data"] is not None)
            self.assertTrue(data["data"]["email"] == "joe@gmail.com")
            self.assertTrue(data["data"]["admin"] == "true" or "false")
            self.assertEqual(response.status_code, 200)

    # def test_valid_logout(self):
    #     """Test for logout before token expires"""
    #     with self.client:
    #         # user registration
    #         resp_register = self.client.post(
    #             "/auth/register",
    #             data=json.dumps(dict(email="joe@gmail.com", password="123456")),
    #             content_type="application/json",
    #         )
    #         data_register = json.loads(resp_register.data)
    #         self.assertTrue(data_register["status"] == "success")
    #         self.assertTrue(data_register["message"] == "Successfully registered.")
    #         self.assertTrue(data_register["auth_token"])
    #         self.assertTrue(resp_register.content_type == "application/json")
    #         self.assertEqual(resp_register.status_code, 201)
    #         # user login
    #         resp_login = self.client.post(
    #             "/auth/login",
    #             data=json.dumps(dict(email="joe@gmail.com", password="123456")),
    #             content_type="application/json",
    #         )
    #         data_login = json.loads(resp_login.data)
    #         self.assertTrue(data_login["status"] == "success")
    #         self.assertTrue(data_login["message"] == "Successfully logged in.")
    #         self.assertTrue(data_login["auth_token"])
    #         self.assertTrue(resp_login.content_type == "application/json")
    #         self.assertEqual(resp_login.status_code, 200)
    #         # valid token logout
    #         response = self.client.post(
    #             "/auth/logout",
    #             headers=dict(
    #                 Authorization="Bearer " + json.loads(resp_login.data)["auth_token"]
    #             ),
    #         )
    #         data = json.loads(response.data)
    #         self.assertTrue(data["status"] == "success")
    #         self.assertTrue(data["message"] == "Successfully logged out.")
    #         self.assertEqual(response.status_code, 200)

    # def test_invalid_logout(self):
    #     """Testing logout after the token expires"""
    #     with self.client:
    #         # user registration
    #         resp_register = self.client.post(
    #             "/auth/register",
    #             data=json.dumps(dict(email="joe@gmail.com", password="123456")),
    #             content_type="application/json",
    #         )
    #         data_register = json.loads(resp_register.data)
    #         self.assertTrue(data_register["status"] == "success")
    #         self.assertTrue(data_register["message"] == "Successfully registered.")
    #         self.assertTrue(data_register["auth_token"])
    #         self.assertTrue(resp_register.content_type == "application/json")
    #         self.assertEqual(resp_register.status_code, 201)
    #         # user login
    #         resp_login = self.client.post(
    #             "/auth/login",
    #             data=json.dumps(dict(email="joe@gmail.com", password="123456")),
    #             content_type="application/json",
    #         )
    #         data_login = json.loads(resp_login.data)
    #         self.assertTrue(data_login["status"] == "success")
    #         self.assertTrue(data_login["message"] == "Successfully logged in.")
    #         self.assertTrue(data_login["auth_token"])
    #         self.assertTrue(resp_login.content_type == "application/json")
    #         self.assertEqual(resp_login.status_code, 200)
    #         # invalid token logout
    #         time.sleep(6)
    #         response = self.client.post(
    #             "/auth/logout",
    #             headers=dict(
    #                 Authorization="Bearer " + json.loads(resp_login.data)["auth_token"]
    #             ),
    #         )
    #         data = json.loads(response.data)
    #         self.assertTrue(data["status"] == "fail")
    #         self.assertTrue(
    #             data["message"] == "Signature expired. Please log in again."
    #         )
    #         self.assertEqual(response.status_code, 401)

    # def test_valid_blacklisted_token_logout(self):
    #     """Test for logout after a valid token gets blacklisted"""
    #     with self.client:
    #         # user registration
    #         resp_register = self.client.post(
    #             "/auth/register",
    #             data=json.dumps(dict(email="joe@gmail.com", password="123456")),
    #             content_type="application/json",
    #         )
    #         data_register = json.loads(resp_register.data)
    #         self.assertTrue(data_register["status"] == "success")
    #         self.assertTrue(data_register["message"] == "Successfully registered.")
    #         self.assertTrue(data_register["auth_token"])
    #         self.assertTrue(resp_register.content_type == "application/json")
    #         self.assertEqual(resp_register.status_code, 201)
    #         # user login
    #         resp_login = self.client.post(
    #             "/auth/login",
    #             data=json.dumps(dict(email="joe@gmail.com", password="123456")),
    #             content_type="application/json",
    #         )
    #         data_login = json.loads(resp_login.data)
    #         self.assertTrue(data_login["status"] == "success")
    #         self.assertTrue(data_login["message"] == "Successfully logged in.")
    #         self.assertTrue(data_login["auth_token"])
    #         self.assertTrue(resp_login.content_type == "application/json")
    #         self.assertEqual(resp_login.status_code, 200)
    #         # blacklist a valid token
    #         blacklist_token = BlacklistToken(
    #             token=json.loads(resp_login.data)["auth_token"]
    #         )
    #         db.session.add(blacklist_token)
    #         db.session.commit()
    #         # blacklisted valid token logout
    #         response = self.client.post(
    #             "/auth/logout",
    #             headers=dict(
    #                 Authorization="Bearer " + json.loads(resp_login.data)["auth_token"]
    #             ),
    #         )
    #         data = json.loads(response.data)
    #         self.assertTrue(data["status"] == "fail")
    #         self.assertTrue(
    #             data["message"] == "Token blacklisted. Please log in again."
    #         )
    #         self.assertEqual(response.status_code, 401)

    # def test_valid_blacklisted_token_user(self):
    #     """Test for user status with a blacklisted valid token"""
    #     with self.client:
    #         resp_register = self.client.post(
    #             "/auth/register",
    #             data=json.dumps(dict(email="joe@gmail.com", password="123456")),
    #             content_type="application/json",
    #         )
    #         # blacklist a valid token
    #         blacklist_token = BlacklistToken(
    #             token=json.loads(resp_register.data)["auth_token"]
    #         )
    #         db.session.add(blacklist_token)
    #         db.session.commit()
    #         response = self.client.get(
    #             "/auth/status",
    #             headers=dict(
    #                 Authorization="Bearer "
    #                 + json.loads(resp_register.data)["auth_token"]
    #             ),
    #         )
    #         data = json.loads(response.data)
    #         self.assertTrue(data["status"] == "fail")
    #         self.assertTrue(
    #             data["message"] == "Token blacklisted. Please log in again."
    #         )
    #         self.assertEqual(response.status_code, 401)

    # def test_user_status_malformed_bearer_token(self):
    #     """Test for user status with malformed bearer token"""
    #     with self.client:
    #         resp_register = register_user(self, "joe@gmail.com", "123456")
    #         response = self.client.get(
    #             "/auth/status",
    #             headers=dict(
    #                 Authorization="Bearer"
    #                 + json.loads(resp_register.data.decode())["auth_token"]
    #             ),
    #         )
    #         data = json.loads(response.data.decode())
    #         self.assertTrue(data["status"] == "fail")
    #         self.assertTrue(data["message"] == "Bearer token malformed.")
    #         self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
