"""
Login Controller - TRUE OOP Implementation
Holds request data in memory and orchestrates authentication
"""

from typing import Dict, Tuple, List
from src.entity import User, Role
from src.utils.validators import Validators
from src.utils.sanitizers import Sanitizers
from src.utils.helpers import TokenHelpers, RequestHelpers, ResponseHelpers


class LoginController:
    """
    Login Controller - TRUE OOP
    
    This controller holds request data in memory and orchestrates authentication.
    It demonstrates proper OOP:
    - Has instance variables (data in memory)
    - Uses instance methods
    - Works with User objects and calls their instance methods
    
    Usage:
        controller = LoginController(request_data)
        response, status = controller.execute()
    """
    
    def __init__(self, request_data: Dict):
        """
        Initialize controller with request data
        
        Args:
            request_data: Login data from HTTP request
        """
        # Instance variables (object state - data in memory)
        self.request_data = request_data
        self.user = None  # Will hold User object
        self.errors: List[str] = []
        self.sanitized_data: Dict = {}
    
    # ============================================================================
    # VALIDATION METHODS (Instance methods)
    # ============================================================================
    
    def validate_request_data(self) -> bool:
        """
        Validate request data
        
        Returns:
            True if valid, False otherwise (errors stored in self.errors)
        """
        if not self.request_data:
            self.errors.append('Request body is required')
            return False
        
        # Validate required fields
        is_valid, error_msg, missing = RequestHelpers.validate_required_fields(
            self.request_data, ['username', 'password', 'role_name']
        )
        if not is_valid:
            self.errors.append(error_msg)
            return False
        
        # Sanitize input data
        self.sanitized_data = {
            'username': Sanitizers.sanitize_username(self.request_data.get('username', '')),
            'password': self.request_data.get('password', ''),  # Don't modify password
            'role_name': Sanitizers.sanitize_string(self.request_data.get('role_name', ''))
        }
        
        # Validate username format
        is_valid, error_msg = Validators.validate_username(self.sanitized_data['username'])
        if not is_valid:
            self.errors.append(error_msg)
            return False
        
        # Validate password format
        is_valid, error_msg = Validators.validate_password(self.sanitized_data['password'])
        if not is_valid:
            self.errors.append(error_msg)
            return False
        
        return True
    
    def authenticate_user(self) -> bool:
        """
        Authenticate user using User.authenticate factory method
        
        Returns:
            True if authenticated, False otherwise
        """
        self.user = User.authenticate(
            username=self.sanitized_data['username'],
            password=self.sanitized_data['password'],
            role_name=self.sanitized_data['role_name']
        )
        
        if not self.user:
            self.errors.append('Invalid credentials or user role mismatch')
            return False
        
        return True
    
    # ============================================================================
    # MAIN EXECUTION METHOD (Instance method)
    # ============================================================================
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute login process
        
        This is the main method that orchestrates the entire process:
        1. Validate request data
        2. Authenticate user (returns User object)
        3. Generate session token
        4. Return response with user data and token
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Step 1: Validate request data
            if not self.validate_request_data():
                return ResponseHelpers.error_response(
                    message='; '.join(self.errors),
                    error_code='VALIDATION_ERROR',
                    status_code=400
                )
            
            # Step 2: Authenticate user (returns User object)
            if not self.authenticate_user():
                return ResponseHelpers.error_response(
                    message='; '.join(self.errors),
                    error_code='AUTH_FAILED',
                    status_code=401
                )
            
            # Step 3: Generate session token
            token = self.user.generate_session_token()
            
            # Step 4: Return success response
            response_data = {
                'token': token,
                'user': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'full_name': self.user.full_name,
                    'email': self.user.email,
                    'role_id': self.user.role_id,
                    'role': self.user.roles if self.user.roles else None
                }
            }
            
            return ResponseHelpers.success_response(
                data=response_data,
                message='Login successful',
                status_code=200
            )
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Login error: {str(e)}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return ResponseHelpers.error_response(
                message='An unexpected error occurred during login',
                error_code='SERVER_ERROR',
                status_code=500
            )


class LogoutController:
    """
    Logout Controller - TRUE OOP
    
    Usage:
        controller = LogoutController(auth_token)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str):
        """
        Initialize controller with auth token
        
        Args:
            auth_token: JWT authentication token
        """
        self.auth_token = auth_token
        self.user = None
        self.errors: List[str] = []
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute logout process
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Verify token and get user
            self.user = User.verify_token(self.auth_token)
            if not self.user:
                return ResponseHelpers.error_response(
                    message='Invalid or expired token',
                    error_code='INVALID_TOKEN',
                    status_code=401
                )
            
            # Return success response
            return ResponseHelpers.success_response(
                message='Logout successful',
                status_code=200
            )
            
        except Exception as e:
            print(f"[ERROR] Logout error: {str(e)}")
            return ResponseHelpers.error_response(
                message='An unexpected error occurred during logout',
                error_code='SERVER_ERROR',
                status_code=500
            )


class VerifyTokenController:
    """
    Verify Token Controller - TRUE OOP
    
    Usage:
        controller = VerifyTokenController(auth_token)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str):
        """
        Initialize controller with auth token
        
        Args:
            auth_token: JWT authentication token
        """
        self.auth_token = auth_token
        self.user = None
        self.errors: List[str] = []
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute token verification process
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Verify token and get user
            self.user = User.verify_token(self.auth_token)
            if not self.user:
                return ResponseHelpers.error_response(
                    message='Invalid or expired token',
                    error_code='INVALID_TOKEN',
                    status_code=401
                )
            
            # Return success response with user data
            response_data = {
                'user': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'full_name': self.user.full_name,
                    'email': self.user.email,
                    'role_id': self.user.role_id,
                    'role': self.user.roles if self.user.roles else None
                }
            }
            
            return ResponseHelpers.success_response(
                data=response_data,
                message='Token is valid',
                status_code=200
            )
            
        except Exception as e:
            print(f"[ERROR] Verify token error: {str(e)}")
            return ResponseHelpers.error_response(
                message='An unexpected error occurred during token verification',
                error_code='SERVER_ERROR',
                status_code=500
            )
