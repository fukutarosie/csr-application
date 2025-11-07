"""Suspend User Account Controller - Business logic for user suspend/activate/delete"""

from src.entity import User, Role


class SuspendUserAccountController:
    @staticmethod
    def suspend(user_id):
        """Suspend (deactivate) a user account"""
        try:
            result = User.update_user(user_id, {'is_active': False})

            if result:
                return {
                    'success': True,
                    'data': result,
                    'message': 'User account suspended successfully'
                }, 200
            else:
                return {
                    'success': False,
                    'message': 'Failed to suspend user account'
                }, 400

        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500

    @staticmethod
    def activate(user_id):
        """Activate a suspended user account"""
        try:
            result = User.update_user(user_id, {'is_active': True})

            if result:
                return {
                    'success': True,
                    'data': result,
                    'message': 'User account activated successfully'
                }, 200
            else:
                return {
                    'success': False,
                    'message': 'Failed to activate user account'
                }, 400

        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500

    @staticmethod
    def delete(user_id):
        """Delete a user account"""
        try:
            # Check if user exists
            user = User.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User account not found'
                }, 404
            
            # Call Entity layer to handle database deletion
            success = User.delete_user(user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'User account deleted successfully'
                }, 200
            else:
                return {
                    'success': False,
                    'message': 'Deletion failed'
                }, 500
                
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500

