import datetime
from flask import request, jsonify, Blueprint
from middleware import verify_client_credentials
from models import OAuth2Token, db, User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "username": user.UserName,  # Changed from id to UserName
        "email": user.Email         # Changed from email to Email
    }), 200