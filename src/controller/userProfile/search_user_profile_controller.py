"""
Search User Profile Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class SearchUserProfileController:
    """
    Search User Profile Controller - TRUE OOP
    
    Usage:
        controller = SearchUserProfileController(payload)
        response, status = controller.execute()
    """
    
    def __init__(self, payload: Dict = None):
        """Initialize controller"""
        self.payload = payload or {}
        self.search_term = self.payload.get('search', '')
        self.profiles = []
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute profile search"""
        # Get all profiles
        all_profiles = Role.all()  # Use factory method
        
        # Filter by search term
        if self.search_term:
            search_lower = self.search_term.lower()
            self.profiles = [
                profile for profile in all_profiles
                if search_lower in profile.role_name.lower()
                or search_lower in profile.role_code.lower()
            ]
        else:
            self.profiles = all_profiles
        
        # Convert to dictionaries
        profiles_data = [profile.to_dict() for profile in self.profiles]
        
        return {
            'success': True,
            'data': profiles_data,
            'count': len(profiles_data)
        }, 200
