from datetime import datetime
from typing import Dict, List, Tuple
from ..config.supabase import get_supabase

class Request:
    @staticmethod
    def create_request(title: str, description: str, priority: str,
                      requester_email: str) -> Tuple[bool, int]:
        """Create a new service request"""
        supabase = get_supabase()
        
        try:
            request_data = {
                "title": title,
                "description": description,
                "status": "Open",
                "priority": priority,
                "requester_email": requester_email,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table('requests').insert(request_data).execute()
            return True, 201
            
        except Exception as e:
            print(f"Error creating request: {str(e)}")
            return False, 500

    @staticmethod
    def get_user_requests(email: str) -> List[Dict]:
        """Get all requests created by a user"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('requests').select("*").eq('requester_email', email).execute()
            return result.data
        except Exception as e:
            print(f"Error getting user requests: {str(e)}")
            return []

    @staticmethod
    def get_assigned_requests(email: str) -> List[Dict]:
        """Get all requests assigned to a user"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('requests').select("*").eq('assignee_email', email).execute()
            return result.data
        except Exception as e:
            print(f"Error getting assigned requests: {str(e)}")
            return []

    @staticmethod
    def assign_request(request_id: int, assignee_email: str) -> Tuple[bool, int]:
        """Assign request to a staff member"""
        supabase = get_supabase()
        
        try:
            update_data = {
                "assignee_email": assignee_email,
                "status": "In Progress",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table('requests').update(update_data).eq('id', request_id).execute()
            return True, 200
        except Exception as e:
            print(f"Error assigning request: {str(e)}")
            return False, 500

    @staticmethod
    def update_status(request_id: int, status: str) -> Tuple[bool, int]:
        """Update request status"""
        valid_statuses = ["Open", "In Progress", "Closed"]
        if status not in valid_statuses:
            return False, 400
            
        supabase = get_supabase()
        
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table('requests').update(update_data).eq('id', request_id).execute()
            return True, 200
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            return False, 500