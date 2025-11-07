from src.entity import Role

class GetPublicRolesController:
    """Controller for fetching roles without authentication (for login page)"""
    
    @staticmethod
    def get_public_roles():
        """Get all roles - Public endpoint for login page (no authentication required)"""
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
