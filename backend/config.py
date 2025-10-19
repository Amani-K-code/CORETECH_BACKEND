# config.py (Corrected)
from dotenv import load_dotenv
import os


ADMIN_DOMAINS = [
    "coretech.org", #current admin domain
]

# 🛑 CRITICAL FIX: The DATABASE_URL definition is removed from config.py 
# as it conflicts with the environment loading logic in run.py.

SECRET_KEY = os.environ.get("SECRET_KEY","supersecretkey")

TOKEN_RATE = 1.0
LITRES_PER_TOKEN = 1.0