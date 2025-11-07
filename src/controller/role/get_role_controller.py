from src.entity import Role

class GetRoleController:
    """Controller for fetching a specific role by ID"""
    
    @staticmethod
    def get_role(role_id):
        """Get specific role by ID"""
        try:
            role = Role.get_role_by_id(role_id)
            if not role:
                return ({
                    'success': False,
                    'message': 'Role not found'
                }, 404)
            
            return ({
                'success': True,
                'data': role
            }, 200)
        except Exception as e:
            return ({
                'success': False,
                'message': str(e)
            }, 500)
