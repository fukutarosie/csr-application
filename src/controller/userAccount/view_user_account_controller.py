"""View User Account Controller - Business logic for user retrieval"""

from src.entity import User, Role


class ViewUserAccountController:
    @staticmethod
    def view_all():
        """Get all user accounts"""
        try:
            users = User.get_all_users()
            return {
                'success': True,
                'data': users,
                'count': len(users) if users else 0
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500

    @staticmethod
    def view_one(user_id):
        """Get specific user account by ID"""
        try:
            user = User.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User account not found'
                }, 404
            
            return {
                'success': True,
                'data': user
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500

