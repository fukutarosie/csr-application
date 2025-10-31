"""View User Profile Controller - Business logic for retrieving roles"""

from src.entity import Role


class ViewUserProfileController:
    @staticmethod
    def get_all_user_profiles():
        profiles = Role.get_all_roles() or []
        return {
            'success': True,
            'data': profiles,
            'count': len(profiles)
        }, 200

    @staticmethod
    def get_user_profile_by_id(profile_id):
        profile = Role.get_role_by_id(profile_id)
        if not profile:
            return {
                'success': False,
                'message': 'User profile not found'
            }, 404

        return {
            'success': True,
            'data': profile
        }, 200
