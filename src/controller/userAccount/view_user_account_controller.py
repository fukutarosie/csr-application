"""
View User Account Controllers - TRUE OOP Implementation
"""

from typing import Dict, Tuple, Optional
from src.entity import User, Role


class ViewAllUserAccountsController:
    """
    View All User Accounts Controller - TRUE OOP
    
    Usage:
        controller = ViewAllUserAccountsController()
        response, status = controller.execute()
    """
    
    def __init__(self):
        """Initialize controller"""
        self.users = []
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute retrieval of all users
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Get all User objects (factory method)
            self.users = User.all()
            
            # Convert to dictionaries
            users_data = [user.to_dict() for user in self.users]
            
            return {
                'success': True,
                'data': users_data,
                'count': len(users_data)
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500


class ViewOneUserAccountController:
    """
    View One User Account Controller - TRUE OOP
    
    Usage:
        controller = ViewOneUserAccountController(user_id)
        response, status = controller.execute()
    """
    
    def __init__(self, user_id: int):
        """
        Initialize controller with user ID
        
        Args:
            user_id: ID of user to retrieve
        """
        self.user_id = user_id
        self.user = None
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute retrieval of specific user
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Load User object (factory method)
            self.user = User.find(self.user_id)
            
            if not self.user:
                return {
                    'success': False,
                    'message': 'User account not found'
                }, 404
            
            return {
                'success': True,
                'data': self.user.to_dict()
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500
