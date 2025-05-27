# wsgi.py

from dotenv import load_dotenv
from pathlib import Path
import os

# Explicitly load .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print("Environment loaded successfully!")
else:
    print("Warning: .env file not found!")

from lib.app import create_app

# Create the app instance
app = create_app()
