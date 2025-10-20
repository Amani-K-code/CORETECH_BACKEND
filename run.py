import os
import sys
from flask_cors import CORS
from backend import create_app, db
from flask_migrate import Migrate
from dotenv import load_dotenv

# --- Production Deployment Change: Simplify Environment Loading ---
# Load .env for LOCAL execution only. Render/production sets these variables directly.
# This assumes you use a .env.local file for local development secrets
if os.environ.get('FLASK_ENV') != 'production':
    load_dotenv(dotenv_path='.env.local', override=True) 

# Get the necessary variables from the environment
# Render provides DATABASE_URL and you must set JWT_SECRET_KEY
database_uri = os.environ.get('DATABASE_URL')
jwt_secret_key = os.environ.get('JWT_SECRET_KEY')

# FIX: Update the default URL to your live Vercel domain for local testing convenience
frontend_url = os.environ.get('FRONTEND_URL', 'https://coretech-frontend.vercel.app') 

# --- CRITICAL: Validation for Production ---
if not database_uri:
    print("Error: DATABASE_URL environment variable not found. Check Render environment variables or .env.local.")
    sys.exit(1)

if not jwt_secret_key:
    print("Error: JWT_SECRET_KEY environment variable not found. Check Render environment variables or .env.local.")
    sys.exit(1)

# Create the application instance by calling the factory function
app = create_app(database_uri, jwt_secret_key)

# --- Production Fix: CORS initialization MUST be after app creation ---
# This allows requests ONLY from your Vercel frontend domain (or the local default)
CORS(app, resources={r"/*": {"origins": frontend_url}})


# Initialize Flask-Migrate with the app and db instance
migrate = Migrate(app, db)

# Define models to be visible to Flask-Migrate 
from backend.models.user import User
from backend.models.token import Token
from backend.models.water import Water

if __name__ == "__main__":
    # This block is for local testing only (Gunicorn will run the app in production)
    with app.app_context():
        # Optional: Run any setup here if needed
        pass
    app.run(debug=True, port=5001)