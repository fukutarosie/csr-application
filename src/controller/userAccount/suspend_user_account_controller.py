"""
Suspend/Activate/Delete User Account Controllers - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import User, Role


class SuspendUserAccountController:
    """
    Suspend User Account Controller - TRUE OOP
    
    Usage:
        controller = SuspendUserAccountController(user_id)
        response, status = controller.execute()
    """
    
    def __init__(self, user_id: int):
        """
        Initialize controller with user ID
        
        Args:
            user_id: ID of user to suspend
        """
        self.user_id = user_id
        self.user = None
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute user suspension
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Load User object
            self.user = User.find(self.user_id)
            if not self.user:
                return {
                    'success': False,
                    'message': 'User account not found'
                }, 404
            
            # Deactivate user (instance method)
            self.user.deactivate()
            
            return {
                'success': True,
                'data': self.user.to_dict(),
                'message': 'User account suspended successfully'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500


class ActivateUserAccountController:
    """
    Activate User Account Controller - TRUE OOP
    
    Usage:
        controller = ActivateUserAccountController(user_id)
        response, status = controller.execute()
    """
    
    def __init__(self, user_id: int):
        """
        Initialize controller with user ID
        
        Args:
            user_id: ID of user to activate
        """
        self.user_id = user_id
        self.user = None
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute user activation
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Load User object
            self.user = User.find(self.user_id)
            if not self.user:
                return {
                    'success': False,
                    'message': 'User account not found'
                }, 404
            
            # Activate user (instance method)
            self.user.activate()
            
            return {
                'success': True,
                'data': self.user.to_dict(),
                'message': 'User account activated successfully'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500


class DeleteUserAccountController:
    """
    Delete User Account Controller - TRUE OOP
    
    Usage:
        controller = DeleteUserAccountController(user_id)
        response, status = controller.execute()
    """
    
    def __init__(self, user_id: int):
        """
        Initialize controller with user ID
        
        Args:
            user_id: ID of user to delete
        """
        self.user_id = user_id
        self.user = None
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute user deletion
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Load User object
            self.user = User.find(self.user_id)
            if not self.user:
                return {
                    'success': False,
                    'message': 'User account not found'
                }, 404
            
            # Delete user (instance method)
            self.user.delete()
            
            return {
                'success': True,
                'message': 'User account deleted successfully'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500
