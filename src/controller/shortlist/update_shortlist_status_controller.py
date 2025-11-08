"""
Update Shortlist Status Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import RequestHelpers, ResponseHelpers


class UpdateShortlistStatusController:
    """
    Update Shortlist Status Controller - TRUE OOP
    
    Usage:
        controller = UpdateShortlistStatusController(auth_token, shortlist_id, data)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, shortlist_id: int, data: Dict):
        """Initialize controller"""
        self.auth_token = auth_token
        self.shortlist_id = shortlist_id
        self.data = data
        self.user = None
        self.shortlist = None
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def validate_data(self) -> Tuple[bool, str]:
        """Validate request data"""
        if not self.data:
            return False, 'Request body is required'
        
        # Validate required fields
        required_fields = ['status']
        is_valid, error_msg, _ = RequestHelpers.validate_required_fields(self.data, required_fields)
        if not is_valid:
            return False, error_msg
        
        # Validate status
        status = self.data.get('status')
        if status not in Shortlist.VALID_STATUSES:
            return False, f'Invalid status. Must be one of: {", ".join(Shortlist.VALID_STATUSES)}'
        
        return True, ''
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute shortlist status update"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return (ResponseHelpers.error_response('Invalid or expired token', 401), 401)
            
            # Validate data
            is_valid, error_msg = self.validate_data()
            if not is_valid:
                return (ResponseHelpers.error_response(error_msg, 400), 400)
            
            # Load Shortlist object
            self.shortlist = Shortlist.find(self.shortlist_id)
            if not self.shortlist:
                return (ResponseHelpers.error_response('Shortlist entry not found', 404), 404)
            
            # Verify ownership
            if self.shortlist.csr_user_id != self.user.id:
                return (ResponseHelpers.error_response('Unauthorized', 403), 403)
            
            new_status = self.data.get('status')

            # Prevent CSR from marking as completed directly
            if new_status == Shortlist.STATUS_COMPLETED:
                return (
                    ResponseHelpers.error_response(
                        'Only PIN users can mark an opportunity as completed.',
                        403
                    ),
                    403
                )

            # Ensure no other CSR has already accepted the request
            if new_status == Shortlist.STATUS_IN_PROGRESS:
                existing_assignment = Shortlist.active_assignment_for_request(self.shortlist.request_id)
                if existing_assignment and existing_assignment.id != self.shortlist.id:
                    return (
                        ResponseHelpers.error_response(
                            'Another CSR representative has already accepted this opportunity.',
                            409
                        ),
                        409
                    )

            # Update status and optional fields
            self.shortlist.status = new_status
            if 'notes' in self.data:
                self.shortlist.notes = self.data.get('notes')
            if 'volunteered_hours' in self.data:
                self.shortlist.volunteered_hours = self.data.get('volunteered_hours')
            if 'feedback_from_pin' in self.data:
                self.shortlist.feedback_from_pin = self.data.get('feedback_from_pin')
            
            # Save (instance method)
            self.shortlist.save()
            
            return (ResponseHelpers.success_response(
                data=self.shortlist.to_dict(),
                message='Shortlist status updated successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Update shortlist status failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
