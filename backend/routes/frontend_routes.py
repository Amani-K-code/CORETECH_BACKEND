from flask import Blueprint, render_template, redirect, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.token import Token
from .. import db
import os
from sqlalchemy import desc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, '..', '..', 'frontend', 'templates')

frontend_bp = Blueprint('frontend', __name__, template_folder=TEMPLATE_FOLDER)

@frontend_bp.route('/')
def home():
    return {"status": "API is operational"}, 200

@frontend_bp.route('/login')
def login():
    return {"status": "API is operational"}, 200

@frontend_bp.route('/register')
def register():
    return {"status": "API is operational"}, 200

@frontend_bp.route('/dashboard')
def dashboard():
    return {"status": "API is operational"}, 200

@frontend_bp.route('/admin_dashboard')
def admin_dashboard():
    return {"status": "API is operational"}, 200

#@frontend_bp.route('/admin/system_logs')
#def system_logs():
#    return render_template('_system_logs.html')

@frontend_bp.route('/_<page_name>.html')
def serve_partial(page_name):
    try:

        return send_from_directory(
            directory=frontend_bp.template_folder,
            path=f'_{page_name}.html'
        )
    except FileNotFoundError:

        return "File not found", 404
