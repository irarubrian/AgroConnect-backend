# seed.py

from lib.app import create_app, db
from lib.models import User, Crop, CropActivity, MarketListing, MarketInquiry, Article, Review
from werkzeug.security import generate_password_hash
import datetime

app = create_app()

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users
        admin = User(
            username='admin',
            email='admin@agroconnect.com',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin',
            location='Nairobi',
            phone='254712345678'
        )
        
        farmer1 = User(
            username='farmer_john',
            email='john@example.com',
            password=generate_password_hash('farmer123', method='pbkdf2:sha256'),
            role='farmer',
            location='Kiambu',
            phone='254712345679'
        )
        
        farmer2 = User(
            username='farmer_mary',
            email='mary@example.com',
            password=generate_password_hash('farmer123', method='pbkdf2:sha256'),
            role='farmer',
            location='Muranga',
            phone='254712345680'
        )
        
        buyer1 = User(
            username='buyer_co',
            email='buyer@example.com',
            password=generate_password_hash('buyer123', method='pbkdf2:sha256'),
            role='buyer',
            location='Nairobi',
            phone='254712345681'
        )
        
        expert1 = User(
            username='agro_expert',
            email='expert@example.com',
            password=generate_password_hash('expert123', method='pbkdf2:sha256'),
            role='expert',
            location='Nairobi',
            phone='254712345682'
        )
        
        db.session.add_all([admin, farmer1, farmer2, buyer1, expert1])
        db.session.commit()
        
        # Create crops
        maize_crop = Crop(
            farmer_id=farmer1.id,
            crop_type='Maize',
            variety='DH04',
            planting_date=datetime.datetime(2023, 3, 15),
            harvest_date=datetime.datetime(2023, 8, 20),
            growth_stage='flowering',
            soil_type='clay loam',
            irrigation_method='drip',
            notes='Planted in field 3'
        )
        
        tomato_crop = Crop(
            farmer_id=farmer2.id,
            crop_type='Tomato',
            variety='Roma',
            planting_date=datetime.datetime(2023, 4, 1),
            harvest_date=datetime.datetime(2023, 7, 15),
            growth_stage='fruiting',
            soil_type='sandy loam',
            irrigation_method='sprinkler',
            notes='Greenhouse 2'
        )
        
        db.session.add_all([maize_crop, tomato_crop])
        db.session.commit()
        
        # Create crop activities
        maize_planting = CropActivity(
            crop_id=maize_crop.id,
            activity_type='planting',
            date=datetime.datetime(2023, 3, 15),
            description='Planted maize seeds',
            products_used='Maize seeds DH04',
            quantity='20kg',
            cost=1500.00
        )
        
        maize_fertilizing = CropActivity(
            crop_id=maize_crop.id,
            activity_type='fertilizing',
            date=datetime.datetime(2023, 4, 10),
            description='Applied DAP fertilizer',
            products_used='DAP fertilizer',
            quantity='50kg',
            cost=2500.00
        )
        
        db.session.add_all([maize_planting, maize_fertilizing])
        db.session.commit()
        
        # Create market listings
        maize_listing = MarketListing(
            farmer_id=farmer1.id,
            crop_type='Maize',
            variety='DH04',
            quantity=1000,
            unit='kg',
            price_per_unit=50,
            location='Kiambu',
            harvest_date=datetime.datetime(2023, 8, 20),
            organic=False,
            status='approved'
        )
        
        tomato_listing = MarketListing(
            farmer_id=farmer2.id,
            crop_type='Tomato',
            variety='Roma',
            quantity=500,
            unit='kg',
            price_per_unit=80,
            location='Muranga',
            harvest_date=datetime.datetime(2023, 7, 15),
            organic=True,
            status='approved'
        )
        
        db.session.add_all([maize_listing, tomato_listing])
        db.session.commit()
        
        # Create market inquiries
        maize_inquiry = MarketInquiry(
            listing_id=maize_listing.id,
            buyer_id=buyer1.id,
            message='Interested in your maize. Can you deliver to Nairobi?',
            quantity_requested=200,
            counter_price=45,
            status='pending'
        )
        
        db.session.add(maize_inquiry)
        db.session.commit()
        
        # Create articles
        pest_article = Article(
            expert_id=expert1.id,
            title='Managing Fall Armyworm in Maize',
            content='Comprehensive guide on identifying and controlling fall armyworm...',
            category='pest_control',
            approved=True
        )
        
        soil_article = Article(
            expert_id=expert1.id,
            title='Improving Soil Fertility Naturally',
            content='Methods for improving soil fertility without chemical fertilizers...',
            category='soil_health',
            approved=True
        )
        
        db.session.add_all([pest_article, soil_article])
        db.session.commit()
        
        # Create reviews
        review1 = Review(
            user_id=buyer1.id,
            farmer_id=farmer1.id,
            rating=4,
            comment='Good quality maize, timely delivery'
        )
        
        db.session.add(review1)
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
