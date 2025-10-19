from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..import db
from ..models.user import User
from ..models.token import Token

token_bp = Blueprint('token', __name__)
@token_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_token_balance():
    user_id = get_jwt_identity()
    token= Token.query.filter_by(user_id=user_id).first()

    if not token:
        token= Token(user_id=user_id, balance=0)
        db.session.add(token)
        db.session.commit()

    return jsonify({'balance': token.balance}), 200



