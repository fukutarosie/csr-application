"""CreatePINNewRequest Controller - Handles PIN user request creation"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role

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
            "title": "Need grocery delivery",
            "description": "Heavy groceries, need help carrying",
            "category": "Food",
            "service_type": "Delivery",
            "priority": "HIGH",
            "location_city": "Bangkok",
            "location_detail": "44/123 Sukhumvit Rd",
            "requested_by_date": "2025-10-31"
        }
        
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
            
            # Validate category
            category = data.get('category', '').strip()
            if not category:
                return jsonify({
                    'success': False,
                    'message': 'Category is required'
                }), 400
            
            # Get optional fields
            service_type = data.get('service_type', '').strip() or None
            priority = data.get('priority', 'MEDIUM').strip()
            location_city = data.get('location_city', '').strip() or None
            location_detail = data.get('location_detail', '').strip() or None
            requested_by_date = data.get('requested_by_date', '').strip() or None
            
            # Call entity layer
            new_request = Request.create_request(
                pin_user_id=pin_user_id,
                title=title,
                description=description,
                category=category,
                service_type=service_type,
                priority=priority,
                location_city=location_city,
                location_detail=location_detail,
                requested_by_date=requested_by_date
            )
            
            if not new_request:
                return jsonify({
                    'success': False,
                    'message': 'Failed to create request. Invalid category or service type.'
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
