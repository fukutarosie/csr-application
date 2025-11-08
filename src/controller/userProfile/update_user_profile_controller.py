"""Update User Profile Controller - Business logic for updating roles"""

from src.entity import Role


class UpdateUserProfileController:
    @staticmethod
    def update_user_profile(profile_id, payload):
        if payload is None:
            return {
                'success': False,
                'message': 'Request payload is required'
            }, 400

        result = Role.update_role(
            role_id=profile_id,
            role_name=payload.get('role_name'),
            role_code=payload.get('role_code'),
            description=payload.get('description'),
            dashboard_route=payload.get('dashboard_route')
        )

        if result:
            return {
                'success': True,
                'data': result,
                'message': 'User profile updated successfully'
            }, 200

        return {
            'success': False,
            'message': 'Failed to update user profile'
        }, 400
