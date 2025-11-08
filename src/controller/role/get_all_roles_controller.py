"""
Get All Roles Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class GetAllRolesController:
    """
    Get All Roles Controller - TRUE OOP
    
    Usage:
        controller = GetAllRolesController()
        response, status = controller.execute()
    """
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute roles retrieval"""
        try:
            roles = Role.all()  # Use factory method
            roles_data = [role.to_dict() for role in roles]
            
            return ({
                'success': True,
                'data': roles_data
            }, 200)
            
        except Exception as e:
            return ({'success': False, 'message': str(e)}, 500)
