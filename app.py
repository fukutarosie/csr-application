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
# Auth Controllers (2-layer BCE)
from src.controller.auth.boundary.login_boundary import login_boundary

# User Account Controllers (2-layer BCE)
from src.controller.userAccount.boundary.create_user_account_boundary import create_user_account_boundary
from src.controller.userAccount.boundary.view_user_account_boundary import view_user_account_boundary
from src.controller.userAccount.boundary.update_user_account_boundary import update_user_account_boundary
from src.controller.userAccount.boundary.suspend_user_account_boundary import suspend_user_account_boundary
from src.controller.userAccount.boundary.search_user_account_boundary import search_user_account_boundary

# User Profile Controllers (2-layer BCE)
from src.controller.userProfile.boundary.create_user_profile_boundary import create_user_profile_boundary
from src.controller.userProfile.boundary.view_user_profile_boundary import view_user_profile_boundary
from src.controller.userProfile.boundary.update_user_profile_boundary import update_user_profile_boundary
from src.controller.userProfile.boundary.suspend_user_profile_boundary import suspend_user_profile_boundary
from src.controller.userProfile.boundary.search_user_profile_boundary import search_user_profile_boundary

# PIN Request Controllers (2-layer BCE)
from src.controller.request.boundary.create_new_pin_request_boundary import create_pin_new_request_boundary
from src.controller.request.boundary.view_pin_request_boundary import view_pin_request_boundary
from src.controller.request.boundary.update_pin_request_boundary import update_pin_request_boundary
from src.controller.request.boundary.suspend_pin_request_boundary import suspend_pin_request_boundary
from src.controller.request.boundary.search_pin_request_boundary import search_pin_request_boundary
from src.controller.request.boundary.get_pin_requests_boundary import get_pin_requests_boundary
from src.controller.request.boundary.get_request_analytics_boundary import get_request_analytics_boundary
from src.controller.request.boundary.increment_view_count_boundary import increment_view_count_boundary
from src.controller.request.boundary.get_completed_matches_boundary import get_completed_matches_boundary
from src.controller.request.boundary.get_request_lookups_boundary import get_request_lookups_boundary

# CSR Shortlist Controllers (2-layer BCE)
from src.controller.shortlist.boundary.add_to_shortlist_boundary import add_to_shortlist_boundary
from src.controller.shortlist.boundary.get_shortlist_boundary import get_shortlist_boundary
from src.controller.shortlist.boundary.update_shortlist_status_boundary import update_shortlist_status_boundary
from src.controller.shortlist.boundary.remove_from_shortlist_boundary import remove_from_shortlist_boundary
from src.controller.shortlist.boundary.get_shortlist_stats_boundary import get_shortlist_stats_boundary

# Role Controllers (2-layer BCE)
from src.controller.role.boundary.get_public_roles_boundary import get_public_roles_boundary
from src.controller.role.boundary.get_all_roles_boundary import get_all_roles_boundary
from src.controller.role.boundary.get_role_boundary import get_role_boundary
from src.controller.role.boundary.create_role_boundary import create_role_boundary
from src.controller.role.boundary.update_role_boundary import update_role_boundary
from src.controller.role.boundary.delete_role_boundary import delete_role_boundary

# Register Auth blueprints (2-layer BCE)
app.register_blueprint(login_boundary)

# Register User Account blueprints (2-layer BCE)
app.register_blueprint(create_user_account_boundary)
app.register_blueprint(view_user_account_boundary)
app.register_blueprint(update_user_account_boundary)
app.register_blueprint(suspend_user_account_boundary)
app.register_blueprint(search_user_account_boundary)

# Register User Profile blueprints (2-layer BCE)
app.register_blueprint(create_user_profile_boundary)
app.register_blueprint(view_user_profile_boundary)
app.register_blueprint(update_user_profile_boundary)
app.register_blueprint(suspend_user_profile_boundary)
app.register_blueprint(search_user_profile_boundary)

# Register PIN Request blueprints (2-layer BCE)
app.register_blueprint(create_pin_new_request_boundary)
app.register_blueprint(view_pin_request_boundary)
app.register_blueprint(update_pin_request_boundary)
app.register_blueprint(suspend_pin_request_boundary)
app.register_blueprint(search_pin_request_boundary)
app.register_blueprint(get_pin_requests_boundary)
app.register_blueprint(get_request_analytics_boundary)
app.register_blueprint(increment_view_count_boundary)  # US-27: Track CSR views
app.register_blueprint(get_completed_matches_boundary)
app.register_blueprint(get_request_lookups_boundary)

# Register CSR Shortlist blueprints (2-layer BCE)
app.register_blueprint(add_to_shortlist_boundary)
app.register_blueprint(get_shortlist_boundary)
app.register_blueprint(update_shortlist_status_boundary)
app.register_blueprint(remove_from_shortlist_boundary)
app.register_blueprint(get_shortlist_stats_boundary)

# Register Role blueprints (2-layer BCE)
app.register_blueprint(get_public_roles_boundary)
app.register_blueprint(get_all_roles_boundary)
app.register_blueprint(get_role_boundary)
app.register_blueprint(create_role_boundary)
app.register_blueprint(update_role_boundary)
app.register_blueprint(delete_role_boundary)

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