import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://localhost:3002').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Import and register blueprints
# Auth Controllers
from src.controller.auth.login_controller import login_blueprint

# User Account Controllers
from src.controller.userAccount.create_user_account_controller import create_user_account_blueprint
from src.controller.userAccount.view_user_account_controller import view_user_account_blueprint
from src.controller.userAccount.update_user_account_controller import update_user_account_blueprint
from src.controller.userAccount.suspend_user_account_controller import suspend_user_account_blueprint
from src.controller.userAccount.search_user_account_controller import search_user_account_blueprint

# User Profile Controllers
from src.controller.userProfile.boundary.create_user_profile_boundary import create_user_profile_boundary
from src.controller.userProfile.boundary.view_user_profile_boundary import view_user_profile_boundary
from src.controller.userProfile.boundary.update_user_profile_boundary import update_user_profile_boundary
from src.controller.userProfile.boundary.suspend_user_profile_boundary import suspend_user_profile_boundary
from src.controller.userProfile.boundary.search_user_profile_boundary import search_user_profile_boundary

# PIN Request Controllers
from src.controller.request.create_pin_new_request import create_pin_new_request_blueprint
from src.controller.request.view_pin_request import view_pin_request_blueprint
from src.controller.request.update_pin_request import update_pin_request_blueprint
from src.controller.request.suspend_pin_request import suspend_pin_request_blueprint
from src.controller.request.search_pin_request import search_pin_request_blueprint

# Consolidated Role and User Controllers
from src.controller.role.role_controller import role_blueprint
from src.controller.user.user_controller import user_blueprint

# Register Auth blueprints
app.register_blueprint(login_blueprint)

# Register User Account blueprints
app.register_blueprint(create_user_account_blueprint)
app.register_blueprint(view_user_account_blueprint)
app.register_blueprint(update_user_account_blueprint)
app.register_blueprint(suspend_user_account_blueprint)
app.register_blueprint(search_user_account_blueprint)

# Register User Profile blueprints
app.register_blueprint(create_user_profile_boundary)
app.register_blueprint(view_user_profile_boundary)
app.register_blueprint(update_user_profile_boundary)
app.register_blueprint(suspend_user_profile_boundary)
app.register_blueprint(search_user_profile_boundary)

# Register PIN Request blueprints
app.register_blueprint(create_pin_new_request_blueprint)
app.register_blueprint(view_pin_request_blueprint)
app.register_blueprint(update_pin_request_blueprint)
app.register_blueprint(suspend_pin_request_blueprint)
app.register_blueprint(search_pin_request_blueprint)

# Register consolidated Role and User blueprints
app.register_blueprint(role_blueprint)
app.register_blueprint(user_blueprint)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return {
        'status': 'healthy',
        'message': 'CSR App Backend is running'
    }, 200

# Error handlers
@app.errorhandler(404)
def not_found(_error):
    return {
        'success': False,
        'message': 'Endpoint not found'
    }, 404

@app.errorhandler(500)
def internal_error(_error):
    return {
        'success': False,
        'message': 'Internal server error'
    }, 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'

    app.run(host=host, port=port, debug=debug)
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    app.run(host=host, port=port, debug=debug)