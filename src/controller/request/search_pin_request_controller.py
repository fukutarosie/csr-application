"""SearchPINRequestController - Handles PIN user request search (Control Layer)"""

from src.entity.request import Request
from src.entity import User

class SearchPINRequestController:
    @staticmethod
    def search_requests(auth_token, keyword, category, status, priority, service_type, my_requests):
        """Search and filter requests"""
        try:
            # Get authenticated user from token
            user_data = User.verify_session_token(auth_token)
            if not user_data:
                return ({'success': False, 'message': 'Unauthorized'}, 401)
            
            pin_user_id = user_data['id']
            
            # Validate status if provided
            valid_statuses = ['ACTIVE', 'SUSPENDED', 'FULFILLED', 'CANCELLED']
            if status and status not in valid_statuses:
                return ({'success': False, 'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 400)
            
            # Validate priority if provided
            valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
            if priority and priority not in valid_priorities:
                return ({'success': False, 'message': f'Invalid priority. Must be one of: {", ".join(valid_priorities)}'}, 400)
            
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
                
                return ({
                    'success': True,
                    'data': filtered_results,
                    'count': len(filtered_results),
                    'filters_applied': filters_applied
                }, 200)
            
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
                
                return ({
                    'success': True,
                    'data': results,
                    'count': len(results),
                    'filters_applied': filters_applied
                }, 200)
            
        except Exception as e:
            print(f"Error searching requests: {str(e)}")
            return ({'success': False, 'message': 'Internal server error'}, 500)
