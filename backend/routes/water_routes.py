from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from datetime import datetime
from ..models.user import User
from ..models.token import Token
from ..models.water import Water
from ..models.water_usage import WaterUsage
from ..models.dispense_log import DispenseLog
from decimal import Decimal

water_bp = Blueprint('water', __name__)

@water_bp.route('/level', methods=['GET'])
def get_water_level():
    """
    Fetches the current water level of the company's main tank
    """
    water_data = Water.query.order_by(Water.last_updated.desc()).first()

    if not water_data:
        #If no water data exists, create an initial entry.
        initial_capacity = 1000000 #1 million litres
        initial_water_tank = Water(capacity_litres=initial_capacity, current_litres = initial_capacity)
        db.session.add(initial_water_tank)
        db.session.commit()
        water_data = initial_water_tank
    
    return jsonify({
            "capacity": float(water_data.capacity_litres),
            "level": float(water_data.current_litres),
            "last_updated": water_data.last_updated.isoformat()
        }), 200



#DISPENSING FUNCTIONALITY:
@water_bp.route('/dispense', methods=['POST'])
@jwt_required()
def dispense_water():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)


    try:
        LITRES_PER_TOKEN = current_app.config['LITRES_PER_TOKEN']
    except KeyError:

        current_app.logger.error("LITRES_PER_TOKEN not found in app config.")
        return jsonify({"msg": "Server configuration error: Water rate undefined."}), 500
    
    if not data or 'litres' not in data:
        return jsonify({'msg': "Missing 'litres' field. "}), 400
    
    try:
        requested_litres_float = float(data.get('litres'))

    except ValueError:
        return jsonify({"msg": "Invalid litres amaount. "}), 400
    
    if requested_litres_float <= 0:
        return jsonify ({"msg": "requested litres must be positive. "}), 400
    requested_litres = Decimal(requested_litres_float)

    tokens_required = Decimal(requested_litres_float) / Decimal(LITRES_PER_TOKEN)

    user = User.query.get(user_id)
    user_token = Token.query.filter_by(user_id = user_id). first()
    company_tank = Water.query.first()

    if not user_token or not user:

        return jsonify({"msg": "User data not found. "}), 404
    

    if user_token.balance < tokens_required:
        return jsonify({
            "msg": f"Insufficient tokens. You need {tokens_required:.2} tokens for {requested_litres: .2f}L.",
            "available_tokens": user_token.balance
        }), 403
    
    if not company_tank or company_tank.current_litres < requested_litres:
        return jsonify({"msg": "Insufficient water in the main tank. Cannot dispense."}), 503
    
    user_token.balance -= tokens_required
    company_tank.current_litres -= requested_litres

    current_litres_dispensed = Decimal(user.litres_dispensed) if user.litres_dispensed is not None else Decimal(0)
    user.litres_dispensed = current_litres_dispensed + requested_litres

    new_usage = WaterUsage(
        user_id=user_id,
        litres_dispensed = requested_litres,
        tokens_used=tokens_required
    )

    db.session.add(new_usage)

    machine_id = data.get('machine_id', 'MOCK_MACHINE_01')

    new_dispense_log = DispenseLog(
        user_id=user_id,
        litres_dispensed = requested_litres,
        tokens_consumed=tokens_required,
        machine_id=machine_id
    )
    db.session.add(new_dispense_log)

    db.session.commit()

    return jsonify({
        "msg": f"Dispensed {requested_litres:.2f}L using {tokens_required:.2f} tokens.",
        "new_token_balance": user_token.balance
    }), 200

@water_bp.route('usage/history', methods=['GET'])
@jwt_required()
def get_usage_history():
    user_id = get_jwt_identity()

    usage_records = WaterUsage.query.filter_by(user_id=user_id) \
                                    .order_by(WaterUsage.timestamp.desc()) \
                                    .limit(30).all()
    data= [record.to_dict() for record in reversed(usage_records)]

    return jsonify({"history": data}), 200

 