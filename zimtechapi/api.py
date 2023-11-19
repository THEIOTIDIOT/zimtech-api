from datetime import datetime
from flask import Blueprint, abort, current_app, jsonify, request, Response
from flask_security import (
    auth_required,
    permissions_required,
    permissions_accepted,
    current_user,
    datastore,
    Security,
)
import logging
from .models import Blog, User

api = Blueprint("api", __name__)
logger = logging.getLogger(__name__)


def auth_methods():
    return current_app.config.get("AUTH_METHODS")


@api.route("/health", methods=["GET"])
@auth_required(auth_methods)
def health():
    return jsonify(secret="42", date=datetime.utcnow())


@api.route("/blog/<bid>", methods=["GET", "PUT"])
@auth_required(auth_methods)
@permissions_required("blogger-edit")
def update_blog(bid):
    # Yes caller has write permission - but do they OWN this blog?
    blog: Blog = Blog.query.where(Blog.id == bid).first()
    # blog = current_app.blog_cls.query.filter_by(id=bid).first()
    if not blog:
        abort(404)
    elif current_user != blog.user:
        abort(403)
    else:
        if request.method == "PUT":
            sec: Security = current_app.security
            ds = sec.datastore
            with current_app.app_context():
                if request.is_json:
                    data = request.get_json()
                else:
                    abort(415)
                
                blog.updated_datetime=datetime.now()
                blog.title=data["title"]
                blog.body=data["body"]
                ds.commit()
                return Response(status=200)
        elif request.method == "GET":
            return {
                "user_id": blog.user_id,
                "created_datetime": blog.created_datetime,
                "updated_datetime": blog.updated_datetime,
                "title": blog.title,
                "body": blog.body,
                "published": blog.published,
            }


@api.route("/<username>/blogs", methods=["POST"])
@auth_required(auth_methods)
@permissions_accepted("blogger-create")
def create_blog(username):
    user = User.query.where(User.username == username).first()
    if current_user != user:
        abort(403)
    else:
        sec: Security = current_app.security
        ds = sec.datastore
        with current_app.app_context():
            if request.is_json:
                data = request.get_json()
            else:
                abort(415)
            b = Blog(
                user_id=current_user.id,
                created_datetime=datetime.now(),
                updated_datetime=datetime.now(),
                title=data["title"],
                body=data["body"],
                published=data["published"]
            )

            ds.put(b)
            ds.commit()
            return Response(status=200)


@api.route("/<username>/blogs", methods=["GET"])
def list_my_blogs(username):
    user: User = User.query.where(User.username == username).first()
    blogs = [blog.as_dict() for blog in user.blogs if blog.published == True]
    
    if not blogs:
        abort(404)
    return blogs
