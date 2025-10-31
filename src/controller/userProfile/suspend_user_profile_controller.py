"""Suspend User Profile Controller - Business logic for deleting roles"""

from src.entity import Role


class SuspendUserProfileController:
    @staticmethod
    def delete_user_profile(profile_id):
        profile = Role.get_role_by_id(profile_id)
        if not profile:
            return {
                'success': False,
                'message': 'User profile not found'
            }, 404

        success = Role.delete_role(profile_id)
        if success:
            return {
                'success': True,
                'message': 'User profile deleted successfully (cascading delete applied)'
            }, 200

        return {
            'success': False,
            'message': 'Failed to delete user profile'
        }, 400
