from src.entity import Role

class GetAllRolesController:
    """Controller for fetching all roles (admin only)"""
    
    @staticmethod
    def get_all_roles():
        """Get all roles - Protected endpoint for admins"""
        try:
            roles = Role.get_all_roles()
            return ({
                'success': True,
                'data': roles
            }, 200)
        except Exception as e:
            return ({
                'success': False,
                'message': str(e)
            }, 500)
