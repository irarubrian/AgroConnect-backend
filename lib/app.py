# lib/app.py
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Application factory pattern"""

    load_dotenv()
    
    
    app = Flask(__name__)
    
    CORS(app,
        origins=[
            "https://agro-connect-fronted.vercel.app",  
            "http://localhost:5173",                   
            "http://127.0.0.1:5173",                   
            "http://localhost:3000",                   
            "http://127.0.0.1:3000"    
        ],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "x-access-token"],
        expose_headers=["Content-Type", "X-Total-Count"],
        max_age=600
    )


    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='None',
        REMEMBER_COOKIE_SECURE=True,
        REMEMBER_COOKIE_SAMESITE='None',
        PREFERRED_URL_SCHEME='https' 
    )
    
    if not app.config['SECRET_KEY']:
        raise RuntimeError("SECRET_KEY must be set in environment variables")

    # ======================
    # Database Configuration
    # ======================
    db_uri = os.getenv('DATABASE_URL')
    if not db_uri:
        raise RuntimeError("DATABASE_URL must be set in environment variables")
    
    # Fix common URI format issues
    if db_uri.startswith('postgres://'):
        db_uri = db_uri.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 30
    }

    
    db.init_app(app)
    migrate.init_app(app, db)

   
    @app.before_request
    def before_request():
        """Log all incoming requests"""
        app.logger.info(f"Incoming {request.method} request to {request.url}")

    @app.after_request
    def after_request(response):
        """Add security headers to all responses"""
        response.headers.update({
            'Access-Control-Allow-Credentials': 'true',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload'
        })
        return response

    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    # ======================
    # Register Blueprints
    # ======================
    from lib.routes import init_routes
    init_routes(app)

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

# Application entry point
if __name__ == '__main__':
    app = create_app()
    
    
    with app.app_context():
        # Verify database connection
        try:
            db.engine.execute("SELECT 1")
            app.logger.info("✅ Database connection successful")
        except Exception as e:
            app.logger.error(f" Database connection failed: {str(e)}")
    
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )