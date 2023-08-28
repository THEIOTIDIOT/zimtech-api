from flask import current_app, Blueprint, request, make_response, jsonify, session
from flask.views import MethodView
from zimtechapi import db

# from zimtechapi import bcrypt, db, app
from zimtechapi.models import (
    WebAppUser,
    WebAppUserSession,
    WebAppUserCSRFSession,
    bcrypt,
)
import logging
auth_blueprint = Blueprint("auth", __name__)


class RegisterApi(MethodView):
    """
    User Registration Resource
    """

    def __init__(self):
        self.logger = logging.getLogger(".".join([__name__, self.__class__.__name__]))

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
                response = jsonify(responseObject)
                response.set_cookie(
                    "user_session", 
                    value=user_session.session_token,
                    httponly=True,
                    domain='.benzimmer.us',
                    secure=True,
                    samesite=None,
                )
                self.logger.debug(user_session.session_token)
                self.logger.debug(response.get_json())
                return response, 201
            except Exception as e:
                self.logger.error("Uncaught exception occurred.")
                self.logger.debug(e)
                responseObject = {
                    "status": "fail",
                    "message": f"Some error occurred. Please try again. {e}",
                }
                return jsonify(responseObject), 401
        else:
            self.logger.error("Attempt was made to create a user with existing email.")
            responseObject = {
                "status": "fail",
                "message": f"Some error occurred. Please try again. {e}",
            }
            return jsonify(responseObject), 401


class LoginApi(MethodView):
    """
    User Login Resource
    """

    def __init__(self):
        self.logger = logging.getLogger(".".join([__name__, self.__class__.__name__]))

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
                self.logger.debug(f"username={user.username}, password={user.password}")
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
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                }
                response = jsonify(responseObject)
                response.set_cookie(
                    "user_session", 
                    value=user_session.session_token,
                    httponly=True,
                    domain='.benzimmer.us',
                    secure=True,
                    samesite=None,
                )
                self.logger.debug(response.get_json())
                return response, 200
            else:
                responseObject = {"status": "fail", "message": "Unable to login."}
                return jsonify(responseObject), 404
        except Exception as e:
            print(e)
            responseObject = {"status": "fail", "message": "Try again"}
            return jsonify(responseObject), 500


class UserApi(MethodView):
    """
    User Resource
    """

    def __init__(self):
        self.logger = logging.getLogger(".".join([__name__, self.__class__.__name__]))

    def get(self):
        # get the auth token
        auth_token = request.cookies.get("user_session")
        self.logger.debug(f"session token is : {auth_token}")
        if auth_token:
            user = WebAppUserSession.get_user(auth_token)
            if user != None:
                response = {
                    "status": "success",
                    "data": {
                        "user_id": user.id,
                        "email": user.email,
                        "admin": user.admin,
                        "registered_on": user.registered_on,
                    },
                }
                response = jsonify(response)
                return response, 200
            response = {"status": "fail", "message": "No active user session."}
            self.logger.debug("No active user session")
            return jsonify(response), 401
        else:
            response = {
                "status": "fail",
                "message": "Provide a valid session token.",
            }
            self.logger.debug("Not a valid session token")
            return jsonify(response), 401


class LogoutApi(MethodView):
    """
    Logout Resource
    """

    def __init__(self):
        self.logger = logging.getLogger(".".join([__name__, self.__class__.__name__]))

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
                    response = jsonify(responseObject)
                    return response, 200
                except Exception as e:
                    responseObject = {"status": "fail", "message": e}
                    return jsonify(responseObject), 200
            else:
                responseObject = {"status": "fail", "message": "No user logged in."}
                return jsonify(responseObject), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "No session cookie found.",
            }
            return jsonify(responseObject), 403


# define the zimtechapi resources

registration_view = RegisterApi.as_view("register_zimtechapi")
login_view = LoginApi.as_view("login_zimtechapi")
user_view = UserApi.as_view("user_zimtechapi")
logout_view = LogoutApi.as_view("logout_zimtechapi")

# add Rules for zimtechapi Endpoints
auth_blueprint.add_url_rule(
    "/auth/register", view_func=registration_view, methods=["POST"]
)
auth_blueprint.add_url_rule("/auth/login", view_func=login_view, methods=["POST"])
auth_blueprint.add_url_rule("/auth/status", view_func=user_view, methods=["GET"])
auth_blueprint.add_url_rule("/auth/logout", view_func=logout_view, methods=["POST"])
