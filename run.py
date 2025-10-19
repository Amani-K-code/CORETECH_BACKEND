import os
import sys
from backend import config
from dotenv import load_dotenv
from backend import create_app, db
from flask_migrate import Migrate
from backend.models.user import User
from backend.models.token import Token
from backend.models.water import Water


# Determine which environment file to use based on command line arguments
is_cloud = (len(sys.argv) > 1 and sys.argv[1] == "cloud")
env_file = ".env.cloud" if is_cloud else ".env.local"

# Load environment variables from the selected file.
load_dotenv(dotenv_path=env_file, override=True) 

# Get the URI from the environment (either from .env.cloud or .env.local)
database_uri = os.environ.get('DATABASE_URL')
jwt_secret_key = os.environ.get('JWT_SECRET_KEY')


if not database_uri and not is_cloud:
    print("Warning: DATABASE_URL not found in .env.local. Using hardcoded default.")
    database_uri = (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}"
        f":{os.getenv('DB_PASSWORD', 'Kamugi')}"
        f"@{os.getenv('DB_HOST', 'localhost')}"
        f":{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'davis_water')}"
    )

# Exit if required environment variables are not found
if not database_uri:
    # This should now only trigger if both the .env file and the hardcoded default fail
    print(f"Error: DATABASE_URL not found in {env_file} and no local default available.")
    sys.exit(1)

if not jwt_secret_key:
    print(f"Error: JWT_SECRET_KEY not found in {env_file}")
    sys.exit(1)

# Create the application instance by calling the factory function
app = create_app(database_uri, jwt_secret_key)

#safe
app.config.from_object(config) 

# Initialize Flask-Migrate with the app and db instance
migrate = Migrate(app, db)

if __name__ == "__main__":
    # Run the application in debug mode
    with app.app_context():
        pass
    app.run(debug=True , port=5001)