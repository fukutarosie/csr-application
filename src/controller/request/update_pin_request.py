"""UpdatePINRequest Controller - Handles PIN user request updates"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role

update_pin_request_blueprint = Blueprint(
    'update_pin_request',
    __name__,
    url_prefix='/api/requests'
)

class UpdatePINRequest:
    @staticmethod
    @update_pin_request_blueprint.route('/<int:request_id>', methods=['PUT'])
    @require_role('PIN')
    def update_request(request_id):
        """
        Update a request
        
        Path parameter:
        - request_id: Request ID to update
        
        Expected JSON body (any of these fields):
        {
            "title": "Updated title",
            "description": "Updated description",
            "category": "Medical",
            "service_type": "Accompaniment",
            "priority": "URGENT",
            "location_city": "Bangkok",
            "location_detail": "New location",
            "requested_by_date": "2025-11-05"
        }
        
        Returns:
        {
            "success": true,
            "data": {
                "id": 1,
                "title": "Updated title",
                "updated_at": "2025-10-28T12:00:00",
                ...
            },
            "message": "Request updated successfully"
        }
        
        Notes:
        - Can only update ACTIVE requests
        - Can only update own requests
        """
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            pin_user_id = user_data['id']
            data = request.get_json()
            
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'}), 400
            
            # Validate fields if provided
            updates = {}
            
            if 'title' in data:
                title = data['title'].strip()
                if not title or len(title) < 5:
                    return jsonify({'success': False, 'message': 'Title must be at least 5 characters'}), 400
                updates['title'] = title
            
            if 'description' in data:
                description = data['description'].strip()
                if not description or len(description) < 10:
                    return jsonify({'success': False, 'message': 'Description must be at least 10 characters'}), 400
                updates['description'] = description
            
            if 'category' in data:
                category = data['category'].strip()
                if category:
                    updates['category'] = category
            
            if 'service_type' in data:
                service_type = data['service_type'].strip()
                if service_type:
                    updates['service_type'] = service_type
            
            if 'priority' in data:
                priority = data['priority'].strip()
                if priority:
                    updates['priority'] = priority
            
            if 'location_city' in data:
                location_city = data['location_city'].strip()
                if location_city:
                    updates['location_city'] = location_city
            
            if 'location_detail' in data:
                location_detail = data['location_detail'].strip()
                if location_detail:
                    updates['location_detail'] = location_detail
            
            if 'requested_by_date' in data:
                requested_by_date = data['requested_by_date'].strip()
                if requested_by_date:
                    updates['requested_by_date'] = requested_by_date
            
            if not updates:
                return jsonify({'success': False, 'message': 'No valid fields to update'}), 400
            
            # Call entity layer
            updated_request = Request.update_request(
                request_id=request_id,
                pin_user_id=pin_user_id,
                updates=updates
            )
            
            if not updated_request:
                return jsonify({'success': False, 'message': 'Failed to update request. Request not found, not owned by you, or not ACTIVE.'}), 400
            
            return jsonify({
                'success': True,
                'data': updated_request,
                'message': 'Request updated successfully'
            }), 200
            
        except Exception as e:
            print(f"Error updating request: {str(e)}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
