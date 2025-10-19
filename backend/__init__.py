import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv

# Initialize extensions outside the factory function
# This allows them to be used across the application without
# being tied to a specific app instance.
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()


def create_app(database_uri, jwt_secret_key):
    """
    Factory function to create the Flask application instance.
    
    Args:
        database_uri (str): The connection string for the database.
        jwt_secret_key (str): The secret key for JWT authentication.
    
    Returns:
        Flask: The configured Flask application object.
    """
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')


    # Configure the application using the provided arguments
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Use the passed-in secret key for JWT, which is more explicit
    app.config["JWT_SECRET_KEY"] = jwt_secret_key

    # Configure SQLAlchemy engine options for better connection handling
    if "supabase" in database_uri or "amazonaws.com" in database_uri:
        # Append SSL requirement directly to the URI
        if 'sslmode=' not in database_uri:
            app.config["SQLALCHEMY_DATABASE_URI"] += "?sslmode=require"
            
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Initialize extensions with the application instance
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app,db)

    # Import and register blueprints and models
    # Note: These imports assume a specific folder structure.
    from .models.user import User
    from .models.token import Token
    from .models.water_usage import WaterUsage
    from .models.water import Water
    from .models.dispense_log import DispenseLog
    
    from .routes.auth_routes import auth_bp
    from .routes.token_routes import token_bp
    from .routes.frontend_routes import frontend_bp
    from .routes.water_routes import water_bp
    from .routes.user_routes import user_bp
    from .routes.payment_routes import payment_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(token_bp, url_prefix="/tokens")
    app.register_blueprint(frontend_bp)
    app.register_blueprint(water_bp,url_prefix="/water")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
    # A simple health check endpoint to verify database connection
    @app.get("/_dbcheck")
    def _dbcheck():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"ok": True}), 200
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    return app