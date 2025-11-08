"""
Create User Profile Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity import Role


class CreateUserProfileController:
    """
    Create User Profile Controller - TRUE OOP
    
    Usage:
        controller = CreateUserProfileController(payload)
        response, status = controller.execute()
    """
    
    REQUIRED_FIELDS = {"role_name", "role_code", "description"}
    
    def __init__(self, payload: Dict):
        """Initialize controller"""
        self.payload = payload
        self.role = None
    
    def validate_payload(self) -> Tuple[bool, str]:
        """Validate request payload"""
        if self.payload is None:
            return False, "Request payload is required"
        
        missing_fields = self.REQUIRED_FIELDS - self.payload.keys()
        if missing_fields:
            return False, f"Missing required fields: {', '.join(sorted(missing_fields))}"
        
        return True, ""
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute profile creation"""
        # Validate
        is_valid, error_msg = self.validate_payload()
        if not is_valid:
            return {"success": False, "message": error_msg}, 400
        
        # Create Role object
        self.role = Role()
        self.role.role_name = self.payload["role_name"]
        self.role.role_code = self.payload["role_code"]
        self.role.description = self.payload["description"]
        self.role.dashboard_route = self.payload.get("dashboard_route", "/dashboard")
        
        # Save (instance method)
        if self.role.save():
            return {
                "success": True,
                "data": self.role.to_dict(),
                "message": "User profile created successfully"
            }, 201
        
        return {
            "success": False,
            "message": "Failed to create user profile"
        }, 400
