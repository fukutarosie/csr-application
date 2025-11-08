"""GetRequestLookups Boundary - HTTP layer for request lookup data"""

from flask import Blueprint, jsonify
from src.controller.request.get_request_lookups_controller import GetRequestCategoriesController, GetRequestServiceTypesController

get_request_lookups_boundary = Blueprint(
    'get_request_lookups',
    __name__,
    url_prefix='/api/requests'
)

@get_request_lookups_boundary.route('/categories', methods=['GET'])
def get_categories():
    """Get all available request categories"""
    controller = GetRequestCategoriesController()
    response, status = controller.execute()
    return jsonify(response), status

@get_request_lookups_boundary.route('/service-types', methods=['GET'])
def get_service_types():
    """Get all available service types"""
    controller = GetRequestServiceTypesController()
    response, status = controller.execute()
    return jsonify(response), status
