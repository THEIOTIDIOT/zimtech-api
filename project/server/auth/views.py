from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db, csrf
from project.server.models import WebAppUser, WebAppUserSession, BlacklistToken

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
                
                # create session for the user
                user_session = WebAppUserSession(user.email, 15)
                db.session.add(user_session)
                db.session.commit()
                
                responseObject = {
                    "status": "success",
                    "message": "Successfully registered.",
                    "csrf_token": user_session.csrf_token,
                }
                return make_response(jsonify(responseObject)), 201
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
                user_session = None
                # Can't have two active sessions
                if not WebAppUserSession.is_session_active(email):
                    user_session = WebAppUserSession(email, 15)
                else:
                    user_session = WebAppUserSession.get_active_user_session(email)
                    user_session.csrf_token_disabled = True
                    db.session.commit()
                    user_session = WebAppUserSession(email, 15)
                    db.session.add(user_session)
                    db.session.commit()

                # json response
                responseObject = {
                    "status": "success",
                    "message": "Successfully logged in.",
                    "csrf_token": user_session.csrf_token,
                }
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {"status": "fail", "message": "User does not exist."}
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
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    "status": "fail",
                    "message": "Bearer token malformed.",
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ""
        if auth_token:
            resp = WebAppUser.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = WebAppUser.query.filter_by(id=resp).first()
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
            responseObject = {"status": "fail", "message": resp}
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """

    def post(self):
        # get auth token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ""
        if auth_token:
            resp = WebAppUser.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
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
                responseObject = {"status": "fail", "message": resp}
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return make_response(jsonify(responseObject)), 403


# define the API resources

registration_view = csrf.exempt(RegisterAPI.as_view("register_api"))
login_view = csrf.exempt(LoginAPI.as_view("login_api"))
user_view = UserAPI.as_view("user_api")
logout_view = LogoutAPI.as_view("logout_api")

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    "/auth/register", view_func=registration_view, methods=["POST"]
)
auth_blueprint.add_url_rule("/auth/login", view_func=login_view, methods=["POST"])
auth_blueprint.add_url_rule("/auth/status", view_func=user_view, methods=["GET"])
auth_blueprint.add_url_rule("/auth/logout", view_func=logout_view, methods=["POST"])
