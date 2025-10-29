"""ViewPINRequest Controller - Handles PIN user request viewing"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role

view_pin_request_blueprint = Blueprint(
    'view_pin_request',
    __name__,
    url_prefix='/api/requests'
)

class ViewPINRequest:
    @staticmethod
    @view_pin_request_blueprint.route('', methods=['GET'])
    @require_role('PIN')
    def get_my_requests():
        """Get all my requests with optional status filter"""
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            pin_user_id = user_data['id']
            status = request.args.get('status', '').strip() or None
            
            requests_list = Request.get_requests_by_pin_user(
                pin_user_id=pin_user_id,
                status=status
            )
            
            return jsonify({
                'success': True,
                'data': requests_list,
                'count': len(requests_list)
            }), 200
            
        except Exception as e:
            print(f"Error getting requests: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500

    @staticmethod
    @view_pin_request_blueprint.route('/<int:request_id>', methods=['GET'])
    @require_role('PIN')
    def get_request_detail(request_id):
        """Get single request detail"""
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            pin_user_id = user_data['id']
            request_data = Request.get_request(request_id)
            
            if not request_data:
                return jsonify({
                    'success': False,
                    'message': 'Request not found'
                }), 404
            
            # Verify ownership
            if request_data['pin_user_id'] != pin_user_id:
                return jsonify({
                    'success': False,
                    'message': 'You do not have permission to view this request'
                }), 403
            
            return jsonify({
                'success': True,
                'data': request_data
            }), 200
            
        except Exception as e:
            print(f"Error getting request detail: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
