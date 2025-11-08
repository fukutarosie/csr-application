"""
Search User Account Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import User, Role


class SearchUserAccountController:
    """
    Search User Account Controller - TRUE OOP
    
    Usage:
        controller = SearchUserAccountController(search_params)
        response, status = controller.execute()
    """
    
    def __init__(self, search_params: Dict):
        """
        Initialize controller with search parameters
        
        Args:
            search_params: Dictionary with search criteria (username, email, full_name)
        """
        self.search_params = search_params or {}
        self.users = []
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute user search
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Extract search parameters
            username = self.search_params.get('username', '')
            email = self.search_params.get('email', '')
            full_name = self.search_params.get('full_name', '')
            
            # Search for User objects (factory method)
            self.users = User.search(
                username=username,
                email=email,
                full_name=full_name
            )
            
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
