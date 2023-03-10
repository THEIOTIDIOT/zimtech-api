from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import (
    WebAppUser,
    WebAppUserSession,
    WebAppUserCSRFSession,
)

auth_blueprint = Blueprint("auth", __name__)


class RegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if user already exists
        user = WebAppUser.query.filter_by(email=post_data.get("email")).first()
        if not user:
            try:
                user = WebAppUser(
                    username=post_data.get("username"),
                    email=post_data.get("email"),
                    password=post_data.get("password"),
                )

                # insert the user
                db.session.add(user)
                db.session.commit()

                # create csrf token session for the user
                csrf_user_session = WebAppUserCSRFSession(user.email, 15)
                db.session.add(csrf_user_session)
                db.session.commit()

                # create session for the user
                user_session = WebAppUserSession(user.email, 60)
                db.session.add(user_session)
                db.session.commit()

                responseObject = {
                    "status": "success",
                    "message": "Successfully registered.",
                    "csrf_token": csrf_user_session.csrf_token,
                }

                response = make_response(jsonify(responseObject))
                response.set_cookie("user_session", user_session.session_token)
                return response, 201
            except Exception as e:
                responseObject = {
                    "status": "fail",
                    "message": f"Some error occurred. Please try again. {e}",
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "User already exists. Please Log in.",
            }
            return make_response(jsonify(responseObject)), 202


class LoginAPI(MethodView):
    """
    User Login Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            email = post_data.get("email")
            user = WebAppUser.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(
                user.password, post_data.get("password")
            ):
                user_csrf_session = None
                # Can't have two active sessions
                if not WebAppUserCSRFSession.is_session_active(email):
                    user_csrf_session = WebAppUserCSRFSession(email, 15)
                else:
                    user_csrf_session = (
                        WebAppUserCSRFSession.get_active_user_csrf_session(email)
                    )
                    user_csrf_session.csrf_token_disabled = True
                    db.session.commit()
                    user_csrf_session = WebAppUserCSRFSession(email, 15)
                    db.session.add(user_csrf_session)
                    db.session.commit()

                # create session for the user
                user_session = WebAppUserSession(user.email, 15)
                db.session.add(user_session)
                db.session.commit()

                # json response
                responseObject = {
                    "status": "success",
                    "message": "Successfully logged in.",
                    "csrf_token": user_csrf_session.csrf_token,
                }

                response = make_response(jsonify(responseObject))
                response.set_cookie("user_session", user_session.session_token)
                return response, 200
            else:
                responseObject = {"status": "fail", "message": "Unable to login."}
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {"status": "fail", "message": "Try again"}
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """
    User Resource
    """

    def get(self):
        # get the auth token
        auth_token = request.cookies.get("user_session")
        if auth_token:
            user = WebAppUserSession.get_user(auth_token)
            if user != None:
                responseObject = {
                    "status": "success",
                    "data": {
                        "user_id": user.id,
                        "email": user.email,
                        "admin": user.admin,
                        "registered_on": user.registered_on,
                    },
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {"status": "fail", "message": "No active user session."}
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid session token.",
            }
            return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """

    def post(self):
        # get the auth token
        session_token = request.cookies.get("user_session")
        if session_token:
            user_session = WebAppUserSession.get_active_user_session(session_token)
            if user_session:
                try:
                    # disable session token
                    user_session.session_token_disabled = True
                    db.session.commit()
                    responseObject = {
                        "status": "success",
                        "message": "Successfully logged out.",
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {"status": "fail", "message": e}
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {"status": "fail", "message": "No user logged in."}
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "No session cookie found.",
            }
            return make_response(jsonify(responseObject)), 403


# define the API resources

registration_view = RegisterAPI.as_view("register_api")
login_view = LoginAPI.as_view("login_api")
user_view = UserAPI.as_view("user_api")
logout_view = LogoutAPI.as_view("logout_api")

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    "/auth/register", view_func=registration_view, methods=["POST"]
)
auth_blueprint.add_url_rule("/auth/login", view_func=login_view, methods=["POST"])
auth_blueprint.add_url_rule("/auth/status", view_func=user_view, methods=["GET"])
auth_blueprint.add_url_rule("/auth/logout", view_func=logout_view, methods=["POST"])
