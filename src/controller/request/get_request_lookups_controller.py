"""
Get Request Lookups Controller
Handles retrieving request categories and service types

BOUNDARY Layer (BCE Architecture)
- No auth required (public lookup data)
- Calls ENTITY layer (Request)
- Returns formatted HTTP responses
"""

from flask import Blueprint
from src.entity.request import Request
from src.utils.helpers import ResponseHelpers

get_request_lookups_blueprint = Blueprint(
    'get_request_lookups',
    __name__,
    url_prefix='/api/requests'
)


class GetRequestLookupsController:
    """
    Provides lookup data for request creation forms
    """
    
    @staticmethod
    @get_request_lookups_blueprint.route('/categories', methods=['GET'])
    def get_categories():
        """
        Get all available request categories
        
        Returns:
            {
                "success": true,
                "data": [
                    {
                        "id": 1,
                        "category_name": "Food",
                        "description": "Food and grocery assistance",
                        "icon": "utensils"
                    },
                    ...
                ],
                "message": "Categories retrieved successfully"
            }
        """
        try:
            # Call ENTITY layer
            categories = Request.get_request_categories()
            
            # Return response (BOUNDARY)
            return ResponseHelpers.success_response(
                data=categories,
                message='Categories retrieved successfully'
            )
            
        except Exception as e:
            print(f"[ERROR] Get categories failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error')
    
    @staticmethod
    @get_request_lookups_blueprint.route('/service-types', methods=['GET'])
    def get_service_types():
        """
        Get all available service types
        
        Returns:
            {
                "success": true,
                "data": [
                    {
                        "id": 1,
                        "service_name": "Delivery",
                        "description": "Delivery service",
                        "icon": "truck"
                    },
                    ...
                ],
                "message": "Service types retrieved successfully"
            }
        """
        try:
            # Call ENTITY layer
            service_types = Request.get_service_types()
            
            # Return response (BOUNDARY)
            return ResponseHelpers.success_response(
                data=service_types,
                message='Service types retrieved successfully'
            )
            
        except Exception as e:
            print(f"[ERROR] Get service types failed: {str(e)}")
            return ResponseHelpers.error_response('Internal server error')
