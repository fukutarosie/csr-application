"""
Get Request Lookups Controller - TRUE OOP Implementation
"""

from typing import Dict, Tuple
from src.entity.request import Request
from src.utils.helpers import ResponseHelpers


class GetRequestCategoriesController:
    """
    Get Request Categories Controller - TRUE OOP
    
    Usage:
        controller = GetRequestCategoriesController()
        response, status = controller.execute()
    """
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute categories retrieval"""
        try:
            # Get categories from Request entity
            categories = Request.get_categories()
            
            return (ResponseHelpers.success_response(
                data=categories,
                message='Categories retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get categories failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)


class GetRequestServiceTypesController:
    """
    Get Request Service Types Controller - TRUE OOP
    
    Usage:
        controller = GetRequestServiceTypesController()
        response, status = controller.execute()
    """
    
    def execute(self) -> Tuple[Dict, int]:
        """Execute service types retrieval"""
        try:
            # Get service types from Request entity
            service_types = Request.get_service_types()
            
            return (ResponseHelpers.success_response(
                data=service_types,
                message='Service types retrieved successfully'
            ), 200)
            
        except Exception as e:
            print(f"[ERROR] Get service types failed: {str(e)}")
            return (ResponseHelpers.error_response('Internal server error'), 500)
