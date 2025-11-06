"""
Shortlist Entity Class - PIN/CSR System
Handles all database operations for CSR shortlisting of PIN requests
Part of the CONTROL/ENTITY layer (BCE Architecture)

Methods:
- add_to_shortlist() - Save/shortlist a request
- remove_from_shortlist() - Remove from shortlist
- search_shortlist() - Get CSR's shortlist with filters
- update_shortlist_status() - Update shortlist status
- get_shortlist_item() - Get specific shortlist entry
"""

from typing import Dict, List, Optional
from datetime import datetime
from .supabase_config import get_supabase


class Shortlist:
    """Shortlist entity - handles CSR shortlisting of requests"""
    
    # Shortlist statuses
    STATUS_SHORTLISTED = 'SHORTLISTED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_DECLINED = 'DECLINED'
    
    VALID_STATUSES = [STATUS_SHORTLISTED, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_DECLINED]
    
    @staticmethod
    def add_to_shortlist(
        csr_user_id: int,
        request_id: int,
        notes: str = None
    ) -> Optional[Dict]:
        """
        Add a request to CSR's shortlist (save/bookmark for later)
        
        Args:
            csr_user_id: CSR user ID (must have CSR role)
            request_id: Request ID to shortlist
            notes: Optional notes from CSR
            
        Returns:
            Created shortlist entry dict, or None if failed
        """
        supabase = get_supabase()
        
        try:
            # Validate CSR user exists and has CSR role
            user = supabase.table('users').select('id, role_id').eq('id', csr_user_id).execute()
            if not user.data:
                return None  # User not found
            
            if user.data[0]['role_id'] != 3:  # CSR role_id = 3
                return None  # User is not CSR role
            
            # Validate request exists and is ACTIVE
            request = supabase.table('requests').select('id, status').eq('id', request_id).execute()
            if not request.data:
                return None  # Request not found
            
            if request.data[0]['status'] != 'ACTIVE':
                return None  # Can only shortlist ACTIVE requests
            
            # Check if already shortlisted (UNIQUE constraint will prevent duplicate)
            existing = supabase.table('shortlist').select('id').eq('csr_user_id', csr_user_id).eq('request_id', request_id).execute()
            if existing.data:
                return None  # Already shortlisted
            
            # Prepare data
            shortlist_data = {
                'csr_user_id': csr_user_id,
                'request_id': request_id,
                'status': Shortlist.STATUS_SHORTLISTED,
                'notes': notes,
                'shortlisted_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Insert
            result = supabase.table('shortlist').insert(shortlist_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            # Handle unique constraint error gracefully
            if 'unique' in str(e).lower():
                print(f"Request already shortlisted by this CSR")
            else:
                print(f"Error adding to shortlist: {str(e)}")
            return None
    
    @staticmethod
    def remove_from_shortlist(
        shortlist_id: int,
        csr_user_id: int
    ) -> bool:
        """
        Remove a request from CSR's shortlist
        
        Args:
            shortlist_id: Shortlist entry ID
            csr_user_id: CSR user ID (must be the owner)
            
        Returns:
            True if removed, False if failed
        """
        supabase = get_supabase()
        
        try:
            # Verify ownership
            existing = supabase.table('shortlist').select('csr_user_id').eq('id', shortlist_id).execute()
            if not existing.data:
                return False  # Not found
            
            if existing.data[0]['csr_user_id'] != csr_user_id:
                return False  # Not the owner
            
            # Delete
            supabase.table('shortlist').delete().eq('id', shortlist_id).execute()
            return True
            
        except Exception as e:
            print(f"Error removing from shortlist: {str(e)}")
            return False
    
    @staticmethod
    def get_shortlist_item(shortlist_id: int) -> Optional[Dict]:
        """
        Get a specific shortlist entry
        
        Args:
            shortlist_id: Shortlist entry ID
            
        Returns:
            Shortlist entry dict with request details, or None if not found
        """
        supabase = get_supabase()
        
        try:
            result = supabase.table('shortlist').select(
                "*",
                "requests(id, title, description, category, service_type, priority, location_city, status)",
                "users(id, username, full_name, email)"
            ).eq('id', shortlist_id).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error getting shortlist item: {str(e)}")
            return None
    
    @staticmethod
    def search_shortlist(
        csr_user_id: int,
        status: str = None,
        service_type: str = None,
        date_from: str = None,
        date_to: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Search CSR's shortlist with filters
        
        Args:
            csr_user_id: CSR user ID
            status: Filter by shortlist status (SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED)
            service_type: Filter by service type
            date_from: Filter shortlisted after date (ISO format)
            date_to: Filter shortlisted before date (ISO format)
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of shortlist entries with request details
        """
        supabase = get_supabase()
        
        try:
            query = supabase.table('shortlist').select(
                "*",
                "requests(id, title, description, category, service_type, priority, location_city, status, pin_user_id)",
                "users(id, username, full_name, email)"
            ).eq('csr_user_id', csr_user_id)
            
            # Apply filters
            if status:
                query = query.eq('status', status)
            if service_type:
                query = query.eq('requests.service_type', service_type)
            if date_from:
                query = query.gte('shortlisted_at', date_from)
            if date_to:
                query = query.lte('shortlisted_at', date_to)
            
            result = query.order('shortlisted_at', desc=True).range(offset, offset + limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error searching shortlist: {str(e)}")
            return []
    
    @staticmethod
    def update_shortlist_status(
        shortlist_id: int,
        csr_user_id: int,
        new_status: str,
        notes: str = None,
        volunteered_hours: float = None
    ) -> Optional[Dict]:
        """
        Update shortlist entry status
        
        Args:
            shortlist_id: Shortlist entry ID
            csr_user_id: CSR user ID (must be the owner)
            new_status: New status (SHORTLISTED, IN_PROGRESS, COMPLETED, DECLINED)
            notes: Updated notes from CSR
            volunteered_hours: Hours spent (for COMPLETED status)
            
        Returns:
            Updated shortlist entry dict, or None if failed
        """
        supabase = get_supabase()
        
        try:
            # Verify ownership
            existing = supabase.table('shortlist').select('csr_user_id, status').eq('id', shortlist_id).execute()
            if not existing.data:
                return None  # Not found
            
            if existing.data[0]['csr_user_id'] != csr_user_id:
                return None  # Not the owner
            
            # Validate new status
            if new_status not in Shortlist.VALID_STATUSES:
                return None
            
            # Prepare updates
            updates = {
                'status': new_status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Add optional fields
            if notes is not None:
                updates['notes'] = notes
            
            if volunteered_hours is not None:
                updates['volunteered_hours'] = volunteered_hours
            
            # Set completion_date if marked as COMPLETED
            if new_status == Shortlist.STATUS_COMPLETED:
                updates['completion_date'] = datetime.utcnow().isoformat()
            
            # Update
            result = supabase.table('shortlist').update(updates).eq('id', shortlist_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error updating shortlist status: {str(e)}")
            return None
    
    @staticmethod
    def get_csr_shortlist_count(csr_user_id: int, status: str = None) -> int:
        """
        Get count of shortlist entries for a CSR
        
        Args:
            csr_user_id: CSR user ID
            status: Optional filter by status
            
        Returns:
            Count of shortlist entries
        """
        supabase = get_supabase()
        
        try:
            query = supabase.table('shortlist').select('id', count='exact').eq('csr_user_id', csr_user_id)
            
            if status:
                query = query.eq('status', status)
            
            result = query.execute()
            return result.count if hasattr(result, 'count') else 0
            
        except Exception as e:
            print(f"Error counting shortlist: {str(e)}")
            return 0
    
    @staticmethod
    def get_request_shortlist_count(request_id: int, status: str = None) -> int:
        """
        Get count of CSRs who shortlisted a request
        
        Args:
            request_id: Request ID
            status: Optional filter by status
            
        Returns:
            Count of shortlist entries
        """
        supabase = get_supabase()
        
        try:
            query = supabase.table('shortlist').select('id', count='exact').eq('request_id', request_id)
            
            if status:
                query = query.eq('status', status)
            
            result = query.execute()
            return result.count if hasattr(result, 'count') else 0
            
        except Exception as e:
            print(f"Error counting request shortlists: {str(e)}")
            return 0
    
    @staticmethod
    def add_feedback(
        shortlist_id: int,
        pin_user_id: int,
        feedback: str
    ) -> Optional[Dict]:
        """
        PIN user adds feedback about CSR's help
        
        Args:
            shortlist_id: Shortlist entry ID
            pin_user_id: PIN user ID (must be the request owner)
            feedback: Feedback text
            
        Returns:
            Updated shortlist entry dict, or None if failed
        """
        supabase = get_supabase()
        
        try:
            # Get shortlist entry with request info
            entry = supabase.table('shortlist').select('request_id, requests(pin_user_id)').eq('id', shortlist_id).execute()
            if not entry.data:
                return None
            
            # Verify user is the request owner
            if entry.data[0]['requests']['pin_user_id'] != pin_user_id:
                return None  # Not the request owner
            
            # Update feedback
            result = supabase.table('shortlist').update({
                'feedback_from_pin': feedback,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', shortlist_id).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error adding feedback: {str(e)}")
            return None
    
    @staticmethod
    def get_statistics(csr_user_id: int) -> Dict:
        """
        Get statistics for CSR's volunteer activity
        
        Args:
            csr_user_id: CSR user ID
            
        Returns:
            Dict with statistics
        """
        supabase = get_supabase()
        
        try:
            shortlist_entries = supabase.table('shortlist').select('id, status, volunteered_hours').eq('csr_user_id', csr_user_id).execute()
            
            if not shortlist_entries.data:
                return {
                    'total_shortlisted': 0,
                    'in_progress': 0,
                    'completed': 0,
                    'total_hours': 0
                }
            
            entries = shortlist_entries.data
            total_hours = sum([e.get('volunteered_hours') or 0 for e in entries])
            
            return {
                'total_shortlisted': len(entries),
                'shortlisted': len([e for e in entries if e['status'] == Shortlist.STATUS_SHORTLISTED]),
                'inProgress': len([e for e in entries if e['status'] == Shortlist.STATUS_IN_PROGRESS]),
                'completed': len([e for e in entries if e['status'] == Shortlist.STATUS_COMPLETED]),
                'declined': len([e for e in entries if e['status'] == Shortlist.STATUS_DECLINED]),
                'totalHoursVolunteered': total_hours
            }
            
        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {}
