from flask_testing import TestCase
from blog import create_app
from flask import Flask
from blog.database import db_session, init_db, Base, engine, metadata

app = create_app()

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self) -> Flask:
        app.config.from_object('blog.config.TestingConfig')
        app.testing = True
        return app

    def setUp(self):
        init_db()

    def tearDown(self):
        db_session.remove()
        Base.metadata.drop_all(engine)