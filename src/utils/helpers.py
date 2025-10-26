"""
Controller Helper Functions
Reusable utilities for BOUNDARY layer (controllers)
"""

from typing import Optional, Tuple
from flask import request


class TokenHelpers:
    """Helper functions for token extraction and handling"""
    
    BEARER_PREFIX = "Bearer "
    
    @staticmethod
    def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
        """
        Extract JWT token from Authorization header
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            Token string or None if invalid format
            
        Example:
            >>> extract_bearer_token("Bearer eyJhbGc...")
            "eyJhbGc..."
        """
        if not auth_header:
            return None
        
        if not isinstance(auth_header, str):
            return None
        
        if not auth_header.startswith(TokenHelpers.BEARER_PREFIX):
            return None
        
        token = auth_header[len(TokenHelpers.BEARER_PREFIX):]
        
        if not token or len(token) < 10:  # Token should be reasonably long
            return None
        
        return token
    
    @staticmethod
    def get_token_from_request() -> Optional[str]:
        """
        Extract token from current request Authorization header
        
        Returns:
            Token string or None
            
        Usage:
            token = get_token_from_request()
            if not token:
                return error
        """
        auth_header = request.headers.get('Authorization')
        return TokenHelpers.extract_bearer_token(auth_header)
    
    @staticmethod
    def validate_bearer_format(auth_header: Optional[str]) -> Tuple[bool, str]:
        """
        Validate Authorization header format
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not auth_header:
            return False, "No token provided"
        
        if not isinstance(auth_header, str):
            return False, "Invalid token format"
        
        if not auth_header.startswith(TokenHelpers.BEARER_PREFIX):
            return False, "Token must start with 'Bearer '"
        
        token = auth_header[len(TokenHelpers.BEARER_PREFIX):]
        
        if not token or len(token) < 10:
            return False, "Invalid token format"
        
        return True, ""


class RequestHelpers:
    """Helper functions for request handling"""
    
    @staticmethod
    def get_json_data() -> Optional[dict]:
        """
        Safely extract JSON data from request
        
        Returns:
            Dictionary of JSON data or None
        """
        try:
            data = request.get_json()
            return data if isinstance(data, dict) else None
        except Exception as e:
            return None
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> Tuple[bool, str, list]:
        """
        Validate that all required fields are present and not empty
        
        Args:
            data: Dictionary of data
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, error_message, missing_fields)
            
        Example:
            is_valid, error, missing = validate_required_fields(
                data,
                ['username', 'password', 'email']
            )
            if not is_valid:
                return error  # or specific field info
        """
        if not data:
            return False, "Request body is required", required_fields
        
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            field_list = ", ".join(missing_fields)
            error_msg = f"Missing required fields: {field_list}"
            return False, error_msg, missing_fields
        
        return True, "", []
    
    @staticmethod
    def validate_json_body() -> Tuple[bool, str]:
        """
        Validate that request body is valid JSON
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if request.content_type and 'application/json' not in request.content_type:
            return False, "Content-Type must be application/json"
        
        data = RequestHelpers.get_json_data()
        if data is None:
            return False, "Invalid JSON body"
        
        return True, ""


class ResponseHelpers:
    """Helper functions for formatting responses"""
    
    @staticmethod
    def success_response(data: dict = None, message: str = None, status_code: int = 200) -> Tuple[dict, int]:
        """
        Create standardized success response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            
        Returns:
            Tuple of (response_dict, status_code)
            
        Example:
            response, code = success_response(
                data={'user': user_data},
                message='User created successfully',
                status_code=201
            )
            return jsonify(response), code
        """
        response = {
            'success': True,
            'message': message or 'Operation successful'
        }
        
        if data:
            response['data'] = data
        
        return response, status_code
    
    @staticmethod
    def error_response(message: str, error_code: str = None, status_code: int = 400, 
                      details: dict = None) -> Tuple[dict, int]:
        """
        Create standardized error response
        
        Args:
            message: Error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details
            
        Returns:
            Tuple of (response_dict, status_code)
            
        Example:
            response, code = error_response(
                message='Invalid credentials',
                error_code='AUTH_FAILED',
                status_code=401
            )
            return jsonify(response), code
        """
        response = {
            'success': False,
            'message': message
        }
        
        if error_code:
            response['error_code'] = error_code
        
        if details:
            response['details'] = details
        
        return response, status_code
    
    @staticmethod
    def validation_error_response(validation_errors: list, status_code: int = 400) -> Tuple[dict, int]:
        """
        Create validation error response
        
        Args:
            validation_errors: List of validation error messages
            status_code: HTTP status code
            
        Returns:
            Tuple of (response_dict, status_code)
            
        Example:
            errors = ['Username too short', 'Email invalid']
            response, code = validation_error_response(errors)
            return jsonify(response), code
        """
        response = {
            'success': False,
            'message': 'Validation failed',
            'error_code': 'VALIDATION_ERROR',
            'errors': validation_errors
        }
        
        return response, status_code


class DataHelpers:
    """Helper functions for data manipulation"""
    
    @staticmethod
    def exclude_fields(data: dict, exclude_fields: list) -> dict:
        """
        Exclude specified fields from dictionary
        
        Args:
            data: Dictionary to filter
            exclude_fields: List of field names to exclude
            
        Returns:
            Filtered dictionary
            
        Example:
            user = exclude_fields(user, ['password_hash', 'password'])
        """
        return {k: v for k, v in data.items() if k not in exclude_fields}
    
    @staticmethod
    def include_only_fields(data: dict, include_fields: list) -> dict:
        """
        Include only specified fields from dictionary
        
        Args:
            data: Dictionary to filter
            include_fields: List of field names to include
            
        Returns:
            Filtered dictionary
            
        Example:
            user_public = include_only_fields(user, ['id', 'username', 'email', 'full_name'])
        """
        return {k: v for k, v in data.items() if k in include_fields}
    
    @staticmethod
    def format_user_response(user: dict, include_role: bool = False) -> dict:
        """
        Format user data for API response
        
        Args:
            user: User dictionary from database
            include_role: Whether to include role information
            
        Returns:
            Formatted user data
        """
        response = {
            'id': user.get('id'),
            'username': user.get('username'),
            'email': user.get('email'),
            'full_name': user.get('full_name'),
            'is_active': user.get('is_active'),
        }
        
        if include_role and 'role' in user:
            response['role'] = user['role']
        
        return response
    
    @staticmethod
    def format_profile_response(profile: dict, include_user: bool = False) -> dict:
        """
        Format profile data for API response
        
        Args:
            profile: Profile dictionary from database
            include_user: Whether to include user information
            
        Returns:
            Formatted profile data
        """
        response = {
            'id': profile.get('id'),
            'user_id': profile.get('user_id'),
            'phone': profile.get('phone'),
            'address': profile.get('address'),
        }
        
        if include_user and 'user' in profile:
            response['user'] = profile['user']
        
        return response


class PaginationHelpers:
    """Helper functions for pagination"""
    
    @staticmethod
    def get_pagination_params(default_page: int = 1, default_limit: int = 10, 
                             max_limit: int = 100) -> Tuple[int, int]:
        """
        Extract and validate pagination parameters from request
        
        Args:
            default_page: Default page number
            default_limit: Default page limit
            max_limit: Maximum allowed limit
            
        Returns:
            Tuple of (page, limit)
            
        Example:
            page, limit = get_pagination_params()
            # Extract from: ?page=2&limit=20
        """
        try:
            page = int(request.args.get('page', default_page))
            limit = int(request.args.get('limit', default_limit))
            
            # Validate values
            if page < 1:
                page = default_page
            if limit < 1:
                limit = default_limit
            if limit > max_limit:
                limit = max_limit
            
            return page, limit
        except (ValueError, TypeError):
            return default_page, default_limit
    
    @staticmethod
    def create_pagination_meta(total_items: int, page: int, limit: int) -> dict:
        """
        Create pagination metadata
        
        Args:
            total_items: Total number of items
            page: Current page number
            limit: Items per page
            
        Returns:
            Pagination metadata dictionary
            
        Example:
            meta = create_pagination_meta(150, 2, 10)
            # Returns: {
            #   'page': 2, 
            #   'limit': 10, 
            #   'total_items': 150, 
            #   'total_pages': 15
            # }
        """
        total_pages = (total_items + limit - 1) // limit
        
        return {
            'page': page,
            'limit': limit,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }
