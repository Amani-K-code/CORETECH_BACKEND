from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import jwt_required
from datetime import datetime
from backend.models.water import Water
from ..utils.admin_required import admin_required
from ..models.user import User
from ..models.token import Token
from ..models.payment import Payment
from ..models.dispense_log import DispenseLog
from ..models.water_usage import WaterUsage 
from ..import db
from sqlalchemy import select, delete

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

DEFAULT_TANK_CAPACITY = 100000

@admin_bp.route('/tank_status', methods=['GET'])
@jwt_required()
@admin_required()
def get_tank_status():
    """
    Fetches current water level

    """
    #main_water = Water.query.first()
    main_water = db.session.execute(select(Water)).scalars().first()

    if not main_water:

        main_water = Water(
            capacity_litres = DEFAULT_TANK_CAPACITY,
            current_litres = 0.00
        )
        db.session.add(main_water)
        db.session.commit()

    return jsonify({
        "level": float(main_water.current_litres),
        "capacity": float(main_water.capacity_litres),
        "last_updated": main_water.last_updated.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

@admin_bp.route('/refill_tank', methods=['POST'])
@jwt_required()
@admin_required()
def refill_tank():
    """
    Refilling the tank

    """
    data = request.get_json()
    amount = data.get('amount')

    if not  amount or not isinstance(amount, (int,float)) or amount <= 0:
        return jsonify({"error": "Invalid refill amount provided"}), 400
    
    #main_water= Water.query.first()
    main_water = db.session.execute(select(Water)).scalars().first()

    if not main_water:
        return jsonify({"error": "Main water record noy found"}), 500
    
    new_level = main_water.current_litres + amount

    if new_level > main_water.capacity_litres:

        amount_added = main_water.capacity_litres - main_water.current_litres
        main_water.current_litres  = main_water.capacity_litres
        msg = f"Tank filled to capacity. Added {amount_added:.2f}L."

    else:
        main_water.current_litres = new_level
        amount_added = amount
        msg = f"Tank refilled by {amount_added:.2f}L."

    main_water.last_updated = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({"msg": msg, "new_level": float(main_water.current_litres)}), 200
    except Exception as e:
        db.session.rollback()
        #log error:
        print(f"Database error during refill: {e}")
        return jsonify({"error": "Database error during refill.Please check server logs. "}), 500
    

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def list_users():
    """
    Retrieves list of reg users

    """

    statement = select(User)
    users =db.session.execute(statement).scalars().all()
    user_list = []

    for user in users:

        #user_token = Token.query.filter_by(user_id=user.id).first()
        token_stmt = select(Token).filter_by(user_id=user.id)
        user_token = db.session.execute(token_stmt).scalars().first()

        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'litres_dispensed': float(user.litres_dispensed) if user.litres_dispensed is not None else 0.0,
            'token_balance': float(user_token.balance) if user_token and user_token.balance is not None else 0.0,
            'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(user_list), 200

@admin_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_user_details(user_id):
    """
    Retrieves detailed info for a single user

    """

    #user = User.query.get(user_id)
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error":"User not found"}), 404
    
    #user_token = Token.query.filter_by(user_id=user_id).first()
    token_stmt = select(Token).filter_by(user_id=user_id)
    user_token = db.session.execute(token_stmt).scalars().first()

    #payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
    payment_stmt = select(Payment).filter_by(user_id=user_id).order_by(Payment.created_at.desc())
    payments = db.session.execute(payment_stmt).scalars().all()


    details={
        'id': user.id,
        'username':user.username,
        'email':user.email,
        'is_admin': user.is_admin,
        'litres_dispensed': float(user.litres_dispensed) if user.litres_dispensed is not None else 0.0,
        'token_balance': float(user_token.balance) if user_token and user_token.balance is not None else 0.0,

        'transactions': [p.to_dict() for p in payments]


    }

    return jsonify(details), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_user(user_id):
    """
    Admin can update user details(edit)

    """
    data = request.get_json()
    #user = User.query.get(user_id)
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error":"User not found"}), 404
    
    if 'username' in data and data['username']:
        check_stmt = select(User).filter(User.username == data['username']).filter(User.id != user_id)
        if db.session.execute(check_stmt).scalars().first():
            return jsonify({"error":"Username already taken"}), 400
        user.username = data['username']

    if 'email' in data and data['email']:
        check_stmt = select(User).filter(User.email == data['email']).filter(User.id != user_id)
        if db.session.execute(check_stmt).scalars().first():
            return jsonify({"error":"Email already taken"}), 400
        user.email = data['email']
    
    if 'is_admin' in data and isinstance(data['is_admin'], bool):
        user.is_admin = data['is_admin']

    if 'token_balance' in data and isinstance(data['token_balance'], (int,float)):
        token_stmt = select(Token).filter_by(user_id=user_id)
        user_token = db.session.execute(token_stmt).scalars().first()

        if user_token:
            user_token.balance = data['token_balance']
        else:
            return jsonify({"error":"User token record not found"}), 500
        
    try:
        db.session.commit()
        return jsonify({"msg":f"User {user_id} updated successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Database error during user update: {e}")
        return jsonify({"error" :"Database error during user update"}), 500
    


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_user(user_id):
    """
    Deletes user + all associated records
    
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error":"User not found"}), 404
    
    try:
        db.session.execute(delete(WaterUsage).where(WaterUsage.user_id == user_id))
        db.session.execute(delete(Token).where(Token.user_id == user_id))
        db.session.execute(delete(Payment).where(Payment.user_id == user_id))
        db.session.execute(delete(DispenseLog).where(DispenseLog.user_id == user_id))

        db.session.delete(user)
        db.session.commit()

        return jsonify({"msg":f"User {user_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Database error during user deletion: {e}")
        return jsonify({"error": "Database error during deletion. "}), 500
    



@admin_bp.route('/logs/dispense', methods=['GET'])
@jwt_required()
@admin_required()
def get_dispense_logs():
    """
    Retrieves all dispensed litres for System logs
    
    """

    log_stmt = select(DispenseLog).order_by(DispenseLog.timestamp.desc())
    logs = db.session.execute(log_stmt).scalars().all()

    log_list = [log.to_dict() for log in logs]

    return jsonify(log_list), 200



@admin_bp.route('/logs/payments', methods=['GET'])
@jwt_required()
@admin_required()
def get_payment_logs():
    """
    Retrieves payment/token logs for System Logs page

    """

    log_stmt = select(Payment).order_by(Payment.created_at.desc())
    payments =db.session.execute(log_stmt).scalars().all()

    log_list=[]

    for payment in payments:
        user = User.query.get(payment.user_id) if payment.user_id else None
        payment_data = payment.to_dict()
        payment_data['username']= user.username if user else 'N/A'
        payment_data['transaction_id'] = payment.transaction_id if hasattr(payment, 'transaction_id') else 'N/A'

        log_list.append(payment_data)

    return jsonify(log_list), 200

@admin_bp.route('/metrics', methods=['GET'])
@jwt_required()
@admin_required()
def get_key_metrics():
    """Retrieves total dispensed water and total users"""
    try:
        total_dispensed = db.session.query(
            db.func.sum(User.litres_dispensed)
        ).scalar() or 0.0

        total_revenue = db.session.query(
            db.func.sum(Payment.amount)
        ).filter(Payment.status == 'completed').scalar() or 0.0


        total_users = User.query.count()

        return jsonify({
            "total_dispensed": total_dispensed,
            "total_users": total_users,
            "system_revenue": float(total_revenue)
        }), 200
    
    except Exception as e:
        print(f"Error fetching key metrics: {e}")
        return jsonify({"error":"database error while fetching key metrics"}), 500
    

@admin_bp.route('/users/<int:user_id>/tokens', methods=['PUT'])
@jwt_required()
@admin_required()
def adjust_user_tokens(user_id):
    """Edits a user's token balance"""
    data = request.get_json()
    adjustment_amount = data.get('amount')

    if adjustment_amount is None or not isinstance(adjustment_amount,(int,float)):
        return jsonify({"error": "Invalid or missing 'amount' field."}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error":"User not found."}), 404
    
    try: 
        user_token_record = Token.query.filter_by(user_id=user_id).first()
        if not user_token_record:
            return jsonify({"error": "Token record not found for user."}), 404
        
        user_token_record.balance += adjustment_amount
        db.session.commit()

        return jsonify({
            "message": "Token balance updated successfully.",
            "new_balance": user_token_record.balance
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error adjusting tokens for user {user_id}: {e}")
        return jsonify({"error": "Server error during token update."}), 500
    
@admin_bp.route('/system_logs')
@jwt_required()
@admin_required()
def system_logs_page():
    return render_template('system_logs.html')


    