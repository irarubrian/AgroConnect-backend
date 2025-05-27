from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os  # ⬅️ NEW IMPORT

db = SQLAlchemy()

from lib.routes import init_routes

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 🔒 UPDATED CONFIG (PostgreSQL + environment variables)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key')  # Never hardcode in production!
    
    # 🐘 POSTGRESQL CONFIG (Render's internal URL format)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///agroconnect.db'  # Fallback for local dev
    ).replace('postgres://', 'postgresql://')  # Essential for Render
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    # ✅ Import models (keep this)
    from lib import models

    # Initialize routes
    init_routes(app)

    return app

# 👇 ONLY FOR LOCAL DEVELOPMENT (remove in production)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)