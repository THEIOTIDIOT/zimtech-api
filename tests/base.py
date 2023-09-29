from flask_testing import TestCase
from zimtechapi import create_app, db, mail

class BaseTestCase(TestCase):
    """Base Tests """
    def create_app(self):
        self.app = create_app("zimtechapi.config.TestingConfig")
        self.mail = mail
        return self.app

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()