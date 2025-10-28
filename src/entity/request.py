"""
Request Entity Class - PIN/CSR System
Handles all database operations for PIN requests
Part of the CONTROL/ENTITY layer (BCE Architecture)

Methods:
- create_request() - Create new request
- get_request() - Retrieve single request
- get_requests_by_pin_user() - Get all requests from a PIN user
- update_request() - Update request details
- suspend_request() - Suspend a request
- search_requests() - Search with filters
- fulfill_request() - Mark as fulfilled
- delete_request() - Hard delete (admin only)
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase


class Request:
    """Request entity - handles PIN user requests"""
    
    # Request statuses
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_FULFILLED = 'FULFILLED'
    STATUS_CANCELLED = 'CANCELLED'
    
    VALID_STATUSES = [STATUS_ACTIVE, STATUS_SUSPENDED, STATUS_FULFILLED, STATUS_CANCELLED]
    
    # Priority levels
    PRIORITY_LOW = 'LOW'
    PRIORITY_MEDIUM = 'MEDIUM'
    PRIORITY_HIGH = 'HIGH'
    PRIORITY_URGENT = 'URGENT'
    
    VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_URGENT]
    
    @staticmethod
    def create_request(
        pin_user_id: int,
        title: str,
        description: str,
        category: str,
        service_type: str = None,
        priority: str = PRIORITY_MEDIUM,
        location_city: str = None,
        location_detail: str = None,
        requested_by_date: str = None
    ) -> Optional[Dict]:
        """
        Create a new request
        
        Args:
            pin_user_id: User ID of the PIN user (must have PIN role)
            title: Request title (required)
            description: Request description (required)
            category: Category (must exist in request_categories)
            service_type: Service type (optional, must exist in service_types)
            priority: Priority level (LOW, MEDIUM, HIGH, URGENT)
            location_city: City where help needed
            location_detail: Detailed location
            requested_by_date: Date help is needed
            
        Returns:
            Created request dict with id, or None if failed
        """
        supabase = get_supabase()
        
        try:
            # Validate user exists and is PIN role
            user = supabase.table('users').select('id, role_id').eq('id', pin_user_id).execute()
            if not user.data:
                return None  # User not found
            
            if user.data[0]['role_id'] != 2:  # PIN role_id = 2
                return None  # User is not PIN role
            
            # Validate required fields
            if not title or not description:
                return None
            
            # Validate category exists
            if category:
                cat_check = supabase.table('request_categories').select('id').eq('category_name', category).execute()
                if not cat_check.data:
                    return None  # Invalid category
            
            # Validate service_type if provided
            if service_type:
                svc_check = supabase.table('service_types').select('id').eq('service_name', service_type).execute()
                if not svc_check.data:
                    return None  # Invalid service type
            
            # Validate priority
            if priority not in Request.VALID_PRIORITIES:
                priority = Request.PRIORITY_MEDIUM
            
            # Prepare data
            request_data = {
                'pin_user_id': pin_user_id,
                'title': title,
                'description': description,
                'category': category,
                'service_type': service_type,
                'priority': priority,
                'location_city': location_city,
                'location_detail': location_detail,
                'requested_by_date': requested_by_date,
                'status': Request.STATUS_ACTIVE,
                'is_archived': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Insert
            result = supabase.table('requests').insert(request_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating request: {str(e)}")
            return None
    
    @staticmethod
    def get_request(request_id: int) -> Optional[Dict]:
        """
        Get a single request by ID
        
        Args:
            request_id: Request ID
            
        Returns:
            Request dict with all fields, or None if not found
        """
        supabase = get_supabase()
        
        try:
            result = supabase.table('requests').select(
                "*",
                "users(id, username, full_name, email)"
            ).eq('id', request_id).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error getting request: {str(e)}")
            return None
    
    @staticmethod
    def get_requests_by_pin_user(pin_user_id: int, status: str = None) -> List[Dict]:
        """
        Get all requests created by a PIN user
        
        Args:
            pin_user_id: PIN user ID
            status: Optional filter by status (ACTIVE, SUSPENDED, etc.)
            
        Returns:
            List of requests
        """
        supabase = get_supabase()
        
        try:
            query = supabase.table('requests').select(
                "*",
                "users(id, username, full_name)"
            ).eq('pin_user_id', pin_user_id)
            
            if status:
                query = query.eq('status', status)
            
            result = query.order('created_at', desc=True).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting requests by PIN user: {str(e)}")
            return []
    
    @staticmethod
    def update_request(
        request_id: int,
        pin_user_id: int,
        updates: Dict
    ) -> Optional[Dict]:
        """
        Update a request (only by the owner)
        
        Args:
            request_id: Request ID
            pin_user_id: PIN user ID (must be the owner)
            updates: Dict with fields to update
            
        Returns:
            Updated request dict, or None if failed
        """
        supabase = get_supabase()
        
        try:
            # Verify ownership and request is ACTIVE
            current = supabase.table('requests').select('pin_user_id, status').eq('id', request_id).execute()
            if not current.data:
                return None  # Request not found
            
            req = current.data[0]
            if req['pin_user_id'] != pin_user_id:
                return None  # Not the owner
            
            if req['status'] != Request.STATUS_ACTIVE:
                return None  # Can only edit ACTIVE requests
            
            # Validate category if being updated
            if 'category' in updates and updates['category']:
                cat_check = supabase.table('request_categories').select('id').eq('category_name', updates['category']).execute()
                if not cat_check.data:
                    return None
            
            # Validate service_type if being updated
            if 'service_type' in updates and updates['service_type']:
                svc_check = supabase.table('service_types').select('id').eq('service_name', updates['service_type']).execute()
                if not svc_check.data:
                    return None
            
            # Validate priority if being updated
            if 'priority' in updates and updates['priority'] not in Request.VALID_PRIORITIES:
                return None
            
            # Add updated_at timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update
            result = supabase.table('requests').update(updates).eq('id', request_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error updating request: {str(e)}")
            return None
    
    @staticmethod
    def suspend_request(request_id: int, pin_user_id: int, reason: str = None) -> Optional[Dict]:
        """
        Suspend a request (mark as no longer needed)
        
        Args:
            request_id: Request ID
            pin_user_id: PIN user ID (must be the owner)
            reason: Reason for suspension
            
        Returns:
            Updated request dict, or None if failed
        """
        supabase = get_supabase()
        
        try:
            # Verify ownership
            current = supabase.table('requests').select('pin_user_id, status').eq('id', request_id).execute()
            if not current.data:
                return None
            
            if current.data[0]['pin_user_id'] != pin_user_id:
                return None  # Not the owner
            
            # Update status to SUSPENDED
            result = supabase.table('requests').update({
                'status': Request.STATUS_SUSPENDED,
                'suspended_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', request_id).execute()
            
            # Record in audit trail
            if result.data:
                Request._record_status_change(
                    request_id=request_id,
                    old_status=current.data[0]['status'],
                    new_status=Request.STATUS_SUSPENDED,
                    changed_by=pin_user_id,
                    reason=reason
                )
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error suspending request: {str(e)}")
            return None
    
    @staticmethod
    def fulfill_request(request_id: int) -> Optional[Dict]:
        """
        Mark request as fulfilled (admin/system only)
        
        Args:
            request_id: Request ID
            
        Returns:
            Updated request dict, or None if failed
        """
        supabase = get_supabase()
        
        try:
            current = supabase.table('requests').select('status').eq('id', request_id).execute()
            if not current.data:
                return None
            
            result = supabase.table('requests').update({
                'status': Request.STATUS_FULFILLED,
                'fulfilled_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', request_id).execute()
            
            # Record in audit trail
            if result.data:
                Request._record_status_change(
                    request_id=request_id,
                    old_status=current.data[0]['status'],
                    new_status=Request.STATUS_FULFILLED,
                    changed_by=None,
                    reason='Marked as fulfilled'
                )
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error fulfilling request: {str(e)}")
            return None
    
    @staticmethod
    def search_requests(
        keyword: str = None,
        category: str = None,
        status: str = None,
        priority: str = None,
        service_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Search requests with filters (for CSR to find opportunities)
        
        Args:
            keyword: Search in title/description
            category: Filter by category
            status: Filter by status (default: ACTIVE only)
            priority: Filter by priority
            service_type: Filter by service type
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of matching requests
        """
        supabase = get_supabase()
        
        try:
            # Start with ACTIVE requests by default (for CSR to see opportunities)
            if status is None:
                status = Request.STATUS_ACTIVE
            
            query = supabase.table('requests').select(
                "*",
                "users(id, username, full_name)"
            ).eq('status', status)
            
            # Apply filters
            if category:
                query = query.eq('category', category)
            if priority:
                query = query.eq('priority', priority)
            if service_type:
                query = query.eq('service_type', service_type)
            
            result = query.order('priority', desc=True).order('created_at', desc=True).range(offset, offset + limit).execute()
            
            # If keyword search, filter results in memory (Supabase full-text search alternative)
            if keyword:
                keyword_lower = keyword.lower()
                result.data = [
                    req for req in (result.data or [])
                    if keyword_lower in req['title'].lower() or keyword_lower in req['description'].lower()
                ]
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error searching requests: {str(e)}")
            return []
    
    @staticmethod
    def get_active_requests_count() -> int:
        """Get count of ACTIVE requests"""
        supabase = get_supabase()
        try:
            result = supabase.table('requests').select('id', count='exact').eq('status', Request.STATUS_ACTIVE).execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception as e:
            print(f"Error counting active requests: {str(e)}")
            return 0
    
    @staticmethod
    def get_request_by_pin_user_count(pin_user_id: int) -> int:
        """Get count of requests created by a PIN user"""
        supabase = get_supabase()
        try:
            result = supabase.table('requests').select('id', count='exact').eq('pin_user_id', pin_user_id).execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception as e:
            print(f"Error counting user requests: {str(e)}")
            return 0
    
    @staticmethod
    def delete_request(request_id: int) -> bool:
        """
        Delete a request (admin only)
        
        Args:
            request_id: Request ID
            
        Returns:
            True if deleted, False if failed
        """
        supabase = get_supabase()
        
        try:
            supabase.table('requests').delete().eq('id', request_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting request: {str(e)}")
            return False
    
    @staticmethod
    def _record_status_change(
        request_id: int,
        old_status: str,
        new_status: str,
        changed_by: int = None,
        reason: str = None
    ) -> bool:
        """
        Record status change in audit trail
        
        Args:
            request_id: Request ID
            old_status: Previous status
            new_status: New status
            changed_by: User ID who made the change
            reason: Reason for change
            
        Returns:
            True if recorded, False if failed
        """
        supabase = get_supabase()
        
        try:
            supabase.table('request_status_history').insert({
                'request_id': request_id,
                'old_status': old_status,
                'new_status': new_status,
                'changed_by': changed_by,
                'reason': reason,
                'changed_at': datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Error recording status change: {str(e)}")
            return False