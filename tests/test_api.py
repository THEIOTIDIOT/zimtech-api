from datetime import datetime
from tests.utils import set_current_user
from flask_security import Security, current_user
from flask import Flask, jsonify
from zimtechapi import db, security, mail, migrate
from zimtechapi.models import Blog
import pytest

TEST_BLOG = dict({"title": "First Blog", "body": "Hello World", "published": True})


def create_blog_post(myapp):
    # This requires "blogger-write" permission
    with myapp.test_client() as c:
        resp = req(
            c,
            "post",
            myapp,
            "/api/me/blogs",
            json=TEST_BLOG,
        )
        return resp


def drop_create_db(myapp: Flask):
    sec: Security = myapp.security
    ds = sec.datastore

    with myapp.app_context():
        ds.db.drop_all()
        ds.db.create_all()


def create_db_and_set_user(myapp: Flask):
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


def req(client, method: str, myapp: Flask, endpoint: str, **kwargs):
    headers = {myapp.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"]: "token"}
    if method.lower() == "get":
        return client.get(endpoint, headers=headers, **kwargs)
    elif method.lower() == "post":
        return client.post(endpoint, headers=headers, **kwargs)
    elif method.lower() == "put":
        return client.put(endpoint, headers=headers, **kwargs)
    elif method.lower() == "delete":
        return client.delete(endpoint, headers=headers, **kwargs)


def test_base():
    assert True


def test_get_health(myapp: Flask):
    create_db_and_set_user(myapp)

    with myapp.test_client() as client:
        resp = req(
            client,
            "get",
            myapp,
            "/api/health",
        )
        assert resp.get_json()["secret"] == "42"
        assert resp.status_code == 200


def test_post_blog(myapp: Flask):
    create_db_and_set_user(myapp)

    with myapp.test_client() as c:
        resp = create_blog_post(myapp)
        assert resp.status_code == 200


def test_get_editable_blog(myapp: Flask):
    # drop_create_db(myapp)
    create_db_and_set_user(myapp)

    # This requires "blogger-write" permission
    with myapp.test_client() as c:
        resp = create_blog_post(myapp)
        assert resp.status_code == 200

        resp = req(c, "get", myapp, "/api/blog/1")

        assert resp.json["title"] == "First Blog"
        assert resp.status_code == 200


def test_get_public_blog(myapp: Flask):
    create_db_and_set_user(myapp)
    create_blog_post(myapp)
    create_blog_post(myapp)
    create_blog_post(myapp)

    set_current_user(myapp.security, force_anon=True)

    with myapp.test_client() as c:
        resp = c.get("/api/me/blogs")
        l = len(resp.json)
        assert l == 3
        assert resp.status_code == 200
