from flask import Blueprint, request, jsonify
from models import Transaction, Category
from models import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/test', methods=['GET'])
def test_transactions_route():
    return jsonify({"message": "Transactions blueprint is working!"}), 200

@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    # Get user ID from JWT token
    user_id = get_jwt_identity()
    
    try:
        # Retrieve all transactions for the user
        transactions = Transaction.query.filter_by(UserId=user_id).all()
        
        # Calculate balance (sum of all transactions)
        balance = sum(float(transaction.Amount) for transaction in transactions) if transactions else 0
        
        # Format transactions for the response
        transaction_list = [{
            'id': transaction.TransactionId,
            'type': 'Transaction',  # You could look up category if needed
            'date': transaction.TransactionDate.strftime('%Y-%m-%d'),
            'time': transaction.TransactionDate.strftime('%H:%M'),
            'amount': float(transaction.Amount),
            'description': transaction.Description or "No description"
        } for transaction in transactions]
        
        return jsonify({
            'transactions': transaction_list,
            'balance': balance
        }), 200
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error retrieving transactions: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve transactions',
            'message': str(e)
        }), 500

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    # Get user ID from JWT token
    user_id = get_jwt_identity()
    
    # Get the transaction and ensure it belongs to the requesting user
    transaction = Transaction.query.filter_by(
        TransactionId=transaction_id,
        UserId=user_id
    ).first_or_404()
    
    transaction_data = {
        'id': transaction.TransactionId,
        'userId': transaction.UserId,
        'categoryId': transaction.CategoryId,
        'amount': float(transaction.Amount),
        'date': transaction.TransactionDate.strftime('%Y-%m-%d'),
        'time': transaction.TransactionDate.strftime('%H:%M'),
        'description': transaction.Description or "No description"
    }
    return jsonify(transaction_data), 200

@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    # Get user ID from JWT token
    user_id = get_jwt_identity()
    
    # Get data from request
    data = request.json
    
    try:
        # Parse the transaction date
        try:
            # Try to parse the date in various formats
            transaction_date = data.get('TransactionDate')
            if isinstance(transaction_date, str):
                if 'T' in transaction_date and 'Z' in transaction_date:
                    # ISO format: '2025-03-28T16:50:10.566Z'
                    transaction_date = datetime.datetime.strptime(
                        transaction_date.split('.')[0], 
                        '%Y-%m-%dT%H:%M:%S'
                    )
                else:
                    # Standard format: '2025-03-28 16:50:10'
                    transaction_date = datetime.datetime.strptime(
                        transaction_date, 
                        '%Y-%m-%d %H:%M:%S'
                    )
            else:
                # Use current time if no valid date provided
                transaction_date = datetime.datetime.now()
                
        except Exception as e:
            print(f"Date parsing error: {e}")
            transaction_date = datetime.datetime.now()
            
        # Create the new transaction
        new_transaction = Transaction(
            UserId=user_id,
            CategoryId=data.get('CategoryId'),
            Amount=data.get('Amount'),
            TransactionDate=transaction_date,
            Description=data.get('Description', ''),
            CreatedAt=datetime.datetime.now(),
            UpdatedAt=datetime.datetime.now()
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction created',
            'TransactionId': new_transaction.TransactionId
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Transaction creation error: {str(e)}")
        return jsonify({
            'error': 'Failed to create transaction',
            'message': str(e)
        }), 500

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    # Get user ID from JWT token
    user_id = get_jwt_identity()
    
    # Get the transaction and ensure it belongs to the requesting user
    transaction = Transaction.query.filter_by(
        TransactionId=transaction_id,
        UserId=user_id
    ).first_or_404()
    
    # Update transaction with request data
    data = request.json
    
    try:
        transaction.CategoryId = data.get('CategoryId', transaction.CategoryId)
        transaction.Amount = data.get('Amount', transaction.Amount)
        transaction.TransactionDate = data.get('TransactionDate', transaction.TransactionDate)
        transaction.Description = data.get('Description', transaction.Description)
        
        db.session.commit()
        return jsonify({'message': 'Transaction updated'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update transaction',
            'message': str(e)
        }), 500

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    # Get user ID from JWT token
    user_id = get_jwt_identity()
    
    # Get the transaction and ensure it belongs to the requesting user
    transaction = Transaction.query.filter_by(
        TransactionId=transaction_id,
        UserId=user_id
    ).first_or_404()
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete transaction',
            'message': str(e)
        }), 500