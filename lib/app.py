from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()

from lib.routes import init_routes

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY'] = 'agroconnect-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agroconnect.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    # ✅ Import models so Alembic can detect them
    from lib import models

    # Initialize routes
    init_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
