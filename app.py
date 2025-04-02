from flask import Flask, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlencode
from Queue_manager import request_queue_manager
from config import Config
from models import db
from flask_mysqldb import MySQL
from flask_cors import CORS
from routes.categories import categories_bp

# Import blueprints 
from routes.auth import auth_bp
from routes.user import user_bp
from routes.test import test_bp
from routes.transactions import transactions_bp
# Other imports...

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}})

db.init_app(app)
jwt = JWTManager(app)
mysql = MySQL(app)

@app.route('/')
def home():
    return jsonify({"message": "Hello Users"}), 200

# Test route for debugging
@app.route('/test-transactions')
def test_transactions():
    return jsonify({"message": "Test endpoint is working!"}), 200

# Register Blueprints - ensure names match exactly
app.register_blueprint(auth_bp, url_prefix='/auth_redirect')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(test_bp, url_prefix='/testing')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
# app.register_blueprint(bill_bp, url_prefix='/bills')
# app.register_blueprint(reminders_bp, url_prefix='/reminders')
# app.register_blueprint(goals_bp, url_prefix='/goals')
# app.register_blueprint(budget_bp, url_prefix='/budgets')
# app.register_blueprint(notifications_bp, url_prefix='/notifications')
# app.register_blueprint(receipts_bp, url_prefix='/receipts')
# app.register_blueprint(ml_bp, url_prefix='/ml')
app.register_blueprint(categories_bp, url_prefix='/categories')

@app.route('/queue', methods=['POST'])
def queue():
    # Example of how to add a request to the queue
    user_id = 1  # Replace with actual user ID
    req_data = {'key': 'value'}  # Replace with actual request data
    success, message = request_queue_manager.add_request(user_id, req_data)
    return jsonify({"message": message}), 200 if success else 400

@app.route('/auth_redirect')
def auth_redirect():
    return jsonify({"message": "This will redirect to authentication"}), 200
# @app.route('/user')
# def user_redirect():
#     return jsonify({"message": "This will redirect to user update"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)