"""
Update Role Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class UpdateRoleController:
    """
    Update Role Controller - TRUE OOP
    
    Usage:
        controller = UpdateRoleController(role_id, data)
        response, status = controller.execute()
    """
    
    def __init__(self, role_id: int, data: Dict):
        """Initialize controller"""
        self.role_id = role_id
        self.data = data
        self.role = None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute role update"""
        try:
            # Load Role object
            self.role = Role.find(self.role_id)  # Use factory method
            if not self.role:
                return ({'success': False, 'message': 'Role not found'}, 404)
            
            # Update role attributes
            if 'role_name' in self.data:
                self.role.role_name = self.data['role_name']
            if 'role_code' in self.data:
                self.role.role_code = self.data['role_code']
            if 'description' in self.data:
                self.role.description = self.data['description']
            if 'dashboard_route' in self.data:
                self.role.dashboard_route = self.data['dashboard_route']
            
            # Save (instance method)
            if self.role.update():
                return ({
                    'success': True,
                    'data': self.role.to_dict(),
                    'message': 'Role updated successfully'
                }, 200)
            
            return ({
                'success': False,
                'message': 'Failed to update role'
            }, 500)
            
        except Exception as e:
            return ({'success': False, 'message': str(e)}, 500)
