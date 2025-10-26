"""
Input Sanitization Utilities
Functions to sanitize and clean user inputs
"""

import html
from typing import Any, Dict


class Sanitizers:
    """Centralized sanitization functions for user inputs"""
    
    @staticmethod
    def sanitize_string(value: str, lowercase: bool = False, max_length: int = None) -> str:
        """
        Sanitize a string by trimming whitespace and optionally converting to lowercase
        
        Args:
            value: String to sanitize
            lowercase: Whether to convert to lowercase
            max_length: Maximum length to truncate to (optional)
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""
        
        # Strip whitespace
        sanitized = value.strip()
        
        # Convert to lowercase if requested
        if lowercase:
            sanitized = sanitized.lower()
        
        # Truncate if max_length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize email address
        
        Args:
            email: Email to sanitize
            
        Returns:
            Sanitized email (trimmed and lowercase)
        """
        return Sanitizers.sanitize_string(email, lowercase=True)
    
    @staticmethod
    def sanitize_username(username: str) -> str:
        """
        Sanitize username
        
        Args:
            username: Username to sanitize
            
        Returns:
            Sanitized username (trimmed, lowercase, max 20 chars)
        """
        return Sanitizers.sanitize_string(username, lowercase=True, max_length=20)
    
    @staticmethod
    def sanitize_full_name(full_name: str) -> str:
        """
        Sanitize full name (trim, no lowercase, max 100 chars)
        
        Args:
            full_name: Full name to sanitize
            
        Returns:
            Sanitized full name
        """
        return Sanitizers.sanitize_string(full_name, lowercase=False, max_length=100)
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """
        Sanitize phone number (trim, keep numbers and common separators)
        
        Args:
            phone: Phone to sanitize
            
        Returns:
            Sanitized phone number
        """
        if not isinstance(phone, str):
            return ""
        
        # Trim whitespace
        sanitized = phone.strip()
        
        # Allow digits, spaces, hyphens, parentheses, plus sign
        allowed_chars = set('0123456789- ()+')
        sanitized = ''.join(c for c in sanitized if c in allowed_chars)
        
        return sanitized
    
    @staticmethod
    def sanitize_address(address: str) -> str:
        """
        Sanitize address (trim, max 200 chars)
        
        Args:
            address: Address to sanitize
            
        Returns:
            Sanitized address
        """
        return Sanitizers.sanitize_string(address, lowercase=False, max_length=200)
    
    @staticmethod
    def html_escape(text: str) -> str:
        """
        Escape HTML special characters
        
        Args:
            text: Text to escape
            
        Returns:
            HTML escaped text
        """
        if not isinstance(text, str):
            return ""
        
        return html.escape(text)
    
    @staticmethod
    def sanitize_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize user data from request
        
        Args:
            data: Dictionary of user data
            
        Returns:
            Sanitized user data
        """
        sanitized = {}
        
        if 'username' in data:
            sanitized['username'] = Sanitizers.sanitize_username(str(data['username']))
        
        if 'email' in data:
            sanitized['email'] = Sanitizers.sanitize_email(str(data['email']))
        
        if 'password' in data:
            # Don't lowercase passwords, but still trim
            sanitized['password'] = Sanitizers.sanitize_string(str(data['password']))
        
        if 'full_name' in data:
            sanitized['full_name'] = Sanitizers.sanitize_full_name(str(data['full_name']))
        
        if 'phone' in data and data['phone']:
            sanitized['phone'] = Sanitizers.sanitize_phone(str(data['phone']))
        
        if 'address' in data and data['address']:
            sanitized['address'] = Sanitizers.sanitize_address(str(data['address']))
        
        if 'role_id' in data:
            try:
                sanitized['role_id'] = int(data['role_id'])
            except (ValueError, TypeError):
                sanitized['role_id'] = None
        
        return sanitized
    
    @staticmethod
    def sanitize_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize profile data from request
        
        Args:
            data: Dictionary of profile data
            
        Returns:
            Sanitized profile data
        """
        sanitized = {}
        
        if 'user_id' in data:
            try:
                sanitized['user_id'] = int(data['user_id'])
            except (ValueError, TypeError):
                sanitized['user_id'] = None
        
        if 'phone' in data and data['phone']:
            sanitized['phone'] = Sanitizers.sanitize_phone(str(data['phone']))
        
        if 'address' in data and data['address']:
            sanitized['address'] = Sanitizers.sanitize_address(str(data['address']))
        
        return sanitized
