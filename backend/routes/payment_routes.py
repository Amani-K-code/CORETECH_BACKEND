from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from sqlalchemy import desc
from datetime import datetime
from ..models.user import User
from ..models.token import Token
from ..models.payment import Payment
from ..config import TOKEN_RATE

payment_bp = Blueprint('payment', __name__, url_prefix= '/payments')

@payment_bp.route('/buy', methods=['POST'])
@jwt_required()
def buy_tokens():
    #purchase of tokens:
    current_user_id = get_jwt_identity()
    data = request.get_json()
    amount = data.get('amount')

    if not amount or not isinstance(amount, (int,float)) or amount <=0:
        return jsonify({"msg":"Invalid payment amount provided"}), 400
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    tokens_purchased = int(amount * TOKEN_RATE)

    #MOCK TRANSACTION which will later be changed to MPESA integration
    mock_transaction_id = f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user_id}"

    try:
        new_payment = Payment(
            user_id = current_user_id,
            amount = amount,
            tokens_purchased=tokens_purchased,
            transaction_id=mock_transaction_id,
            status='completed' 
        )
        db.session.add(new_payment)

        user_token = Token.query.filter_by(user_id=current_user_id).first()
        if user_token:
            user_token.balance += tokens_purchased
        else:
            #Just incase it wasnt initialied after registration.
            user_token = Token(user_id=current_user_id, balance=tokens_purchased)
            db.session.add(user_token)

        db.session.commit()

        return jsonify({
            "msg": "Payment successful and tokens added!",
            "new_balance": user_token.balance,
            "tokens_purchased": tokens_purchased,
            "amount": amount
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Payment processing unsuccessful with this error: {e}")
        return jsonify ({"msg":"An internal error occured during payment processing"}), 500

@payment_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    current_user_id = get_jwt_identity()

    payments = Payment.query.filter_by(user_id = current_user_id)\
                            .order_by(desc(Payment.created_at))\
                            .limit(20).all()
    
    history_list = [p.to_dict() for p in payments]

    return jsonify({"history": history_list}), 200