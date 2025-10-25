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
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Import and register blueprints
from src.controller.auth.auth_controller import auth_blueprint
from src.controller.user.user_controller import user_blueprint
from src.controller.role.role_controller import role_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(role_blueprint)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return {
        'status': 'healthy',
        'message': 'CSR App Backend is running'
    }, 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {
        'success': False,
        'message': 'Endpoint not found'
    }, 404

@app.errorhandler(500)
def internal_error(error):
    return {
        'success': False,
        'message': 'Internal server error'
    }, 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    app.run(host=host, port=port, debug=debug)