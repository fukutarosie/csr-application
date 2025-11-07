"""UpdatePINRequestController - Handles PIN user request updates (Control Layer)"""

from src.entity.request import Request
from src.entity import User

class UpdatePINRequestController:
    @staticmethod
    def update_request(auth_token, request_id, data):
        """
        Update a request
        
        Args:
            auth_token: JWT token
            request_id: Request ID to update
            data: Dictionary with fields to update
        
        Returns:
            (response_dict, status_code)
        """
        try:
            # Get authenticated user from token
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return ({'success': False, 'message': 'Unauthorized'}, 401)
            
            pin_user_id = user_data['id']
            
            if not data:
                return ({'success': False, 'message': 'No data provided'}, 400)
            
            # Validate fields if provided
            updates = {}
            
            if 'title' in data:
                title = data['title'].strip()
                if not title or len(title) < 5:
                    return ({'success': False, 'message': 'Title must be at least 5 characters'}, 400)
                updates['title'] = title
            
            if 'description' in data:
                description = data['description'].strip()
                if not description or len(description) < 10:
                    return ({'success': False, 'message': 'Description must be at least 10 characters'}, 400)
                updates['description'] = description
            
            if 'service_type' in data:
                service_type = data['service_type'].strip()
                if service_type:
                    updates['service_type'] = service_type
            
            if 'region' in data:
                region = data['region'].strip()
                if region:
                    updates['region'] = region
            
            # For backwards compatibility, also accept location_city
            if 'location_city' in data and 'region' not in data:
                location_city = data['location_city'].strip()
                if location_city:
                    updates['region'] = location_city
            
            if 'requested_by_date' in data:
                requested_by_date = data['requested_by_date'].strip()
                if requested_by_date:
                    updates['requested_by_date'] = requested_by_date
            
            if 'image_url' in data:
                image_url = data['image_url'].strip() if data['image_url'] else None
                updates['image_url'] = image_url
            
            if not updates:
                return ({'success': False, 'message': 'No valid fields to update'}, 400)
            
            # Call entity layer
            updated_request = Request.update_request(
                request_id=request_id,
                pin_user_id=pin_user_id,
                updates=updates
            )
            
            if not updated_request:
                return ({'success': False, 'message': 'Failed to update request. Request not found, not owned by you, or not ACTIVE.'}, 400)
            
            return ({
                'success': True,
                'data': updated_request,
                'message': 'Request updated successfully'
            }, 200)
            
        except Exception as e:
            print(f"Error updating request: {str(e)}")
            return ({'success': False, 'message': 'Internal server error'}, 500)
