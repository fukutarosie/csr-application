# Shortlist Count Fix Summary

## Issue
The `shortlist_count` field in the `requests` table was being incremented/decremented **twice** due to duplicate logic in both the Entity layer and the Controller layer.

## Root Cause
When a CSR Rep shortlisted or un-shortlisted a request, the count was being updated in three places:

### For Adding to Shortlist:
1. ✅ `Shortlist.add_to_shortlist()` (Entity) - Lines 98-110 in `shortlist.py`
2. ✅ `Request.increment_shortlist_count()` (Entity) - Called by Shortlist entity
3. ❌ `AddToShortlistController` (Controller) - Line 57 in `add_to_shortlist_controller.py` - **DUPLICATE**

### For Removing from Shortlist:
1. ✅ `Shortlist.remove_from_shortlist()` (Entity) - Lines 156-167 in `shortlist.py`
2. ✅ `Request.decrement_shortlist_count()` (Entity) - Called by Shortlist entity
3. ❌ `RemoveFromShortlistController` (Controller) - Line 52 in `remove_from_shortlist_controller.py` - **DUPLICATE**

## Solution
Removed the duplicate increment/decrement calls from the Controller layer, as the Entity layer already handles this correctly.

### Files Modified:

#### 1. `src/controller/shortlist/add_to_shortlist_controller.py`
- **Removed**: Line 57 - `Request.increment_shortlist_count(request_id)`
- **Removed**: Import of `Request` entity (no longer needed)
- **Added**: Comment explaining that shortlist_count is automatically handled by Entity layer

#### 2. `src/controller/shortlist/remove_from_shortlist_controller.py`
- **Removed**: Lines 30-36 - Code to fetch `request_id` before deletion
- **Removed**: Lines 51-52 - `Request.decrement_shortlist_count(request_id)`
- **Removed**: Import of `Request` entity (no longer needed)
- **Added**: Comment explaining that shortlist_count is automatically handled by Entity layer

## How It Works Now

### Adding to Shortlist:
```
1. CSR Rep clicks "Add to Shortlist" in frontend
2. Frontend calls POST /api/shortlist
3. Boundary layer receives request
4. Controller calls Shortlist.add_to_shortlist()
5. Entity layer:
   a. Validates user is CSR
   b. Validates request is ACTIVE
   c. Checks for duplicates
   d. Inserts shortlist entry
   e. ✅ Increments shortlist_count by 1
6. Returns success response
```

### Removing from Shortlist:
```
1. CSR Rep clicks "Remove from Shortlist" in frontend
2. Frontend calls DELETE /api/shortlist/{id}
3. Boundary layer receives request
4. Controller calls Shortlist.remove_from_shortlist()
5. Entity layer:
   a. Verifies ownership
   b. Gets request_id before deletion
   c. Deletes shortlist entry
   d. ✅ Decrements shortlist_count by 1 (minimum 0)
6. Returns success response
```

## Testing Results

Test performed on **Request ID 14** with initial `shortlist_count: 5`:

1. ✅ **Remove from shortlist**: Count decreased from 5 → 4
2. ✅ **Add to shortlist**: Count increased from 4 → 5

**Result**: Both increment and decrement work correctly! ✅

## Benefits

1. **No Duplicate Updates**: Count is updated exactly once per operation
2. **Accurate Count**: Reflects the actual number of unique CSR Reps who shortlisted the request
3. **Cleaner Architecture**: Controller layer doesn't duplicate Entity layer logic
4. **Follows BCE Pattern**: Business logic stays in Entity layer, Controller only orchestrates

## Database Schema

The `shortlist_count` field in the `requests` table now accurately represents:
- **Definition**: Number of unique CSR Reps who have currently shortlisted this request
- **Increment**: When a CSR Rep adds request to their shortlist (+1)
- **Decrement**: When a CSR Rep removes request from their shortlist (-1)
- **Minimum**: 0 (cannot go negative)

## Related Files

- `src/entity/shortlist.py` - Shortlist Entity (handles increment/decrement)
- `src/entity/request.py` - Request Entity (contains increment/decrement methods)
- `src/controller/shortlist/add_to_shortlist_controller.py` - Add to Shortlist Controller
- `src/controller/shortlist/remove_from_shortlist_controller.py` - Remove from Shortlist Controller
- `src/controller/shortlist/boundary/shortlist_boundary.py` - Shortlist Boundary (HTTP interface)

## Date
November 8, 2025




