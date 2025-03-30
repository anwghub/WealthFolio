from flask import Blueprint, request, jsonify
from models import Category
from models import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware import verify_client_credentials

categories_bp = Blueprint('categories_bp', __name__)

@categories_bp.route('/initialize', methods=['POST'])
@verify_client_credentials
@jwt_required()
def initialize_default_categories():
    current_user_id = get_jwt_identity()
    
    print(f"Initializing categories for user {current_user_id}")

    try:
        default_categories = [
            {'name': 'Food', 'description': 'Food and dining expenses'},
            {'name': 'Transportation', 'description': 'Transportation expenses'},
            {'name': 'Entertainment', 'description': 'Entertainment expenses'},
            {'name': 'Shopping', 'description': 'Shopping expenses'},
            {'name': 'Bills', 'description': 'Monthly bills and utilities'},
            {'name': 'Salary', 'description': 'Income from salary'},
            {'name': 'Other', 'description': 'Miscellaneous expenses'},
        ]
        
        created_categories = []
        
        for category_data in default_categories:
            # Check if category already exists for this user
            existing = Category.query.filter_by(
                UserId=current_user_id,
                category_name=category_data['name']
            ).first()
            
            if not existing:
                new_category = Category(
                    UserId=current_user_id,
                    category_name=category_data['name'],
                    Description=category_data['description']
                )
                db.session.add(new_category)
                created_categories.append(category_data['name'])
        
        if created_categories:
            db.session.commit()
            return jsonify({
                'message': 'Default categories created',
                'categories': created_categories
            }), 201
        else:
            return jsonify({'message': 'Default categories already exist'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing categories: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@categories_bp.route('', methods=['GET'])
@verify_client_credentials
@jwt_required()
def get_categories():
    current_user_id = get_jwt_identity()
    
    # Retrieve categories for current user
    categories = Category.query.filter_by(UserId=current_user_id).all()
    
    category_list = [{
        'CategoryId': category.CategoryId,
        'UserId': category.UserId,
        'category_name': category.category_name,
        'description': category.Description,
    } for category in categories]
    
    return jsonify(category_list), 200

@categories_bp.route('/<int:category_id>', methods=['GET'])
@verify_client_credentials
@jwt_required()
def get_category(category_id):
    current_user_id = get_jwt_identity()
    
    # Ensure category belongs to the current user
    category = Category.query.filter_by(
        CategoryId=category_id,
        UserId=current_user_id
    ).first_or_404()
    
    category_data = {
        'CategoryId': category.CategoryId,
        'UserId': category.UserId,
        'category_name': category.category_name,
        'description': category.Description,
        'CreatedAt': category.CreatedAt,
        'UpdatedAt': category.UpdatedAt
    }
    return jsonify(category_data), 200

@categories_bp.route('', methods=['POST'])
@verify_client_credentials
@jwt_required()
def create_category():
    current_user_id = get_jwt_identity()
    data = request.json
    
    if not data or 'category_name' not in data:
        return jsonify({"error": "Category name is required"}), 400
    
    category_name = data.get('category_name')
    description = data.get('description', '')
    
    # Check for duplicate category name for the user
    if Category.query.filter_by(category_name=category_name, UserId=current_user_id).first():
        return jsonify({"error": "Category name already exists for this user"}), 409
    
    new_category = Category(
        UserId=current_user_id,  # Get user ID from JWT token
        category_name=category_name,
        Description=description
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category created', 'CategoryId': new_category.CategoryId}), 201

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@verify_client_credentials
@jwt_required()
def update_category(category_id):
    current_user_id = get_jwt_identity()
    
    # Ensure category belongs to the current user
    category = Category.query.filter_by(
        CategoryId=category_id,
        UserId=current_user_id
    ).first_or_404()
    
    data = request.json
    category_name = data.get('category_name')
    description = data.get('description')
    
    if category_name:
        # Ensure no duplicate category name for this user
        existing_category = Category.query.filter_by(
            category_name=category_name, 
            UserId=current_user_id
        ).first()
        
        if existing_category and existing_category.CategoryId != category_id:
            return jsonify({"error": "Category name already exists for this user"}), 409
        
        category.category_name = category_name
    
    if description:
        category.Description = description
    
    db.session.commit()
    return jsonify({'message': 'Category updated'}), 200

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@verify_client_credentials
@jwt_required()
def delete_category(category_id):
    current_user_id = get_jwt_identity()
    
    # Ensure category belongs to the current user
    category = Category.query.filter_by(
        CategoryId=category_id,
        UserId=current_user_id
    ).first_or_404()
    
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200

@categories_bp.route('/transactions/categories', methods=['GET'])
@verify_client_credentials
@jwt_required()
def get_transaction_categories():
    current_user_id = get_jwt_identity()
    
    # First check if user has any categories
    user_categories = Category.query.filter_by(UserId=current_user_id).all()
    
    # If no categories exist for this user, create default ones
    if not user_categories:
        default_categories = [
            {'name': 'Food', 'description': 'Food and dining expenses'},
            {'name': 'Transportation', 'description': 'Transportation expenses'},
            {'name': 'Entertainment', 'description': 'Entertainment expenses'},
            {'name': 'Shopping', 'description': 'Shopping expenses'},
            {'name': 'Bills', 'description': 'Monthly bills and utilities'},
            {'name': 'Salary', 'description': 'Income from salary'},
            {'name': 'Other', 'description': 'Miscellaneous expenses'},
        ]
        
        for category_data in default_categories:
            new_category = Category(
                UserId=current_user_id,
                category_name=category_data['name'],
                Description=category_data['description']
            )
            db.session.add(new_category)
        
        db.session.commit()
        
        # Now get the newly created categories
        user_categories = Category.query.filter_by(UserId=current_user_id).all()
    
    # Return the categories
    category_list = [{
        'CategoryId': category.CategoryId,
        'category_name': category.category_name,
        'description': category.Description,
    } for category in user_categories]
    
    return jsonify(category_list), 200