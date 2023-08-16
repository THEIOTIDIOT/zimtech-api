import unittest
from base import BaseTestCase
from zimtechapi.models import (
    WebAppUserCSRFSession,
)
import json


@staticmethod
def register_user(self: BaseTestCase, email, password, username):
    payload = dict(username=username, email=email, password=password)
    return self.client.post(
        "/auth/register",
        data=json.dumps(payload),
        content_type="application/json",
    )

class TestAuthBlueprint(BaseTestCase):
    def test_base(self):
        self.assertTrue(True)

    def test_registration(self):
        """Test for user registration"""
        with self.client:
            email = "ben@gmail.com"
            response = register_user(self, email, "123456", "ben")
            data = json.loads(response.data)
            user_session_csrf = WebAppUserCSRFSession.get_active_user_csrf_session(email)
            self.assertTrue(data["csrf_token"] != self.client.get_cookie("user_session"))
            self.assertTrue(data["csrf_token"] == user_session_csrf.csrf_token)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

    def test_non_whitelist_registration(self):
        """Test for non white list attempted user registration"""
        with self.client:
            email = "intruder@gmail.com"
            response = register_user(self, email, "123456", "intruder")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 401)

    def test_registered_user_login(self):
        """Test for login of registered-user login"""
        with self.client:
            # user registration
            email = "ben@gmail.com"
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
            email = "ben@gmail.com"
            register_user(self, email, "123456", "ben")
            cookie = self.client.get_cookie("user_session")
            response = self.client.get("/auth/status")
            data = json.loads(response.data)
            self.assertTrue(cookie is not None)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["data"] is not None)
            self.assertTrue(data["data"]["email"] == "ben@gmail.com")
            self.assertTrue(data["data"]["admin"] == "true" or "false")
            self.assertEqual(response.status_code, 200)

    def test_valid_logout(self):
        """Test for logout before token expires"""
        with self.client:
            # user registration
            email = "ben@gmail.com"
            register_user(self, email, "123456", "ben")
            # valid token logout
            response = self.client.post("/auth/logout")
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully logged out.")
            self.assertEqual(response.status_code, 200)

    # def test_create_


if __name__ == "__main__":
    unittest.main()
