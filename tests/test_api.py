from datetime import datetime
from tests.utils import set_current_user
from flask_security import Security, current_user
from flask import Flask, jsonify
from zimtechapi import db, security, mail, migrate
from zimtechapi.models import Blog
import pytest


def create_and_set_user(myapp: Flask):
    sec: Security = myapp.security
    ds = sec.datastore
    with myapp.app_context():
        ds.db.drop_all()
        ds.db.create_all()

        r1 = ds.create_role(
            name="blogger", permissions={"blogger-create", "blogger-edit"}
        )
        user = ds.create_user(
            email="unittest@me.com", username="me", password="password", roles=[r1]
        )
        ds.commit()

    set_current_user(myapp, ds, "unittest@me.com")


def test_base():
    assert True


def test_get_health(myapp: Flask):
    sec: Security = myapp.security
    ds = sec.datastore
    with myapp.app_context():
        ds.db.drop_all()
        ds.db.create_all()

        r1 = ds.create_role(name="basic")
        user = ds.create_user(email="unittest@me.com", password="password", roles=[r1])
        ds.commit()

    set_current_user(myapp, ds, "unittest@me.com")

    with myapp.test_client() as client:
        resp = client.get(
            "/api/health",
            headers={myapp.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"},
        )
        assert resp.get_json()["secret"] == "42"
        assert resp.status_code == 200


def test_post_blog(myapp: Flask):
    create_and_set_user(myapp)
    with myapp.test_client() as c:
        resp = c.post(
            "/api/me/blogs",
            headers={myapp.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"},
            json=dict(
                {"title": "First Blog", "body": "Hello World", "published": True}
            ),
        )
        assert resp.status_code == 200


def test_get_editable_blog(myapp: Flask):
    create_and_set_user(myapp)

    # This requires "blogger-write" permission
    with myapp.test_client() as c:
        resp = c.post(
            "/api/blog/1",
            headers={myapp.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"},
            json=dict({"title": "First Blog", "body": "Hello World"}),
        )
        assert resp.status_code == 200

        resp = c.get(
            "/api/blog/1",
            headers={myapp.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"},
        )

        assert resp.json["title"] == "First Blog"
        assert resp.status_code == 200


def test_get_public_blog(myapp: Flask):
    create_and_set_user(myapp)

    # This requires "blogger-write" permission
    with myapp.test_client() as c:
        resp = c.post(
            "/api/blog/1",
            headers={myapp.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"},
            json=dict({"title": "First Blog", "body": "Hello World"}),
        )
        assert resp.status_code == 200

    with myapp.test_client() as c:
        resp = c.get("/api/blogs")
        assert resp.status_code == 200
