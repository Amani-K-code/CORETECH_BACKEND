from flask import jsonify
from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from  ..models.user import User

def admin_required():
    """
    Checks whether logged in user is an admmin

    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({"error": "User not found"}), 404
            

            if not user.is_admin:
                return jsonify({"error": "Forbidden: Admin access required"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
