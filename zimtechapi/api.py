from datetime import datetime

from flask import Blueprint, abort, current_app, jsonify
from flask_security import auth_required

api = Blueprint("api", __name__)

@api.route("/health", methods=["GET"])
@auth_required("session")
def health():
    return jsonify(secret="42", date=datetime.utcnow())