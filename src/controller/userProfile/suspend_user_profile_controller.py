"""
Suspend User Profile Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class SuspendUserProfileController:
    """
    Suspend (Delete) User Profile Controller - TRUE OOP
    
    Usage:
        controller = SuspendUserProfileController(profile_id)
        response, status = controller.execute()
    """
    
    def __init__(self, profile_id: int):
        """Initialize controller"""
        self.profile_id = profile_id
        self.profile = None
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute profile deletion"""
        self.profile = Role.find(self.profile_id)  # Use factory method
        if not self.profile:
            return {
                'success': False,
                'message': 'User profile not found'
            }, 404
        
        # Delete (instance method)
        if self.profile.delete():
            return {
                'success': True,
                'message': 'User profile deleted successfully (cascading delete applied)'
            }, 200
        
        return {
            'success': False,
            'message': 'Failed to delete user profile'
        }, 400
