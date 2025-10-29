"""SuspendPINRequest Controller - Handles PIN user request suspension"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role

suspend_pin_request_blueprint = Blueprint(
    'suspend_pin_request',
    __name__,
    url_prefix='/api/requests'
)

class SuspendPINRequest:
    @staticmethod
    @suspend_pin_request_blueprint.route('/<int:request_id>/suspend', methods=['PUT'])
    @require_role('PIN')
    def suspend_request(request_id):
        """Suspend a request (mark as no longer needed)"""
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            pin_user_id = user_data['id']
            data = request.get_json() or {}
            reason = data.get('reason', '').strip()
            
            suspended_request = Request.suspend_request(
                request_id=request_id,
                pin_user_id=pin_user_id,
                reason=reason if reason else None
            )
            
            if not suspended_request:
                return jsonify({'success': False, 'message': 'Failed to suspend request. Request not found, not owned by you, or not ACTIVE.'}), 400
            
            return jsonify({
                'success': True,
                'data': suspended_request,
                'message': 'Request suspended successfully'
            }), 200
            
        except Exception as e:
            print(f"Error suspending request: {str(e)}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
