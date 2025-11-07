import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Create Flask app with static folder configured
app = Flask(__name__, static_folder='static', static_url_path='/static')

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
from src.controller.request.create_new_pin_request_controller import create_pin_new_request_blueprint
from src.controller.request.view_pin_request_controller import view_pin_request_blueprint
from src.controller.request.update_pin_request_controller import update_pin_request_blueprint
from src.controller.request.suspend_pin_request_controller import suspend_pin_request_blueprint
from src.controller.request.search_pin_request_controller import search_pin_request_blueprint
from src.controller.request.get_pin_requests_controller import get_pin_requests_blueprint
from src.controller.request.get_request_analytics_controller import get_request_analytics_blueprint
from src.controller.request.increment_view_count_controller import increment_view_count_blueprint
from src.controller.request.get_completed_matches_controller import get_completed_matches_blueprint
from src.controller.request.get_request_lookups_controller import get_request_lookups_blueprint

# CSR Shortlist Controllers
from src.controller.shortlist.add_to_shortlist_controller import add_to_shortlist_blueprint
from src.controller.shortlist.get_shortlist_controller import get_shortlist_blueprint
from src.controller.shortlist.update_shortlist_status_controller import update_shortlist_status_blueprint
from src.controller.shortlist.remove_from_shortlist_controller import remove_from_shortlist_blueprint
from src.controller.shortlist.get_shortlist_stats_controller import get_shortlist_stats_blueprint

# Role Controllers (Specific Controllers following SRP)
from src.controller.role.get_public_roles_controller import get_public_roles_blueprint
from src.controller.role.get_all_roles_controller import get_all_roles_blueprint
from src.controller.role.get_role_controller import get_role_blueprint
from src.controller.role.create_role_controller import create_role_blueprint
from src.controller.role.update_role_controller import update_role_blueprint
from src.controller.role.delete_role_controller import delete_role_blueprint

# Consolidated User Controller
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
app.register_blueprint(get_pin_requests_blueprint)
app.register_blueprint(get_request_analytics_blueprint)
app.register_blueprint(increment_view_count_blueprint)  # US-27: Track CSR views
app.register_blueprint(get_completed_matches_blueprint)
app.register_blueprint(get_request_lookups_blueprint)

# Register CSR Shortlist blueprints
app.register_blueprint(add_to_shortlist_blueprint)
app.register_blueprint(get_shortlist_blueprint)
app.register_blueprint(update_shortlist_status_blueprint)
app.register_blueprint(remove_from_shortlist_blueprint)
app.register_blueprint(get_shortlist_stats_blueprint)

# Register Role blueprints (Specific Controllers)
app.register_blueprint(get_public_roles_blueprint)
app.register_blueprint(get_all_roles_blueprint)
app.register_blueprint(get_role_blueprint)
app.register_blueprint(create_role_blueprint)
app.register_blueprint(update_role_blueprint)
app.register_blueprint(delete_role_blueprint)

# Register User blueprint
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