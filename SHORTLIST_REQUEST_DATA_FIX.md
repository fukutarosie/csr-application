# Shortlist Request Data Fix ✅

## Problem
The CSR shortlist page (`/csr/shortlist`) was loading, but the request details (title, description, service_type, etc.) were not being displayed because the joined `requests` data was not being returned by the API.

## Root Cause
The `Shortlist` entity was fetching the joined request data using `select('*, requests(*)')` in the database query, but:

1. **Not storing it**: The `_load_from_dict()` method was not storing the `requests` field
2. **Not returning it**: The `to_dict()` method was not including the `requests` field in the API response

This meant the frontend received shortlist items without any request details:
```json
{
  "id": 1,
  "csr_user_id": 2,
  "request_id": 5,
  "status": "SHORTLISTED",
  "notes": null,
  // ❌ Missing: "requests": {...}
}
```

## Solution
Updated the `Shortlist` entity to properly store and return the joined request data:

### 1. Added Instance Variable (line 67)
```python
self.requests: Optional[Dict] = None  # Store joined request data
```

### 2. Updated `_load_from_dict()` (line 103)
```python
def _load_from_dict(self, data: Dict) -> None:
    """Populate instance variables from dictionary (private method)"""
    self.id = data.get('id')
    self.csr_user_id = data.get('csr_user_id')
    self.request_id = data.get('request_id')
    self.status = data.get('status', Shortlist.STATUS_SHORTLISTED)
    self.notes = data.get('notes')
    self.volunteered_hours = data.get('volunteered_hours')
    self.completion_date = data.get('completion_date')
    self.feedback_from_pin = data.get('feedback_from_pin')
    self.shortlisted_at = data.get('shortlisted_at')
    self.updated_at = data.get('updated_at')
    self.requests = data.get('requests')  # ✅ Store joined request data
```

### 3. Updated `to_dict()` (line 346)
```python
def to_dict(self) -> Dict:
    """Convert instance to dictionary (for API responses)"""
    return {
        'id': self.id,
        'csr_user_id': self.csr_user_id,
        'request_id': self.request_id,
        'status': self.status,
        'notes': self.notes,
        'volunteered_hours': self.volunteered_hours,
        'completion_date': self.completion_date,
        'feedback_from_pin': self.feedback_from_pin,
        'shortlisted_at': self.shortlisted_at,
        'updated_at': self.updated_at,
        'requests': self.requests  # ✅ Include joined request data
    }
```

## What Data is Now Returned

The API now returns complete shortlist items with full request details:

```json
{
  "id": 1,
  "csr_user_id": 2,
  "request_id": 5,
  "status": "SHORTLISTED",
  "notes": "Interested in helping",
  "volunteered_hours": null,
  "completion_date": null,
  "feedback_from_pin": null,
  "shortlisted_at": "2025-11-08T10:30:00Z",
  "updated_at": "2025-11-08T10:30:00Z",
  "requests": {
    "id": 5,
    "pin_user_id": 3,
    "title": "Need help with grocery shopping",
    "description": "Weekly grocery shopping assistance needed",
    "service_type": "Grocery Shopping",
    "region": "Hougang",
    "status": "ACTIVE",
    "requested_by_date": "2025-11-15",
    "created_at": "2025-11-08T09:00:00Z",
    "updated_at": "2025-11-08T09:00:00Z",
    "view_count": 10,
    "shortlist_count": 3,
    "image_url": "/uploads/requests/image.jpg"
  }
}
```

## Frontend Display Fields

The frontend can now correctly display:
- ✅ `item.requests.title` - Request title
- ✅ `item.requests.description` - Request description
- ✅ `item.requests.service_type` - Service type
- ✅ `item.requests.region` - Location
- ✅ `item.requests.category` - Category
- ✅ `item.requests.priority` - Priority
- ✅ `item.requests.status` - Request status
- ✅ All other request fields

## File Modified
- ✅ `src/entity/shortlist.py`

## Testing Steps

1. **Restart Backend** (important - entity changes require restart):
   ```powershell
   # Stop backend (Ctrl+C)
   cd "C:\Users\Fukutaro\Downloads\LENOVO LAPTOP FILE TRANSFER\Subject Modules\CSIT314 Software Development Methodologies\CSR (ScrumMasters)\csr_app"
   .\venv\Scripts\activate
   python app.py
   ```

2. **Test as CSR Rep** (`csr_rep1` / `password123`):
   - Go to `/csr/browse`
   - Add some requests to shortlist
   - Go to `/csr/shortlist`
   - **Should now see**:
     - ✅ Request titles displayed
     - ✅ Request descriptions displayed
     - ✅ Service types displayed
     - ✅ Regions/locations displayed
     - ✅ All request details visible

## Status
✅ **FIXED** - Shortlist now displays complete request data!

