"""
Request Entity Class - PIN /CSR System
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
    
    @staticmethod
    def create_request(
        pin_user_id: int,
        title: str,
        description: str,
        service_type: str,
        region: str,
        requested_by_date: str,
        image_url: str
    ) -> Optional[Dict]:
        """
        Create a new request
        
        Args:
            pin_user_id: User ID of the PIN user (must have PIN role)
            title: Request title (required, min 5 characters)
            description: Request description (required, min 10 characters)
            service_type: Service type (required, must exist in service_types)
            region: Region where help needed (required, e.g., Hougang, Sengkang)
            requested_by_date: Date help is needed (required)
            image_url: URL path to uploaded image (required)
            
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
            if not title or not description or not service_type or not region or not requested_by_date or not image_url:
                return None
            
            # Validate service_type (now required)
            svc_check = supabase.table('service_types').select('id').eq('service_name', service_type).execute()
            if not svc_check.data:
                return None  # Invalid service type
            
            # Prepare data
            request_data = {
                'pin_user_id': pin_user_id,
                'title': title,
                'description': description,
                'service_type': service_type,
                'region': region,
                'requested_by_date': requested_by_date,
                'image_url': image_url,
                'status': Request.STATUS_ACTIVE,
                'is_archived': False,
                'view_count': 0,
                'shortlist_count': 0,
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
    def get_all_requests(status: str = None) -> List[Dict]:
        """
        Get all requests in the system (for CSR Rep and Platform Manager)
        
        Args:
            status: Optional filter by status (ACTIVE, SUSPENDED, etc.)
            
        Returns:
            List of requests
        """
        supabase = get_supabase()
        
        try:
            query = supabase.table('requests').select(
                "*",
                "users(id, username, full_name)"
            )
            
            if status:
                query = query.eq('status', status)
            
            result = query.order('created_at', desc=True).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting all requests: {str(e)}")
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
            
            # Validate service_type if being updated
            if 'service_type' in updates and updates['service_type']:
                svc_check = supabase.table('service_types').select('id').eq('service_name', updates['service_type']).execute()
                if not svc_check.data:
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
            # Verify ownership and current status
            current = supabase.table('requests').select('pin_user_id, status').eq('id', request_id).execute()
            if not current.data:
                print(f"Request {request_id} not found")
                return None
            
            if current.data[0]['pin_user_id'] != pin_user_id:
                print(f"Request {request_id} not owned by user {pin_user_id}")
                return None  # Not the owner
            
            if current.data[0]['status'] != Request.STATUS_ACTIVE:
                print(f"Request {request_id} is not ACTIVE (status: {current.data[0]['status']})")
                return None  # Can only suspend ACTIVE requests
            
            # Update status to SUSPENDED
            result = supabase.table('requests').update({
                'status': Request.STATUS_SUSPENDED,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', request_id).execute()
            
            # Record in audit trail if available
            if result.data:
                try:
                    Request._record_status_change(
                        request_id=request_id,
                        old_status=current.data[0]['status'],
                        new_status=Request.STATUS_SUSPENDED,
                        changed_by=pin_user_id,
                        reason=reason
                    )
                except Exception as audit_error:
                    print(f"Audit trail failed (non-critical): {str(audit_error)}")
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error suspending request: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
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
    
    # ===== ANALYTICS METHODS (US-27, US-28) =====
    
    @staticmethod
    def get_request_analytics(request_id: int) -> Optional[Dict]:
        """
        Get analytics for a specific request (view count, shortlist count).
        Supports US-27 and US-28.
        
        Args:
            request_id: Request ID
        
        Returns:
            {
                'request_id': int,
                'view_count': int,
                'shortlist_count': int,
                'title': str
            } or None if not found
        """
        supabase = get_supabase()
        
        try:
            result = supabase.table('requests').select("id, title, view_count, shortlist_count").eq('id', request_id).execute()
            
            if result.data:
                request = result.data[0]
                return {
                    'request_id': request['id'],
                    'title': request['title'],
                    'view_count': request.get('view_count', 0),
                    'shortlist_count': request.get('shortlist_count', 0)
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting analytics for request {request_id}: {str(e)}")
            return None
    
    @staticmethod
    def increment_view_count(request_id: int) -> bool:
        """
        Increment view count when a CSR views the request.
        Called by CSR controller when viewing request details.
        
        Args:
            request_id: Request ID
        
        Returns:
            True on success, False on failure
        """
        supabase = get_supabase()
        
        try:
            # Get current view count
            request = Request.get_request(request_id)
            if not request:
                return False
            
            current_count = request.get('view_count', 0)
            
            # Increment by 1
            result = supabase.table('requests').update({
                'view_count': current_count + 1,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', request_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"Error incrementing view count for request {request_id}: {str(e)}")
            return False
    
    @staticmethod
    def increment_shortlist_count(request_id: int) -> bool:
        """
        Increment shortlist count when a CSR adds request to shortlist.
        Called by Shortlist entity when adding to shortlist.
        
        Args:
            request_id: Request ID
        
        Returns:
            True on success, False on failure
        """
        supabase = get_supabase()
        
        try:
            # Get current shortlist count
            request = Request.get_request(request_id)
            if not request:
                return False
            
            current_count = request.get('shortlist_count', 0)
            
            # Increment by 1
            result = supabase.table('requests').update({
                'shortlist_count': current_count + 1,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', request_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"Error incrementing shortlist count for request {request_id}: {str(e)}")
            return False
    
    @staticmethod
    def decrement_shortlist_count(request_id: int) -> bool:
        """
        Decrement shortlist count when a CSR removes request from shortlist.
        Called by Shortlist entity when removing from shortlist.
        
        Args:
            request_id: Request ID
        
        Returns:
            True on success, False on failure
        """
        supabase = get_supabase()
        
        try:
            # Get current shortlist count
            request = Request.get_request(request_id)
            if not request:
                return False
            
            current_count = request.get('shortlist_count', 0)
            
            # Decrement by 1 (but don't go below 0)
            new_count = max(0, current_count - 1)
            
            result = supabase.table('requests').update({
                'shortlist_count': new_count,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', request_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"Error decrementing shortlist count for request {request_id}: {str(e)}")
            return False
    
    # ===== COMPLETED MATCHES (US-29, US-30) =====
    
    @staticmethod
    def get_completed_matches(user_id: int, filters: Dict = None, page: int = 1, limit: int = 10) -> Dict:
        """
        Get completed matches for a PIN user (requests that have been fulfilled).
        Supports US-29 and US-30.
        
        Args:
            user_id: PIN user ID
            filters: Optional filters:
                - start_date: Filter by fulfilled_at >= start_date
                - end_date: Filter by fulfilled_at <= end_date
            page: Page number (1-indexed)
            limit: Results per page
        
        Returns:
            {
                'data': [requests with shortlist details],
                'pagination': {
                    'page': int,
                    'limit': int,
                    'total': int,
                    'total_pages': int
                }
            }
        """
        supabase = get_supabase()
        
        try:
            # Build query for FULFILLED requests
            query = supabase.table('requests').select("*", count='exact').eq('pin_user_id', user_id).eq('status', 'FULFILLED')
            
            # Apply date filters
            if filters:
                if filters.get('start_date'):
                    query = query.gte('fulfilled_at', filters['start_date'])
                if filters.get('end_date'):
                    query = query.lte('fulfilled_at', filters['end_date'])
            
            # Get total count
            count_result = query.execute()
            total = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.order('fulfilled_at', desc=True).range(offset, offset + limit - 1)
            
            # Execute query
            result = query.execute()
            
            # For each completed request, get the associated shortlist entry (CSR who helped)
            completed_requests = []
            for request in result.data:
                # Get shortlist entries for this request (status = COMPLETED)
                shortlist_result = supabase.table('shortlist').select("*").eq('request_id', request['id']).eq('status', 'COMPLETED').execute()
                
                request['matched_csr'] = shortlist_result.data if shortlist_result.data else []
                completed_requests.append(request)
            
            return {
                'data': completed_requests,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            print(f"Error getting completed matches for user {user_id}: {str(e)}")
            return {'data': [], 'pagination': {'page': page, 'limit': limit, 'total': 0, 'total_pages': 0}}
    
    # ===== LOOKUP TABLES =====
    
    @staticmethod
    def get_request_categories() -> List[Dict]:
        """
        Get all available request categories.
        
        Returns:
            List of category dicts
        """
        supabase = get_supabase()
        
        try:
            result = supabase.table('request_categories').select("*").order('category_name').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting request categories: {str(e)}")
            return []
    
    @staticmethod
    def get_service_types() -> List[Dict]:
        """
        Get all available service types.
        
        Returns:
            List of service type dicts
        """
        supabase = get_supabase()
        
        try:
            result = supabase.table('service_types').select("*").order('service_name').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting service types: {str(e)}")
            return []