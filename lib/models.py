
from datetime import datetime
from lib.app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # farmer, buyer, expert, admin
    location = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    crops = db.relationship('Crop', backref='farmer', lazy=True)
    listings = db.relationship('MarketListing', backref='farmer', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True, foreign_keys='Review.user_id')
    reviews_received = db.relationship('Review', backref='farmer', lazy=True, foreign_keys='Review.farmer_id')

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crop_type = db.Column(db.String(80), nullable=False)
    variety = db.Column(db.String(80))
    planting_date = db.Column(db.DateTime, nullable=False)
    harvest_date = db.Column(db.DateTime)
    growth_stage = db.Column(db.String(50))
    soil_type = db.Column(db.String(80))
    irrigation_method = db.Column(db.String(80))
    notes = db.Column(db.Text)
    activities = db.relationship('CropActivity', backref='crop', lazy=True)

class CropActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    activity_type = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    products_used = db.Column(db.String(200))
    quantity = db.Column(db.String(50))
    cost = db.Column(db.Float)

class MarketListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crop_type = db.Column(db.String(80), nullable=False)
    variety = db.Column(db.String(80))
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    harvest_date = db.Column(db.DateTime)
    organic = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    inquiries = db.relationship('MarketInquiry', backref='listing', lazy=True)

class MarketInquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('market_listing.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    quantity_requested = db.Column(db.Float)
    counter_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)