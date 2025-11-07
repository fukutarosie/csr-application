"""SearchPINRequestController - Handles PIN user request search"""

from flask import Blueprint, request, jsonify
from src.entity.request import Request
from src.entity import User
from src.controller.auth.auth_middleware import require_role

search_pin_request_blueprint = Blueprint(
    'search_pin_request',
    __name__,
    url_prefix='/api/requests'
)

class SearchPINRequestController:
    @staticmethod
    @search_pin_request_blueprint.route('/search', methods=['GET'])
    @require_role('PIN')
    def search_requests():
        """Search and filter requests"""
        try:
            # Get authenticated user from token
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return jsonify({'success': False, 'message': 'Unauthorized'}), 401
            
            pin_user_id = user_data['id']
            
            # Parse query parameters
            keyword = request.args.get('keyword', '').strip() or None
            category = request.args.get('category', '').strip() or None
            status = request.args.get('status', '').strip() or None
            priority = request.args.get('priority', '').strip() or None
            service_type = request.args.get('service_type', '').strip() or None
            my_requests = request.args.get('my_requests', 'true').lower() == 'true'
            
            # Validate status if provided
            valid_statuses = ['ACTIVE', 'SUSPENDED', 'FULFILLED', 'CANCELLED']
            if status and status not in valid_statuses:
                return jsonify({'success': False, 'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
            
            # Validate priority if provided
            valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
            if priority and priority not in valid_priorities:
                return jsonify({'success': False, 'message': f'Invalid priority. Must be one of: {", ".join(valid_priorities)}'}), 400
            
            # For PIN users, always search own requests
            if my_requests:
                results = Request.get_requests_by_pin_user(pin_user_id=pin_user_id, status=status)
                
                filtered_results = []
                for req in results:
                    if keyword:
                        if keyword.lower() not in req.get('title', '').lower() and \
                           keyword.lower() not in req.get('description', '').lower():
                            continue
                    
                    if category and req.get('category') != category:
                        continue
                    
                    if priority and req.get('priority') != priority:
                        continue
                    
                    if service_type and req.get('service_type') != service_type:
                        continue
                    
                    filtered_results.append(req)
                
                filters_applied = {}
                if keyword:
                    filters_applied['keyword'] = keyword
                if category:
                    filters_applied['category'] = category
                if status:
                    filters_applied['status'] = status
                if priority:
                    filters_applied['priority'] = priority
                if service_type:
                    filters_applied['service_type'] = service_type
                
                return jsonify({
                    'success': True,
                    'data': filtered_results,
                    'count': len(filtered_results),
                    'filters_applied': filters_applied
                }), 200
            
            else:
                results = Request.search_requests(keyword=keyword, category=category, status=status, priority=priority, service_type=service_type)
                
                filters_applied = {}
                if keyword:
                    filters_applied['keyword'] = keyword
                if category:
                    filters_applied['category'] = category
                if status:
                    filters_applied['status'] = status
                if priority:
                    filters_applied['priority'] = priority
                if service_type:
                    filters_applied['service_type'] = service_type
                
                return jsonify({
                    'success': True,
                    'data': results,
                    'count': len(results),
                    'filters_applied': filters_applied
                }), 200
            
        except Exception as e:
            print(f"Error searching requests: {str(e)}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
