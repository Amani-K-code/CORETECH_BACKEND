from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.token import Token
from .. import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_data():
    """
    Fetches logged-in user data and token balance.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    token = Token.query.filter_by(user_id=user_id).first()
    litres_dispensed_total = float(user.litres_dispensed) if user.litres_dispensed is not None else 0.00

    token_balance = 0
    if token:
        token_balance = token.balance

    return jsonify({
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'token_balance': token_balance,
        'litres_dispensed': litres_dispensed_total
    }), 200