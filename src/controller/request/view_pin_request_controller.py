"""
View PIN Request Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple, Optional
from src.entity.request import Request
from src.entity.shortlist import Shortlist
from src.entity import User


class ViewPINRequestsController:
    """
    View PIN Requests Controller - TRUE OOP
    
    Usage:
        controller = ViewPINRequestsController(auth_token, status_param)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, status_param: str = None):
        """Initialize controller"""
        self.auth_token = auth_token
        self.status_param = status_param
        self.user = None
        self.requests = []
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute request retrieval"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return ({'success': False, 'message': 'Unauthorized'}, 401)
            
            # Check permission
            user_role = self.user.roles.get('role_name') if self.user.roles else None
            if user_role not in ['PIN', 'CSR Rep', 'Platform Management']:
                return ({
                    'success': False,
                    'message': 'You do not have permission to view requests'
                }, 403)
            
            # Get requests based on role
            if user_role == 'PIN':
                # PIN users see only their own requests
                self.requests = Request.by_pin_user(self.user.id)
                if self.status_param:
                    self.requests = [r for r in self.requests if r.status == self.status_param]
            else:
                # CSR Rep and Platform Manager see all requests
                status = self.status_param or 'ACTIVE'
                self.requests = Request.by_status(status)
            
            # Convert to dictionaries
            requests_data = []
            for req in self.requests:
                req_dict = req.to_dict()
                active_assignment = Shortlist.active_assignment_for_request(req.id)
                if active_assignment:
                    req_dict['assignment_status'] = active_assignment.status
                    req_dict['active_assignment'] = active_assignment.to_assignment_dict()
                else:
                    req_dict['assignment_status'] = None
                    req_dict['active_assignment'] = None
                requests_data.append(req_dict)
            
            return ({
                'success': True,
                'data': requests_data,
                'count': len(requests_data)
            }, 200)
            
        except Exception as e:
            print(f"Error getting requests: {str(e)}")
            return ({
                'success': False,
                'message': 'Internal server error'
            }, 500)


class ViewPINRequestDetailController:
    """
    View PIN Request Detail Controller - TRUE OOP
    
    Usage:
        controller = ViewPINRequestDetailController(auth_token, request_id)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, request_id: int):
        """Initialize controller"""
        self.auth_token = auth_token
        self.request_id = request_id
        self.user = None
        self.request = None
    
    def authenticate_user(self) -> bool:
        """Authenticate user from token"""
        self.user = User.verify_token(self.auth_token)
        return self.user is not None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute request detail retrieval"""
        try:
            # Authenticate
            if not self.authenticate_user():
                return ({'success': False, 'message': 'Unauthorized'}, 401)
            
            # Load Request object
            self.request = Request.find(self.request_id)
            if not self.request:
                return ({'success': False, 'message': 'Request not found'}, 404)
            
            # Check permission (PIN users can only see their own)
            user_role = self.user.roles.get('role_name') if self.user.roles else None
            if user_role == 'PIN' and self.request.pin_user_id != self.user.id:
                return ({'success': False, 'message': 'Unauthorized'}, 403)
            
            # Increment view count
            self.request.increment_view_count()
            
            request_dict = self.request.to_dict()
            active_assignment = Shortlist.active_assignment_for_request(self.request.id)
            if active_assignment:
                request_dict['assignment_status'] = active_assignment.status
                request_dict['active_assignment'] = active_assignment.to_assignment_dict()
            else:
                request_dict['assignment_status'] = None
                request_dict['active_assignment'] = None
            
            return ({
                'success': True,
                'data': request_dict
            }, 200)
            
        except Exception as e:
            print(f"Error getting request detail: {str(e)}")
            return ({
                'success': False,
                'message': 'Internal server error'
            }, 500)
