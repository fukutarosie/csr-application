"""
Create Role Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class CreateRoleController:
    """
    Create Role Controller - TRUE OOP
    
    Usage:
        controller = CreateRoleController(data)
        response, status = controller.execute()
    """
    
    def __init__(self, data: Dict):
        """Initialize controller"""
        self.data = data
        self.role = None
    
    def validate_data(self) -> Tuple[bool, str]:
        """Validate request data"""
        if not self.data.get('role_name') or not self.data.get('role_code') or not self.data.get('description'):
            return False, 'Missing required fields: role_name, role_code, description'
        return True, ''
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute role creation"""
        try:
            # Validate
            is_valid, error_msg = self.validate_data()
            if not is_valid:
                return ({'success': False, 'message': error_msg}, 400)
            
            # Create Role object
            self.role = Role()
            self.role.role_name = self.data['role_name']
            self.role.role_code = self.data['role_code']
            self.role.description = self.data['description']
            self.role.dashboard_route = self.data.get('dashboard_route', '/')
            
            # Save (instance method)
            if self.role.save():
                return ({
                    'success': True,
                    'data': self.role.to_dict(),
                    'message': 'Role created successfully'
                }, 201)
            
            return ({
                'success': False,
                'message': 'Role already exists or failed to create'
            }, 400)
            
        except Exception as e:
            return ({'success': False, 'message': str(e)}, 500)
