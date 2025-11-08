from src.entity import Role

class DeleteRoleController:
    """Controller for deleting a role (CASCADE delete associated users)"""
    
    @staticmethod
    def delete_role(role_id):
        """Delete a role and cascade delete associated users"""
        try:
            # Check if role exists
            role = Role.get_role_by_id(role_id)
            if not role:
                return ({
                    'success': False,
                    'message': 'Role not found'
                }, 404)
            
            # Delete the role (cascading delete handled by database constraints)
            success = Role.delete_role(role_id)
            
            if success:
                return ({
                    'success': True,
                    'message': 'Role deleted successfully'
                }, 200)
            else:
                return ({
                    'success': False,
                    'message': 'Failed to delete role'
                }, 500)
        except Exception as e:
            return ({
                'success': False,
                'message': str(e)
            }, 500)
