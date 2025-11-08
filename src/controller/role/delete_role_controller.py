"""
Delete Role Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class DeleteRoleController:
    """
    Delete Role Controller - TRUE OOP
    
    Usage:
        controller = DeleteRoleController(role_id)
        response, status = controller.execute()
    """
    
    def __init__(self, role_id: int):
        """Initialize controller"""
        self.role_id = role_id
        self.role = None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute role deletion"""
        try:
            # Load Role object
            self.role = Role.find(self.role_id)  # Use factory method
            if not self.role:
                return ({'success': False, 'message': 'Role not found'}, 404)
            
            # Delete (instance method)
            if self.role.delete():
                return ({
                    'success': True,
                    'message': 'Role deleted successfully'
                }, 200)
            
            return ({
                'success': False,
                'message': 'Failed to delete role'
            }, 500)
            
        except Exception as e:
            return ({'success': False, 'message': str(e)}, 500)
