"""GetRequestLookups Boundary - HTTP layer for request lookup data"""

from flask import Blueprint, jsonify
from src.controller.request.get_request_lookups_controller import GetRequestLookupsController

get_request_lookups_boundary = Blueprint(
    'get_request_lookups',
    __name__,
    url_prefix='/api/requests'
)

@get_request_lookups_boundary.route('/categories', methods=['GET'])
def get_categories():
    """Get all available request categories"""
    response, status = GetRequestLookupsController.get_categories()
    return jsonify(response), status

@get_request_lookups_boundary.route('/service-types', methods=['GET'])
def get_service_types():
    """Get all available service types"""
    response, status = GetRequestLookupsController.get_service_types()
    return jsonify(response), status
