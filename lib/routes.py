
from flask import Flask, jsonify, request, current_app
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from lib.models import db, User, Crop, MarketListing, Article, Review, MarketInquiry, CropActivity

@app.route('/', methods=['GET'])
def index():
    return {"message": "Backend is alive!"}, 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated

def init_routes(app):
    @app.route('/')
    def index():
        return jsonify({'message': 'AgroConnect API'})

    # Auth Routes
    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists!'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists!'}), 400
            
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashed_password,
            role=data['role'],
            location=data.get('location', ''),
            phone=data.get('phone', '')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully!'}), 201

    @app.route('/login', methods=['POST'])
    def login():
        auth = request.get_json()
        
        if not auth or not auth['username'] or not auth['password']:
            return jsonify({'message': 'Could not verify'}), 401
            
        user = User.query.filter_by(username=auth['username']).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        if check_password_hash(user.password, auth['password']):
            token = jwt.encode({
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'location': user.location,
                    'phone': user.phone
                }
            })
            
        return jsonify({'message': 'Wrong credentials'}), 401

    # User Routes
    @app.route('/users', methods=['GET'])
    @token_required
    def get_all_users(current_user):
        if current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'}), 403
            
        users = User.query.all()
        output = []
        
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'location': user.location,
                'phone': user.phone
            }
            output.append(user_data)
            
        return jsonify({'users': output})

    @app.route('/users/<int:user_id>', methods=['GET'])
    @token_required
    def get_one_user(current_user, user_id):
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found!'}), 404
            
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'location': user.location,
            'phone': user.phone
        }
        
        return jsonify({'user': user_data})

    # Crop Routes
    @app.route('/crops', methods=['POST'])
    @token_required
    def create_crop(current_user):
        if current_user.role != 'farmer':
            return jsonify({'message': 'Only farmers can create crops!'}), 403
            
        data = request.get_json()
        
        new_crop = Crop(
            farmer_id=current_user.id,
            crop_type=data['crop_type'],
            variety=data.get('variety', ''),
            planting_date=datetime.datetime.strptime(data['planting_date'], '%Y-%m-%d'),
            harvest_date=datetime.datetime.strptime(data['harvest_date'], '%Y-%m-%d') if data.get('harvest_date') else None,
            growth_stage=data.get('growth_stage', 'planting'),
            soil_type=data.get('soil_type', ''),
            irrigation_method=data.get('irrigation_method', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(new_crop)
        db.session.commit()
        
        return jsonify({'message': 'Crop created successfully!'}), 201

    @app.route('/crops', methods=['GET'])
    @token_required
    def get_all_crops(current_user):
        if current_user.role == 'farmer':
            crops = Crop.query.filter_by(farmer_id=current_user.id).all()
        else:
            crops = Crop.query.all()
            
        output = []
        
        for crop in crops:
            crop_data = {
                'id': crop.id,
                'farmer_id': crop.farmer_id,
                'crop_type': crop.crop_type,
                'variety': crop.variety,
                'planting_date': crop.planting_date.strftime('%Y-%m-%d'),
                'harvest_date': crop.harvest_date.strftime('%Y-%m-%d') if crop.harvest_date else None,
                'growth_stage': crop.growth_stage,
                'soil_type': crop.soil_type,
                'irrigation_method': crop.irrigation_method,
                'notes': crop.notes
            }
            output.append(crop_data)
            
        return jsonify({'crops': output})
    

    @app.route('/crops/<int:crop_id>', methods=['GET'])
    @token_required
    def get_crop(current_user, crop_id):
        crop = Crop.query.filter_by(id=crop_id).first()
        
        if not crop:
            return jsonify({'message': 'Crop not found!'}), 404
            
        if current_user.role == 'farmer' and crop.farmer_id != current_user.id:
            return jsonify({'message': 'You can only view your own crops!'}), 403
            
        crop_data = {
            'id': crop.id,
            'farmer_id': crop.farmer_id,
            'crop_type': crop.crop_type,
            'variety': crop.variety,
            'planting_date': crop.planting_date.strftime('%Y-%m-%d'),
            'harvest_date': crop.harvest_date.strftime('%Y-%m-%d') if crop.harvest_date else None,
            'growth_stage': crop.growth_stage,
            'soil_type': crop.soil_type,
            'irrigation_method': crop.irrigation_method,
            'notes': crop.notes
        }
        
        return jsonify({'crop': crop_data})

    @app.route('/crops/<int:crop_id>', methods=['PUT'])
    @token_required
    def update_crop(current_user, crop_id):
        crop = Crop.query.filter_by(id=crop_id).first()
        
        if not crop:
            return jsonify({'message': 'Crop not found!'}), 404
            
        if crop.farmer_id != current_user.id:
            return jsonify({'message': 'You can only update your own crops!'}), 403
            
        data = request.get_json()
        
        crop.crop_type = data.get('crop_type', crop.crop_type)
        crop.variety = data.get('variety', crop.variety)
        if 'planting_date' in data:
            crop.planting_date = datetime.datetime.strptime(data['planting_date'], '%Y-%m-%d')
        if 'harvest_date' in data:
            crop.harvest_date = datetime.datetime.strptime(data['harvest_date'], '%Y-%m-%d') if data['harvest_date'] else None
        crop.growth_stage = data.get('growth_stage', crop.growth_stage)
        crop.soil_type = data.get('soil_type', crop.soil_type)
        crop.irrigation_method = data.get('irrigation_method', crop.irrigation_method)
        crop.notes = data.get('notes', crop.notes)
        
        db.session.commit()
        
        return jsonify({'message': 'Crop updated successfully!'})

    @app.route('/crops/<int:crop_id>', methods=['DELETE'])
    @token_required
    def delete_crop(current_user, crop_id):
        crop = Crop.query.filter_by(id=crop_id).first()
        
        if not crop:
            return jsonify({'message': 'Crop not found!'}), 404
            
        if crop.farmer_id != current_user.id:
            return jsonify({'message': 'You can only delete your own crops!'}), 403
            
        db.session.delete(crop)
        db.session.commit()
        
        return jsonify({'message': 'Crop deleted successfully!'})

    # Crop Activity Routes
    @app.route('/crops/<int:crop_id>/activities', methods=['POST'])
    @token_required
    def create_activity(current_user, crop_id):
        crop = Crop.query.filter_by(id=crop_id).first()
        
        if not crop:
            return jsonify({'message': 'Crop not found!'}), 404
            
        if crop.farmer_id != current_user.id:
            return jsonify({'message': 'You can only add activities to your own crops!'}), 403
            
        data = request.get_json()
        
        new_activity = CropActivity(
            crop_id=crop_id,
            activity_type=data['activity_type'],
            date=datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
            description=data.get('description', ''),
            products_used=data.get('products_used', ''),
            quantity=data.get('quantity', ''),
            cost=data.get('cost', 0.0)
        )
        
        db.session.add(new_activity)
        db.session.commit()
        
        return jsonify({'message': 'Activity created successfully!'}), 201

    @app.route('/crops/<int:crop_id>/activities', methods=['GET'])
    @token_required
    def get_crop_activities(current_user, crop_id):
        crop = Crop.query.filter_by(id=crop_id).first()
        
        if not crop:
            return jsonify({'message': 'Crop not found!'}), 404
            
        if current_user.role == 'farmer' and crop.farmer_id != current_user.id:
            return jsonify({'message': 'You can only view activities for your own crops!'}), 403
            
        activities = CropActivity.query.filter_by(crop_id=crop_id).all()
        output = []
        
        for activity in activities:
            activity_data = {
                'id': activity.id,
                'crop_id': activity.crop_id,
                'activity_type': activity.activity_type,
                'date': activity.date.strftime('%Y-%m-%d'),
                'description': activity.description,
                'products_used': activity.products_used,
                'quantity': activity.quantity,
                'cost': activity.cost
            }
            output.append(activity_data)
            
        return jsonify({'activities': output})

    # Market Listing Routes
    @app.route('/listings', methods=['POST'])
    @token_required
    def create_listing(current_user):
        if current_user.role != 'farmer':
            return jsonify({'message': 'Only farmers can create listings!'}), 403
            
        data = request.get_json()
        
        new_listing = MarketListing(
            farmer_id=current_user.id,
            crop_type=data['crop_type'],
            variety=data.get('variety', ''),
            quantity=data['quantity'],
            unit=data['unit'],
            price_per_unit=data['price_per_unit'],
            location=data['location'],
            harvest_date=datetime.datetime.strptime(data['harvest_date'], '%Y-%m-%d') if data.get('harvest_date') else None,
            organic=data.get('organic', False)
        )
        
        db.session.add(new_listing)
        db.session.commit()
        
        return jsonify({'message': 'Listing created successfully!'}), 201

    @app.route('/listings', methods=['GET'])
    def get_all_listings():
        listings = MarketListing.query.filter_by(status='approved').all()
        output = []
        
        for listing in listings:
            listing_data = {
                'id': listing.id,
                'farmer_id': listing.farmer_id,
                'crop_type': listing.crop_type,
                'variety': listing.variety,
                'quantity': listing.quantity,
                'unit': listing.unit,
                'price_per_unit': listing.price_per_unit,
                'location': listing.location,
                'harvest_date': listing.harvest_date.strftime('%Y-%m-%d') if listing.harvest_date else None,
                'organic': listing.organic,
                'status': listing.status,
                'created_at': listing.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            output.append(listing_data)
            
        return jsonify({'listings': output})

    @app.route('/listings/<int:listing_id>', methods=['GET'])
    def get_listing(listing_id):
        listing = MarketListing.query.filter_by(id=listing_id).first()
        
        if not listing:
            return jsonify({'message': 'Listing not found!'}), 404
            
        listing_data = {
            'id': listing.id,
            'farmer_id': listing.farmer_id,
            'crop_type': listing.crop_type,
            'variety': listing.variety,
            'quantity': listing.quantity,
            'unit': listing.unit,
            'price_per_unit': listing.price_per_unit,
            'location': listing.location,
            'harvest_date': listing.harvest_date.strftime('%Y-%m-%d') if listing.harvest_date else None,
            'organic': listing.organic,
            'status': listing.status,
            'created_at': listing.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({'listing': listing_data})

    # Market Inquiry Routes
    @app.route('/listings/<int:listing_id>/inquiries', methods=['POST'])
    @token_required
    def create_inquiry(current_user, listing_id):
        if current_user.role != 'buyer':
            return jsonify({'message': 'Only buyers can create inquiries!'}), 403
            
        listing = MarketListing.query.filter_by(id=listing_id).first()
        
        if not listing:
            return jsonify({'message': 'Listing not found!'}), 404
            
        if listing.status != 'approved':
            return jsonify({'message': 'You can only inquire about approved listings!'}), 400
            
        data = request.get_json()
        
        new_inquiry = MarketInquiry(
            listing_id=listing_id,
            buyer_id=current_user.id,
            message=data['message'],
            quantity_requested=data.get('quantity_requested'),
            counter_price=data.get('counter_price')
        )
        
        db.session.add(new_inquiry)
        db.session.commit()
        
        return jsonify({'message': 'Inquiry created successfully!'}), 201

    @app.route('/listings/<int:listing_id>/inquiries', methods=['GET'])
    @token_required
    def get_listing_inquiries(current_user, listing_id):
        listing = MarketListing.query.filter_by(id=listing_id).first()
        
        if not listing:
            return jsonify({'message': 'Listing not found!'}), 404
            
        # Only the farmer who owns the listing or admin can see inquiries
        if current_user.id != listing.farmer_id and current_user.role != 'admin':
            return jsonify({'message': 'You can only view inquiries for your own listings!'}), 403
            
        inquiries = MarketInquiry.query.filter_by(listing_id=listing_id).all()
        output = []
        
        for inquiry in inquiries:
            inquiry_data = {
                'id': inquiry.id,
                'listing_id': inquiry.listing_id,
                'buyer_id': inquiry.buyer_id,
                'message': inquiry.message,
                'quantity_requested': inquiry.quantity_requested,
                'counter_price': inquiry.counter_price,
                'status': inquiry.status,
                'created_at': inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            output.append(inquiry_data)
            
        return jsonify({'inquiries': output})

    # Article Routes
    @app.route('/articles', methods=['POST'])
    @token_required
    def create_article(current_user):
        if current_user.role not in ['expert', 'admin']:
            return jsonify({'message': 'Only experts and admins can create articles!'}), 403
            
        data = request.get_json()
        
        new_article = Article(
            expert_id=current_user.id,
            title=data['title'],
            content=data['content'],
            category=data['category'],
            approved=(current_user.role == 'admin')
        )
        
        db.session.add(new_article)
        db.session.commit()
        
        return jsonify({'message': 'Article created successfully!'}), 201

    @app.route('/articles', methods=['GET'])
    def get_all_articles():
        articles = Article.query.filter_by(approved=True).all()
        output = []
        
        for article in articles:
            article_data = {
                'id': article.id,
                'expert_id': article.expert_id,
                'title': article.title,
                'content': article.content,
                'category': article.category,
                'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            output.append(article_data)
            
        return jsonify({'articles': output})

    @app.route('/articles/<int:article_id>', methods=['GET'])
    def get_article(article_id):
        article = Article.query.filter_by(id=article_id, approved=True).first()
        
        if not article:
            return jsonify({'message': 'Article not found or not approved!'}), 404
            
        article_data = {
            'id': article.id,
            'expert_id': article.expert_id,
            'title': article.title,
            'content': article.content,
            'category': article.category,
            'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({'article': article_data})

    # Review Routes
    @app.route('/farmers/<int:farmer_id>/reviews', methods=['POST'])
    @token_required
    def create_review(current_user, farmer_id):
        if current_user.role != 'buyer':
            return jsonify({'message': 'Only buyers can create reviews!'}), 403
            
        farmer = User.query.filter_by(id=farmer_id, role='farmer').first()
        
        if not farmer:
            return jsonify({'message': 'Farmer not found!'}), 404
            
        data = request.get_json()
        
        # Check if the user has already reviewed this farmer
        existing_review = Review.query.filter_by(user_id=current_user.id, farmer_id=farmer_id).first()
        if existing_review:
            return jsonify({'message': 'You have already reviewed this farmer!'}), 400
            
        new_review = Review(
            user_id=current_user.id,
            farmer_id=farmer_id,
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        return jsonify({'message': 'Review created successfully!'}), 201

    @app.route('/farmers/<int:farmer_id>/reviews', methods=['GET'])
    def get_farmer_reviews(farmer_id):
        farmer = User.query.filter_by(id=farmer_id, role='farmer').first()
        
        if not farmer:
            return jsonify({'message': 'Farmer not found!'}), 404
            
        reviews = Review.query.filter_by(farmer_id=farmer_id).all()
        output = []
        
        for review in reviews:
            review_data = {
                'id': review.id,
                'user_id': review.user_id,
                'farmer_id': review.farmer_id,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            output.append(review_data)
            
        return jsonify({'reviews': output})

    # Admin Routes
    @app.route('/admin/listings', methods=['GET'])
    @token_required
    def get_pending_listings(current_user):
        if current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'}), 403
            
        listings = MarketListing.query.filter_by(status='pending').all()
        output = []
        
        for listing in listings:
            listing_data = {
                'id': listing.id,
                'farmer_id': listing.farmer_id,
                'crop_type': listing.crop_type,
                'variety': listing.variety,
                'quantity': listing.quantity,
                'unit': listing.unit,
                'price_per_unit': listing.price_per_unit,
                'location': listing.location,
                'harvest_date': listing.harvest_date.strftime('%Y-%m-%d') if listing.harvest_date else None,
                'organic': listing.organic,
                'status': listing.status,
                'created_at': listing.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            output.append(listing_data)
            
        return jsonify({'listings': output})

    @app.route('/admin/listings/<int:listing_id>/approve', methods=['PUT'])
    @token_required
    def approve_listing(current_user, listing_id):
        if current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'}), 403
            
        listing = MarketListing.query.filter_by(id=listing_id).first()
        
        if not listing:
            return jsonify({'message': 'Listing not found!'}), 404
            
        listing.status = 'approved'
        db.session.commit()
        
        return jsonify({'message': 'Listing approved successfully!'})

    @app.route('/admin/listings/<int:listing_id>/reject', methods=['PUT'])
    @token_required
    def reject_listing(current_user, listing_id):
        if current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'}), 403
            
        listing = MarketListing.query.filter_by(id=listing_id).first()
        
        if not listing:
            return jsonify({'message': 'Listing not found!'}), 404
            
        listing.status = 'rejected'
        db.session.commit()
        
        return jsonify({'message': 'Listing rejected successfully!'})

    @app.route('/admin/articles', methods=['GET'])
    @token_required
    def get_pending_articles(current_user):
        if current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'}), 403
            
        articles = Article.query.filter_by(approved=False).all()
        output = []
        
        for article in articles:
            article_data = {
                'id': article.id,
                'expert_id': article.expert_id,
                'title': article.title,
                'content': article.content,
                'category': article.category,
                'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            output.append(article_data)
            
        return jsonify({'articles': output})

    @app.route('/admin/articles/<int:article_id>/approve', methods=['PUT'])
    @token_required
    def approve_article(current_user, article_id):
        if current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'}), 403
            
        article = Article.query.filter_by(id=article_id).first()
        
        if not article:
            return jsonify({'message': 'Article not found!'}), 404
            
        article.approved = True
        db.session.commit()
        
        return jsonify({'message': 'Article approved successfully!'})

    @app.route('/admin/articles/<int:article_id>/reject', methods=['DELETE'])
    @token_required
    def reject_article(current_user, article_id):
        if current_user.role != 'admin':
            return jsonify({'message': 'Cannot perform that function!'}), 403
            
        article = Article.query.filter_by(id=article_id).first()
        
        if not article:
            return jsonify({'message': 'Article not found!'}), 404
            
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({'message': 'Article rejected and deleted successfully!'})