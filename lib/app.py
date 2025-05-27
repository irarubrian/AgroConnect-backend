# lib/app.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Application factory pattern"""
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app, origins=["https://agro-connect-fronted.vercel.app"], supports_credentials=True)

    
    # ======================
    # Configuration Section
    # ======================
    
    # Mandatory security configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise RuntimeError("SECRET_KEY must be set in environment variables")
    
    # PostgreSQL configuration
    db_uri = os.getenv('DATABASE_URL')
    if not db_uri:
        raise RuntimeError("DATABASE_URL must be set in environment variables")
    
    # Fix common URI format issues
    if db_uri.startswith('postgres://'):
        db_uri = db_uri.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Helps with connection recycling
        'pool_recycle': 300,   # Recycle connections after 5 minutes
    }

    # ======================
    # Initialize Extensions
    # ======================
    db.init_app(app)
    migrate.init_app(app, db)

    # ======================
    # Register Blueprints
    # ======================
    from lib.routes import init_routes
    init_routes(app)

    # ======================
    # Shell Context
    # ======================
    @app.shell_context_processor
    def make_shell_context():
        from lib.models import User, Article, Crop, MarketListing, Review, CropActivity, MarketInquiry
        return {
            'db': db,
            'User': User,
            'Article': Article,
            'Crop': Crop,
            'MarketListing': MarketListing,
            'Review': Review,
            'CropActivity': CropActivity,
            'MarketInquiry': MarketInquiry
        }

    return app

# Only for local development
if __name__ == '__main__':
    app = create_app()
    
    # Additional checks for development
    with app.app_context():
        # Verify database connection
        try:
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
    
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')