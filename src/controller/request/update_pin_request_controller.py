"""
Update PIN Request Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple, Optional
from src.entity.request import Request
from src.entity.shortlist import Shortlist
from src.entity import User


class UpdatePINRequestController:
    """
    Update PIN Request Controller - TRUE OOP
    
    Usage:
        controller = UpdatePINRequestController(auth_token, request_id, data)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, request_id: int, data: Dict):
        """Initialize controller"""
        self.auth_token = auth_token
        self.request_id = request_id
        self.data = data
        self.user = None
        self.request = None
        self.errors = []
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def validate_and_prepare_updates(self) -> Dict:
        """Validate and prepare update data"""
        if not self.data:
            self.errors.append('No data provided')
            return {}
        
        updates = {}
        
        if 'title' in self.data:
            title = self.data['title'].strip()
            if not title or len(title) < 5:
                self.errors.append('Title must be at least 5 characters')
            else:
                updates['title'] = title
        
        if 'description' in self.data:
            description = self.data['description'].strip()
            if not description or len(description) < 10:
                self.errors.append('Description must be at least 10 characters')
            else:
                updates['description'] = description
        
        if 'service_type' in self.data:
            service_type = self.data['service_type'].strip()
            if service_type:
                updates['service_type'] = service_type
        
        if 'region' in self.data:
            region = self.data['region'].strip()
            if region:
                updates['region'] = region
        
        if 'requested_by_date' in self.data:
            requested_by_date = self.data['requested_by_date']
            if requested_by_date:
                updates['requested_by_date'] = requested_by_date
        
        return updates
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute request update"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return ({'success': False, 'message': 'Unauthorized'}, 401)

            status_update = self.data.get('status') if self.data else None
            if status_update:
                status_update = status_update.strip().upper()
            
            # Special handling: marking as fulfilled
            if status_update == Request.STATUS_FULFILLED:
                return self._handle_fulfillment()
            
            # Validate and prepare updates
            updates = self.validate_and_prepare_updates()
            if self.errors:
                return ({'success': False, 'message': '; '.join(self.errors)}, 400)
            
            if not updates:
                return ({'success': False, 'message': 'No valid fields to update'}, 400)
            
            # Load Request object
            self.request = Request.find(self.request_id)
            if not self.request:
                return ({'success': False, 'message': 'Request not found'}, 404)
            
            # Verify ownership
            if self.request.pin_user_id != self.user.id:
                return ({'success': False, 'message': 'Unauthorized'}, 403)
            
            # Apply updates
            for key, value in updates.items():
                setattr(self.request, key, value)
            
            # Save
            self.request.save()
            
            return ({
                'success': True,
                'data': self.request.to_dict(),
                'message': 'Request updated successfully'
            }, 200)
            
        except Exception as e:
            print(f"Error updating request: {str(e)}")
            return ({
                'success': False,
                'message': 'Internal server error'
            }, 500)

    def _handle_fulfillment(self) -> Tuple[Dict, int]:
        """Handle request fulfillment by PIN user"""
        # Load request
        self.request = Request.find(self.request_id)
        if not self.request:
            return ({'success': False, 'message': 'Request not found'}, 404)
        
        # Verify ownership
        if self.request.pin_user_id != self.user.id:
            return ({'success': False, 'message': 'Unauthorized'}, 403)
        
        # Mark request fulfilled
        if not self.request.fulfill():
            return ({'success': False, 'message': 'Failed to fulfill request'}, 500)
        
        # Update related shortlist assignment (if any)
        shortlist_entry = Shortlist.active_assignment_for_request(self.request.id)
        volunteer_hours = self._parse_float(self.data.get('volunteered_hours'))
        feedback = self.data.get('feedback_from_pin')
        
        if shortlist_entry:
            shortlist_entry.mark_completed(volunteer_hours, feedback)
        
        # Reload request to return updated data
        self.request = Request.find(self.request_id)
        response_data = self.request.to_dict()
        
        assignment = Shortlist.active_assignment_for_request(self.request.id)
        if assignment:
            response_data['assignment_status'] = assignment.status
            response_data['active_assignment'] = assignment.to_assignment_dict()
        else:
            response_data['assignment_status'] = None
            response_data['active_assignment'] = None
        
        return ({
            'success': True,
            'data': response_data,
            'message': 'Request marked as completed successfully'
        }, 200)

    def _parse_float(self, value: Optional[object]) -> Optional[float]:
        """Parse float value safely"""
        if value in (None, ''):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
