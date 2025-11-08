"""
Get Role Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class GetRoleController:
    """
    Get Role Controller - TRUE OOP
    
    Usage:
        controller = GetRoleController(role_id)
        response, status = controller.execute()
    """
    
    def __init__(self, role_id: int):
        """Initialize controller"""
        self.role_id = role_id
        self.role = None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute role retrieval"""
        try:
            self.role = Role.find(self.role_id)  # Use factory method
            if not self.role:
                return ({'success': False, 'message': 'Role not found'}, 404)
            
            return ({
                'success': True,
                'data': self.role.to_dict()
            }, 200)
            
        except Exception as e:
            return ({'success': False, 'message': str(e)}, 500)
