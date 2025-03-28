from flask import request, jsonify
from functools import wraps
from models import OAuth2Client

# List of public routes that do not require client credentials
PUBLIC_ROUTES = {
    "/auth_redirect/signup",  # Allow user signup without authentication
    "/auth_redirect/login",   # Optional: If login should also be open
}

def verify_client_credentials(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for public routes
        if request.path in PUBLIC_ROUTES:
            return f(*args, **kwargs)

        # Try to get credentials from headers first
        client_id = request.headers.get('X-Client-ID')
        client_secret = request.headers.get('X-Client-Secret')

        # If credentials aren't found in headers, check query parameters for GET requests...
        if not client_id or not client_secret:
            if request.method == 'GET':
                client_id = request.args.get('client_id')
                client_secret = request.args.get('client_secret')
            # ...or check JSON body for POST/PUT/PATCH requests
            elif request.method in ['POST', 'PUT', 'PATCH']:
                json_data = request.get_json(silent=True)
                if json_data:
                    client_id = client_id or json_data.get('client_id')
                    client_secret = client_secret or json_data.get('client_secret')

        if not client_id or not client_secret:
            return jsonify({"message": "Client ID and Client Secret are required"}), 401

        client = OAuth2Client.query.filter_by(client_id=client_id, client_secret=client_secret).first()
        if not client:
            return jsonify({"message": "Invalid client credentials"}), 401

        return f(*args, **kwargs)
    
    return decorated_function
