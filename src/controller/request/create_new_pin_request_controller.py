"""
Create New PIN Request Controller - TRUE OOP Implementation
Holds request data in memory and orchestrates request creation
"""

from typing import Dict, Tuple, List
from src.entity.request import Request
from src.entity import User
from src.utils.image_upload import save_base64_image


class CreateNewPINRequestController:
    """
    Create New PIN Request Controller - TRUE OOP
    
    This controller holds request data in memory and orchestrates request creation.
    It demonstrates proper OOP:
    - Has instance variables (data in memory)
    - Uses instance methods
    - Creates Request objects and calls their instance methods
    
    Usage:
        controller = CreateNewPINRequestController(auth_token, request_data)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, request_data: Dict):
        """
        Initialize controller with auth token and request data
        
        Args:
            auth_token: JWT authentication token
            request_data: Request data from HTTP request
        """
        # Instance variables (object state - data in memory)
        self.auth_token = auth_token
        self.request_data = request_data
        self.user = None  # Will hold User object
        self.request = None  # Will hold Request object
        self.errors: List[str] = []
        self.image_url: str = None
    
    # ============================================================================
    # AUTHENTICATION METHOD (Instance method)
    # ============================================================================
    
    def authenticate_user(self) -> bool:
        """
        Authenticate user from token
        
        Returns:
            True if authenticated, False otherwise
        """
        self.user = User.verify_token(self.auth_token)
        if not self.user:
            self.errors.append('Unauthorized')
            return False
        return True
    
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
            self.errors.append('No data provided')
            return False
        
        # Validate title
        title = self.request_data.get('title', '').strip()
        if not title or len(title) < 5:
            self.errors.append('Title is required (minimum 5 characters)')
        
        # Validate description
        description = self.request_data.get('description', '').strip()
        if not description or len(description) < 10:
            self.errors.append('Description is required (minimum 10 characters)')
        
        # Validate service_type
        service_type = self.request_data.get('service_type', '').strip()
        if not service_type:
            self.errors.append('Service type is required')
        
        # Validate region
        region = self.request_data.get('region', '').strip()
        if not region:
            self.errors.append('Region is required')
        
        # Validate requested_by_date
        requested_by_date = self.request_data.get('requested_by_date', '').strip()
        if not requested_by_date:
            self.errors.append('Requested by date is required')
        
        # Validate image
        image_data = self.request_data.get('image', '').strip()
        if not image_data:
            self.errors.append('Image is required')
        
        return len(self.errors) == 0
    
    def process_image_upload(self) -> bool:
        """
        Process image upload
        
        Returns:
            True if successful, False otherwise
        """
        image_data = self.request_data.get('image', '').strip()
        title = self.request_data.get('title', '').strip()
        
        success, result, error_msg = save_base64_image(image_data, title)
        if not success:
            self.errors.append(f'Image upload failed: {error_msg}')
            return False
        
        self.image_url = result
        return True
    
    def create_request_object(self) -> None:
        """
        Create Request object from request data
        Stores Request object in self.request (data in memory)
        """
        self.request = Request()  # Create Request object
        
        # Set instance variables on Request object (data in memory)
        self.request.pin_user_id = self.user.id
        self.request.title = self.request_data.get('title', '').strip()
        self.request.description = self.request_data.get('description', '').strip()
        self.request.service_type = self.request_data.get('service_type', '').strip()
        self.request.region = self.request_data.get('region', '').strip()
        self.request.requested_by_date = self.request_data.get('requested_by_date', '').strip()
        self.request.image_url = self.image_url
        self.request.status = Request.STATUS_ACTIVE
    
    # ============================================================================
    # MAIN EXECUTION METHOD (Instance method)
    # ============================================================================
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute request creation process
        
        This is the main method that orchestrates the entire process:
        1. Authenticate user
        2. Validate request data
        3. Process image upload
        4. Create Request object (holds data in memory)
        5. Save Request object (Request does the actual database work)
        6. Return response
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Step 1: Authenticate user
            if not self.authenticate_user():
                return ({
                    'success': False,
                    'message': '; '.join(self.errors)
                }, 401)
            
            # Step 2: Validate request data
            if not self.validate_request_data():
                return ({
                    'success': False,
                    'message': '; '.join(self.errors)
                }, 400)
            
            # Step 3: Process image upload
            if not self.process_image_upload():
                return ({
                    'success': False,
                    'message': '; '.join(self.errors)
                }, 400)
            
            # Step 4: Create Request object (holds data in memory)
            self.create_request_object()
            
            # Step 5: Save Request object (Request.save() does the actual work)
            try:
                self.request.save()  # Instance method - does actual database work
            except ValueError as e:
                return ({
                    'success': False,
                    'message': str(e)
                }, 400)
            
            # Step 6: Return success response
            return ({
                'success': True,
                'data': self.request.to_dict(),
                'message': 'Request created successfully'
            }, 201)
            
        except Exception as e:
            print(f"[ERROR] Create request error: {str(e)}")
            return ({
                'success': False,
                'message': 'Internal server error'
            }, 500)
