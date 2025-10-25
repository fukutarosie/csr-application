from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .supabase_config import get_supabase

class CSRRequest:
    @staticmethod
    def create_request(title: str, description: str, priority: str,
                      requester_id: int, category: str = None) -> Tuple[bool, int]:
        """Create a new CSR request"""
        supabase = get_supabase()
        
        try:
            request_data = {
                "title": title,
                "description": description,
                "status": "Open",
                "priority": priority,
                "requester_id": requester_id,
                "category": category,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table('csr_requests').insert(request_data).execute()
            return True, 201
            
        except Exception as e:
            print(f"Error creating request: {str(e)}")
            return False, 500

    @staticmethod
    def get_request_by_id(request_id: int) -> Optional[Dict]:
        """Get request by ID with user details"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('csr_requests').select(
                "*",
                "requester:users!requester_id(username, full_name)",
                "assignee:users!assignee_id(username, full_name)"
            ).eq('id', request_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting request: {str(e)}")
            return None

    @staticmethod
    def get_user_requests(user_id: int) -> List[Dict]:
        """Get all requests created by a user"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('csr_requests').select(
                "*",
                "assignee:users!assignee_id(username, full_name)"
            ).eq('requester_id', user_id).order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting user requests: {str(e)}")
            return []

    @staticmethod
    def get_assigned_requests(user_id: int) -> List[Dict]:
        """Get all requests assigned to a user"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('csr_requests').select(
                "*",
                "requester:users!requester_id(username, full_name)"
            ).eq('assignee_id', user_id).order('updated_at', desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting assigned requests: {str(e)}")
            return []

    @staticmethod
    def assign_request(request_id: int, assignee_id: int) -> Tuple[bool, int]:
        """Assign request to a staff member"""
        supabase = get_supabase()
        
        try:
            update_data = {
                "assignee_id": assignee_id,
                "status": "In Progress",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table('csr_requests').update(update_data).eq('id', request_id).execute()
            return True, 200
        except Exception as e:
            print(f"Error assigning request: {str(e)}")
            return False, 500

    @staticmethod
    def update_status(request_id: int, status: str, resolution_notes: str = None) -> Tuple[bool, int]:
        """Update request status"""
        valid_statuses = ["Open", "In Progress", "Resolved", "Closed", "Cancelled"]
        if status not in valid_statuses:
            return False, 400
            
        supabase = get_supabase()
        
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if resolution_notes:
                update_data["resolution_notes"] = resolution_notes
            
            result = supabase.table('csr_requests').update(update_data).eq('id', request_id).execute()
            return True, 200
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            return False, 500

    @staticmethod
    def get_requests_by_status(status: str) -> List[Dict]:
        """Get all requests with a specific status"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('csr_requests').select(
                "*",
                "requester:users!requester_id(username, full_name)",
                "assignee:users!assignee_id(username, full_name)"
            ).eq('status', status).order('updated_at', desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting requests by status: {str(e)}")
            return []