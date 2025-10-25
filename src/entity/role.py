from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase

class Role:
    # Role Constants
    USER_ADMIN = "User Admin"
    PIN = "PIN"
    CSR_REP = "CSR Rep"
    PLATFORM_MANAGEMENT = "Platform Management"

    # Role Dashboard Routes
    ROLE_ROUTES = {
        USER_ADMIN: "/admin/dashboard",
        PIN: "/pin/dashboard",
        CSR_REP: "/csr/dashboard",
        PLATFORM_MANAGEMENT: "/platform/dashboard"
    }

    @staticmethod
    def create_role(role_name: str, role_code: str, description: str, dashboard_route: str = "/") -> Optional[Dict]:
        """Create a new role"""
        supabase = get_supabase()
        
        try:
            # Get dashboard route based on role name if not provided
            if dashboard_route == "/":
                dashboard_route = Role.ROLE_ROUTES.get(role_name, "/dashboard")
            
            role_data = {
                "role_name": role_name,
                "role_code": role_code,
                "description": description,
                "dashboard_route": dashboard_route,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Check if role exists
            existing = supabase.table('roles').select("*").eq('role_name', role_name).execute()
            if existing.data:
                return None  # Role already exists
            
            result = supabase.table('roles').insert(role_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating role: {str(e)}")
            return None

    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[Dict]:
        """Get role by ID"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('roles').select("*").eq('id', role_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting role: {str(e)}")
            return None

    @staticmethod
    def get_all_roles() -> List[Dict]:
        """Get all roles"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('roles').select("*").execute()
            return result.data
        except Exception as e:
            print(f"Error getting roles: {str(e)}")
            return []

    @staticmethod
    def get_role_by_name(role_name: str) -> Optional[Dict]:
        """Get role by name"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('roles').select("*").eq('role_name', role_name).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting role: {str(e)}")
            return None

    @staticmethod
    def update_role(role_id: int, role_name: str, role_code: str, description: str, dashboard_route: str = "/") -> Optional[Dict]:
        """Update an existing role"""
        supabase = get_supabase()
        
        try:
            role_data = {
                "role_name": role_name,
                "role_code": role_code,
                "description": description,
                "dashboard_route": dashboard_route
            }
            
            result = supabase.table('roles').update(role_data).eq('id', role_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating role: {str(e)}")
            return None

    @staticmethod
    def delete_role(role_id: int) -> bool:
        """Delete a role (cascading delete handled by database constraints)"""
        supabase = get_supabase()
        
        try:
            result = supabase.table('roles').delete().eq('id', role_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting role: {str(e)}")
            return False