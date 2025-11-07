"""
Get Request Lookups Controller (Control Layer)
Handles retrieving request categories and service types
"""

from src.entity.request import Request
from src.utils.helpers import ResponseHelpers

class GetRequestLookupsController:
    """
    Provides lookup data for request creation forms
    """
    
    @staticmethod
    def get_categories():
        """
        Get all available request categories
        
        Returns: (response_dict, status_code)
        """
        try:
            # Call ENTITY layer
            categories = Request.get_request_categories()
            
            # Return response
            return (ResponseHelpers.success_response(
                data=categories,
                message='Categories retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get categories failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
    
    @staticmethod
    def get_service_types():
        """
        Get all available service types
        
        Returns: (response_dict, status_code)
        """
        try:
            # Call ENTITY layer
            service_types = Request.get_service_types()
            
            # Return response
            return (ResponseHelpers.success_response(
                data=service_types,
                message='Service types retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get service types failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
