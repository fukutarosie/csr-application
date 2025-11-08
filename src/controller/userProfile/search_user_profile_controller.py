"""Search User Profile Controller - Business logic for searching roles"""

from src.entity import Role


class SearchUserProfileController:
    @staticmethod
    def search_user_profiles(payload):
        if payload is None:
            payload = {}

        search_term = payload.get('search', '')

        all_roles = Role.get_all_roles() or []
        filtered_roles = [
            role for role in all_roles
            if search_term.lower() in (role.get('role_name', '')).lower()
            or search_term.lower() in (role.get('role_code', '')).lower()
        ]

        return {
            'success': True,
            'data': filtered_roles,
            'count': len(filtered_roles)
        }, 200
