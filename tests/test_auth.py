import unittest
from base import BaseTestCase

class TestAuthBlueprint(BaseTestCase):
    def test_base(self):
        self.assertTrue(True)
    
    def test_send_email(self):
        mailer = self.mail
        mailer.send_mail(
            "Test Subject",
            "Test message!",
            "benzimmer.is@gmail.com",
            ["benzimmer.is@gmail.com"]
        )

    

if __name__ == "__main__":
    unittest.main()
