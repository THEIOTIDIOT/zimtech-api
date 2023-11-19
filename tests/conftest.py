import pytest
from zimtechapi import create_app


@pytest.fixture
def myapp():
    app = create_app("zimtechapi.config.TestingConfig")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()