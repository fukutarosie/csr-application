"""Suspend User Account Controller - Handles user suspend/activate logic"""

from flask import Blueprint, request, jsonify
from src.entity import User, Role
from src.controller.auth.auth_middleware import require_role

suspend_user_account_blueprint = Blueprint('suspend_user_account', __name__, url_prefix='/api/userAccount')

class SuspendUserAccountController:
    @staticmethod
    @suspend_user_account_blueprint.route('/<int:user_id>/suspend', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def suspend(user_id):
        """Suspend (deactivate) a user account"""
        try:
            result = User.update_user(user_id, {'is_active': False})

            if result:
                return jsonify({
                    'success': True,
                    'data': result,
                    'message': 'User account suspended successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to suspend user account'
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @staticmethod
    @suspend_user_account_blueprint.route('/<int:user_id>/activate', methods=['PUT'])
    @require_role(Role.USER_ADMIN)
    def activate(user_id):
        """Activate a suspended user account"""
        try:
            result = User.update_user(user_id, {'is_active': True})

            if result:
                return jsonify({
                    'success': True,
                    'data': result,
                    'message': 'User account activated successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to activate user account'
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @suspend_user_account_blueprint.route('/<int:user_id>/delete', methods=['DELETE'])
    @require_role(Role.USER_ADMIN)
    def delete(user_id):
        """Delete a user account"""
        try:
            from src.config.supabase import supabase
            
            # Check if user exists
            user = User.get_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User account not found'
                }), 404
            
            # Delete from database
            supabase.table('users').delete().eq('id', user_id).execute()
            
            return jsonify({
                'success': True,
                'message': 'User account deleted successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
