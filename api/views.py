from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from flask_cors import cross_origin
from api.models import (
    WebAppUser,
    WebAppUserSession,
    WebAppUserCSRFSession,
)

base_blueprint = Blueprint("base", __name__)


class HomePage(MethodView):
    """
    User Registration Resource
    """
    @cross_origin
    def get(self):
        pass
        
# define the API resources
home_page_view = HomePage.as_view("home_page")

# add Rules for API Endpoints
base_blueprint.add_url_rule("/", view_func=home_page_view, methods=["GET"])