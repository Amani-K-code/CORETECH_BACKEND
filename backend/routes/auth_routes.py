from flask import Blueprint, request, jsonify
from  .. import db
from ..models.user import User
from flask_jwt_extended import create_access_token
import uuid

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods= ["POST"])
def register():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400
    
    username = data.get("username")
    email = data.get("email")
    password= data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User already exists"}), 400
    
    #new user
    new_user=User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify ({"message": "User registered succesfully"}), 201

    
@auth_bp.route("/login", methods=["POST"])
def login():

    data= request.get_json()

    user= User.query.filter_by(username=data.get("username")).first()
    if not user or not user.check_password(data.get("password")):
        return jsonify({"error": "Invalid username or password"}), 401
    

    is_admin = user.is_admin

    
    token = create_access_token(identity=str(user.id))


    return jsonify({
        "token": token,
        "is_admin":is_admin
        }), 200
