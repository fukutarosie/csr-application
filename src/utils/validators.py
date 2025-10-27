"""
Data Validation Utilities
Centralized validation functions for user inputs
"""

import re
from typing import Tuple


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validators:
    """Centralized validation functions for user inputs"""
    
    # Validation Patterns
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    USERNAME_PATTERN = r'^[a-zA-Z0-9_-]{3,20}$'  # 3-20 chars, alphanumeric, underscore, hyphen
    PHONE_PATTERN = r'^[0-9\-+\s()]{10,}$'  # At least 10 digits
    PASSWORD_MIN_LENGTH = 8
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 20
    FULL_NAME_MIN_LENGTH = 2
    FULL_NAME_MAX_LENGTH = 100
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        email = email.strip().lower()
        
        if len(email) > 100:
            return False, "Email is too long (max 100 characters)"
        
        if not re.match(Validators.EMAIL_PATTERN, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        username = username.strip()
        
        if len(username) < Validators.USERNAME_MIN_LENGTH:
            return False, f"Username must be at least {Validators.USERNAME_MIN_LENGTH} characters"
        
        if len(username) > Validators.USERNAME_MAX_LENGTH:
            return False, f"Username must be at most {Validators.USERNAME_MAX_LENGTH} characters"
        
        if not re.match(Validators.USERNAME_PATTERN, username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str, require_special: bool = False) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            require_special: Whether to require special characters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < Validators.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {Validators.PASSWORD_MIN_LENGTH} characters"
        
        if len(password) > 100:
            return False, "Password is too long (max 100 characters)"
        
        # Check for at least one alphanumeric character (letter OR digit)
        if not any(c.isalnum() for c in password):
            return False, "Password must contain at least letters or numbers"
        
        # Check for special character (optional)
        if require_special and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return False, "Password must contain at least one special character (!@#$%^&*)"
        
        return True, ""
    
    @staticmethod
    def validate_full_name(full_name: str) -> Tuple[bool, str]:
        """
        Validate full name format
        
        Args:
            full_name: Full name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not full_name:
            return False, "Full name is required"
        
        full_name = full_name.strip()
        
        if len(full_name) < Validators.FULL_NAME_MIN_LENGTH:
            return False, f"Full name must be at least {Validators.FULL_NAME_MIN_LENGTH} characters"
        
        if len(full_name) > Validators.FULL_NAME_MAX_LENGTH:
            return False, f"Full name must be at most {Validators.FULL_NAME_MAX_LENGTH} characters"
        
        # Check if contains at least one letter
        if not any(c.isalpha() for c in full_name):
            return False, "Full name must contain at least one letter"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number is required"
        
        phone = phone.strip()
        
        # Remove common separators
        digits_only = re.sub(r'[^\d+]', '', phone)
        
        # Check minimum digits
        if len(digits_only) < 10:
            return False, "Phone number must contain at least 10 digits"
        
        if not re.match(Validators.PHONE_PATTERN, phone):
            return False, "Invalid phone number format"
        
        return True, ""
    
    @staticmethod
    def validate_role_id(role_id: int) -> Tuple[bool, str]:
        """
        Validate role ID
        
        Args:
            role_id: Role ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not role_id:
            return False, "Role ID is required"
        
        if not isinstance(role_id, int) or role_id <= 0:
            return False, "Role ID must be a positive integer"
        
        return True, ""
    
    @staticmethod
    def validate_user_data(username: str, password: str, email: str, full_name: str, 
                          role_id: int, phone: str = None) -> Tuple[bool, str]:
        """
        Validate all user creation data at once
        
        Args:
            username: Username to validate
            password: Password to validate
            email: Email to validate
            full_name: Full name to validate
            role_id: Role ID to validate
            phone: Phone number to validate (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate each field
        validations = [
            Validators.validate_username(username),
            Validators.validate_password(password),
            Validators.validate_email(email),
            Validators.validate_full_name(full_name),
            Validators.validate_role_id(role_id)
        ]
        
        # Add phone validation if provided
        if phone:
            validations.append(Validators.validate_phone(phone))
        
        # Check if any validation failed
        for is_valid, error_message in validations:
            if not is_valid:
                return False, error_message
        
        return True, ""
    
    @staticmethod
    def validate_user_update(updates: dict) -> Tuple[bool, str]:
        """
        Validate user update data
        
        Args:
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not updates:
            return False, "No fields to update"
        
        # Validate email if provided
        if 'email' in updates:
            is_valid, error = Validators.validate_email(updates['email'])
            if not is_valid:
                return False, error
        
        # Validate password if provided
        if 'password' in updates:
            is_valid, error = Validators.validate_password(updates['password'])
            if not is_valid:
                return False, error
        
        # Validate full_name if provided
        if 'full_name' in updates:
            is_valid, error = Validators.validate_full_name(updates['full_name'])
            if not is_valid:
                return False, error
        
        # Validate role_id if provided
        if 'role_id' in updates:
            is_valid, error = Validators.validate_role_id(updates['role_id'])
            if not is_valid:
                return False, error
        
        # Validate phone if provided
        if 'phone' in updates:
            is_valid, error = Validators.validate_phone(updates['phone'])
            if not is_valid:
                return False, error
        
        return True, ""


class ProfileValidators:
    """Validation functions for user profiles"""
    
    PHONE_PATTERN = r'^[0-9\-+\s()]{10,}$'
    ADDRESS_MIN_LENGTH = 5
    ADDRESS_MAX_LENGTH = 200
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number"""
        if not phone:
            return False, "Phone number is required"
        
        if not re.match(ProfileValidators.PHONE_PATTERN, phone):
            return False, "Invalid phone number format"
        
        return True, ""
    
    @staticmethod
    def validate_address(address: str) -> Tuple[bool, str]:
        """Validate address"""
        if not address:
            return False, "Address is required"
        
        address = address.strip()
        
        if len(address) < ProfileValidators.ADDRESS_MIN_LENGTH:
            return False, f"Address must be at least {ProfileValidators.ADDRESS_MIN_LENGTH} characters"
        
        if len(address) > ProfileValidators.ADDRESS_MAX_LENGTH:
            return False, f"Address must be at most {ProfileValidators.ADDRESS_MAX_LENGTH} characters"
        
        return True, ""
    
    @staticmethod
    def validate_profile_data(user_id: int, phone: str, address: str) -> Tuple[bool, str]:
        """Validate all profile data"""
        if not user_id or not isinstance(user_id, int) or user_id <= 0:
            return False, "Valid user ID is required"
        
        is_valid, error = ProfileValidators.validate_phone(phone)
        if not is_valid:
            return False, error
        
        is_valid, error = ProfileValidators.validate_address(address)
        if not is_valid:
            return False, error
        
        return True, ""
