from src.entity import Role

class CreateRoleController:
    """Controller for creating a new role"""
    
    @staticmethod
    def create_role(data):
        """Create a new role"""
        try:
            # Validate required fields
            if not data.get('role_name') or not data.get('role_code') or not data.get('description'):
                return ({
                    'success': False,
                    'message': 'Missing required fields: role_name, role_code, description'
                }, 400)
            
            new_role = Role.create_role(
                role_name=data['role_name'],
                role_code=data['role_code'],
                description=data['description'],
                dashboard_route=data.get('dashboard_route', '/')
            )
            
            if not new_role:
                return ({
                    'success': False,
                    'message': 'Role already exists or failed to create'
                }, 400)
            
            return ({
                'success': True,
                'data': new_role,
                'message': 'Role created successfully'
            }, 201)
        except Exception as e:
            return ({
                'success': False,
                'message': str(e)
            }, 500)
