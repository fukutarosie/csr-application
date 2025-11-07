"""Search User Account Controller - Business logic for user search"""

from src.entity import User, Role


class SearchUserAccountController:
    @staticmethod
    def search(data):
        """Search user accounts by criteria"""
        try:
            if not data:
                data = {}
            
            users = User.search_users(
                username=data.get('username', ''),
                email=data.get('email', ''),
                full_name=data.get('full_name', '')
            )

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

