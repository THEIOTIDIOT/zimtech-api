from flask_testing import TestCase
from api import create_app
from flask import Flask
from api.models import db

app = create_app()

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self) -> Flask:
        app.config.from_object('api.config.TestingConfig')
        app.testing = True
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()