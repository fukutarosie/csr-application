"""CreatePINNewRequest Controller - Handles PIN user request creation"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role
from src.utils.image_upload import save_base64_image

create_pin_new_request_blueprint = Blueprint(
    'create_pin_new_request',
    __name__,
    url_prefix='/api/requests'
)

class CreatePINNewRequest:
    @staticmethod
    @create_pin_new_request_blueprint.route('', methods=['POST'])
    @require_role('PIN')
    def create_new_request():
        """
        Create a new request
        
        Expected JSON body:
        {
            "title": "Need grocery shopping help",
            "description": "Heavy groceries, need help carrying",
            "service_type": "Grocery Shopping",
            "region": "Hougang",
            "requested_by_date": "2025-12-31",
            "image": "data:image/jpeg;base64,/9j/4AAQ..." (required)
        }
        
        All fields are REQUIRED.
        
        Returns:
        {
            "success": true,
            "data": {
                "id": 1,
                "pin_user_id": 2,
                "title": "Need grocery delivery",
                "status": "ACTIVE",
                ...
            },
            "message": "Request created successfully"
        }
        """
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            pin_user_id = user_data['id']
            
            # Get request data
            data = request.get_json()
            
            # Validate required fields
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No data provided'
                }), 400
            
            # Validate title
            title = data.get('title', '').strip()
            if not title or len(title) < 5:
                return jsonify({
                    'success': False,
                    'message': 'Title is required (minimum 5 characters)'
                }), 400
            
            # Validate description
            description = data.get('description', '').strip()
            if not description or len(description) < 10:
                return jsonify({
                    'success': False,
                    'message': 'Description is required (minimum 10 characters)'
                }), 400
            
            # Validate service_type (now required)
            service_type = data.get('service_type', '').strip()
            if not service_type:
                return jsonify({
                    'success': False,
                    'message': 'Service type is required'
                }), 400
            
            # Validate region (now required)
            region = data.get('region', '').strip()
            if not region:
                return jsonify({
                    'success': False,
                    'message': 'Region is required'
                }), 400
            
            # Validate requested_by_date (now required)
            requested_by_date = data.get('requested_by_date', '').strip()
            if not requested_by_date:
                return jsonify({
                    'success': False,
                    'message': 'Requested by date is required'
                }), 400
            
            # Handle image upload (now required)
            image_url = None
            image_data = data.get('image', '').strip()
            if not image_data:
                return jsonify({
                    'success': False,
                    'message': 'Image is required'
                }), 400
            
            success, result, error_msg = save_base64_image(image_data, title)
            if not success:
                return jsonify({
                    'success': False,
                    'message': f'Image upload failed: {error_msg}'
                }), 400
            image_url = result
            
            # Call entity layer
            new_request = Request.create_request(
                pin_user_id=pin_user_id,
                title=title,
                description=description,
                service_type=service_type,
                region=region,
                requested_by_date=requested_by_date,
                image_url=image_url
            )
            
            if not new_request:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create request. Invalid service type.'
                }), 400
            
            return jsonify({
                'success': True,
                'data': new_request,
                'message': 'Request created successfully'
            }), 201
            
        except Exception as e:
            print(f"Error creating request: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
