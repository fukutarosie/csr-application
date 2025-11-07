"""ViewPINRequestController - Handles PIN user request viewing"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role

view_pin_request_blueprint = Blueprint(
    'view_pin_request',
    __name__,
    url_prefix='/api/requests'
)

class ViewPINRequestController:
    @staticmethod
    @view_pin_request_blueprint.route('', methods=['GET'])
    def get_requests():
        """Get requests - PIN users see their own, CSR Reps see all ACTIVE requests"""
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            user_role = user_data.get('role', {}).get('name', '')
            user_id = user_data['id']
            
            print(f"[DEBUG] get_requests - User {user_id} ({user_role}) fetching requests")
            
            # Check if user has permission
            if user_role not in ['PIN', 'CSR Rep', 'Platform Manager']:
                return jsonify({
                    'success': False,
                    'message': 'You do not have permission to view requests'
                }), 403
            
            status = request.args.get('status', '').strip() or None
            
            # PIN users see only their own requests
            if user_role == 'PIN':
                requests_list = Request.get_requests_by_pin_user(
                    pin_user_id=user_id,
                    status=status
                )
            # CSR Rep and Platform Manager see all requests (default to ACTIVE if no status specified)
            else:
                if status is None:
                    status = 'ACTIVE'
                requests_list = Request.get_all_requests(status=status)
            
            print(f"[DEBUG] Returning {len(requests_list)} requests")
            
            return jsonify({
                'success': True,
                'data': requests_list,
                'count': len(requests_list)
            }), 200
            
        except Exception as e:
            print(f"Error getting requests: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500

    @staticmethod
    @view_pin_request_blueprint.route('/<int:request_id>', methods=['GET'])
    def get_request_detail(request_id):
        """Get single request detail - accessible by PIN (own requests), CSR Rep (all requests), Platform Manager"""
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            user_role = user_data.get('role', {}).get('name', '')
            user_id = user_data['id']
            
            print(f"[DEBUG] User {user_id} ({user_role}) requesting request {request_id}")
            
            # Check if user has permission to view requests
            if user_role not in ['PIN', 'CSR Rep', 'Platform Manager']:
                print(f"[DEBUG] Role '{user_role}' not in allowed roles")
                return jsonify({
                    'success': False,
                    'message': 'You do not have permission to view requests'
                }), 403
            
            request_data = Request.get_request(request_id)
            
            if not request_data:
                print(f"[DEBUG] Request {request_id} not found")
                return jsonify({
                    'success': False,
                    'message': 'Request not found'
                }), 404
            
            print(f"[DEBUG] Request data keys: {request_data.keys()}")
            print(f"[DEBUG] Request pin_user_id: {request_data.get('pin_user_id')}")
            
            # PIN users can only view their own requests
            if user_role == 'PIN' and request_data.get('pin_user_id') != user_id:
                print(f"[DEBUG] PIN user {user_id} trying to access request owned by {request_data.get('pin_user_id')}")
                return jsonify({
                    'success': False,
                    'message': 'You do not have permission to view this request'
                }), 403
            
            # CSR Rep and Platform Manager can view any request
            return jsonify({
                'success': True,
                'data': request_data
            }), 200
            
        except Exception as e:
            print(f"Error getting request detail: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
