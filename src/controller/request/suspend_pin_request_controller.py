"""SuspendPINRequestController - Handles PIN user request suspension (Control Layer)"""

from src.entity.request import Request
from src.entity import User

class SuspendPINRequestController:
    @staticmethod
    def suspend_request(auth_token, request_id, data):
        """Suspend a request (mark as no longer needed)"""
        try:
            # Get authenticated user from token
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return ({'success': False, 'message': 'Unauthorized'}, 401)
            
            pin_user_id = user_data['id']
            reason = data.get('reason', '').strip()
            
            suspended_request = Request.suspend_request(
                request_id=request_id,
                pin_user_id=pin_user_id,
                reason=reason if reason else None
            )
            
            if not suspended_request:
                return ({'success': False, 'message': 'Failed to suspend request. Request not found, not owned by you, or not ACTIVE.'}, 400)
            
            return ({
                'success': True,
                'data': suspended_request,
                'message': 'Request suspended successfully'
            }, 200)
            
        except Exception as e:
            print(f"Error suspending request: {str(e)}")
            return ({'success': False, 'message': 'Internal server error'}, 500)
