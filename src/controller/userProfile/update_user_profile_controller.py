"""
Update User Profile Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class UpdateUserProfileController:
    """
    Update User Profile Controller - TRUE OOP
    
    Usage:
        controller = UpdateUserProfileController(profile_id, payload)
        response, status = controller.execute()
    """
    
    def __init__(self, profile_id: int, payload: Dict):
        """Initialize controller"""
        self.profile_id = profile_id
        self.payload = payload
        self.role = None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute profile update"""
        if self.payload is None:
            return {
                'success': False,
                'message': 'Request payload is required'
            }, 400
        
        # Load Role object
        self.role = Role.find(self.profile_id)
        if not self.role:
            return {
                'success': False,
                'message': 'User profile not found'
            }, 404
        
        # Update role attributes
        if 'role_name' in self.payload:
            self.role.role_name = self.payload['role_name']
        if 'role_code' in self.payload:
            self.role.role_code = self.payload['role_code']
        if 'description' in self.payload:
            self.role.description = self.payload['description']
        if 'dashboard_route' in self.payload:
            self.role.dashboard_route = self.payload['dashboard_route']
        
        # Save (instance method)
        if self.role.update():
            return {
                'success': True,
                'data': self.role.to_dict(),
                'message': 'User profile updated successfully'
            }, 200
        
        return {
            'success': False,
            'message': 'Failed to update user profile'
        }, 400
