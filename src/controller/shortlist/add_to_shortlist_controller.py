"""
Add to Shortlist Controller - TRUE OOP Implementation
Holds request data in memory and orchestrates shortlist creation
"""

from typing import Dict, Tuple, List
from src.entity.shortlist import Shortlist
from src.entity import User
from src.utils.helpers import RequestHelpers, ResponseHelpers


class AddToShortlistController:
    """
    Add to Shortlist Controller - TRUE OOP
    
    This controller holds request data in memory and orchestrates shortlist creation.
    It demonstrates proper OOP:
    - Has instance variables (data in memory)
    - Uses instance methods
    - Creates Shortlist objects and calls their instance methods
    
    Usage:
        controller = AddToShortlistController(auth_token, request_data)
        response, status = controller.execute()
    """
    
    def __init__(self, auth_token: str, request_data: Dict):
        """
        Initialize controller with auth token and request data
        
        Args:
            auth_token: JWT authentication token
            request_data: Shortlist data from HTTP request
        """
        # Instance variables (object state - data in memory)
        self.auth_token = auth_token
        self.request_data = request_data
        self.user = None  # Will hold User object
        self.shortlist = None  # Will hold Shortlist object
        self.errors: List[str] = []
    
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
            self.errors.append('Invalid or expired token')
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
            self.errors.append('Request body is required')
            return False
        
        # Validate required fields
        required_fields = ['request_id']
        is_valid, error_msg, _ = RequestHelpers.validate_required_fields(
            self.request_data, required_fields
        )
        if not is_valid:
            self.errors.append(error_msg)
            return False
        
        return True
    
    def create_shortlist_object(self) -> None:
        """
        Create Shortlist object from request data
        Stores Shortlist object in self.shortlist (data in memory)
        """
        self.shortlist = Shortlist()  # Create Shortlist object
        
        # Set instance variables on Shortlist object (data in memory)
        self.shortlist.csr_user_id = self.user.id
        self.shortlist.request_id = self.request_data.get('request_id')
        self.shortlist.notes = self.request_data.get('notes')
        self.shortlist.status = Shortlist.STATUS_SHORTLISTED
    
    # ============================================================================
    # MAIN EXECUTION METHOD (Instance method)
    # ============================================================================
    
    def execute(self) -> Tuple[Dict, int]:
        """
        Execute shortlist creation process
        
        This is the main method that orchestrates the entire process:
        1. Authenticate user
        2. Validate request data
        3. Create Shortlist object (holds data in memory)
        4. Save Shortlist object (Shortlist does the actual database work)
        5. Return response
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Step 1: Authenticate user
            if not self.authenticate_user():
                return (ResponseHelpers.error_response(
                    '; '.join(self.errors), 401
                ), 401)
            
            # Step 2: Validate request data
            if not self.validate_request_data():
                return (ResponseHelpers.error_response(
                    '; '.join(self.errors), 400
                ), 400)

            # Step 2b: Prevent duplicate acceptance if opportunity already taken
            request_id = self.request_data.get('request_id')
            try:
                request_id_int = int(request_id)
            except (TypeError, ValueError):
                return (ResponseHelpers.error_response('Invalid request ID', 400), 400)

            existing_assignment = Shortlist.active_assignment_for_request(request_id_int)
            if existing_assignment and existing_assignment.csr_user_id != self.user.id:
                return (
                    ResponseHelpers.error_response(
                        'This opportunity has already been accepted by another CSR representative.',
                        409
                    ),
                    409
                )
            
            # Step 3: Create Shortlist object (holds data in memory)
            self.create_shortlist_object()
            self.shortlist.request_id = request_id_int
            
            # Step 4: Save Shortlist object (Shortlist.save() does the actual work)
            try:
                self.shortlist.save()  # Instance method - does actual database work
            except ValueError as e:
                return (ResponseHelpers.error_response(str(e), 400), 400)
            
            # Step 5: Return success response
            return (ResponseHelpers.success_response(
                data=self.shortlist.to_dict(),
                message='Request added to shortlist successfully'
            ), 201)
            
        except Exception as e:
            print(f"[ERROR] Add to shortlist failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
