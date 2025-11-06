# Add Image Upload to PIN Requests - Implementation Plan

## Overview
Add image upload functionality so PIN users can attach photos when creating requests.

## Implementation Steps

### 1. Database Schema Update ✅ (SQL)
Add `image_url` column to `requests` table:
```sql
ALTER TABLE requests ADD COLUMN image_url TEXT;
```

### 2. Backend - Entity Layer Update
**File:** `src/entity/request.py`
- Add `image_url` parameter to `create_request()` method
- Add `image_url` to request_data dict
- Add `image_url` parameter to `update_request()` method

### 3. Backend - Image Upload Utility
**File:** `src/utils/image_upload.py` (NEW)
- Create utility function to handle base64 image upload
- Save images to `static/uploads/requests/` folder
- Generate unique filenames (timestamp + UUID)
- Return image URL path

### 4. Backend - Controller Update
**File:** `src/controller/requests/boundary/create_request_boundary.py`
- Accept `image` field in request JSON (base64 encoded)
- Call image upload utility
- Pass `image_url` to entity create method

### 5. Frontend - Create Request Form
**File:** `src/app/pin/request/new/page.js`
- Add file input for image upload
- Preview selected image
- Convert image to base64 before sending to API
- Send base64 image in request payload

### 6. Frontend - Display Request Image
**File:** `src/app/pin/request/[id]/page.js`
- Display uploaded image if exists
- Show placeholder if no image

**File:** `src/app/pin/dashboard/page.js`
- Optionally show thumbnail in table

**File:** `src/app/csr/browse/page.js`
- Show image in CSR browse view

## Technical Approach

### Image Storage: Local File System
- Store images in: `csr_app/static/uploads/requests/`
- Serve via Flask static files
- Image URL format: `/static/uploads/requests/{filename}`

### Image Format
- Accept: JPEG, PNG, GIF, WebP
- Max size: 5MB
- Convert to base64 for transport
- Save as file on server

### File Naming Convention
- Format: `{timestamp}_{uuid}_{original_extension}`
- Example: `1699276800_a1b2c3d4_photo.jpg`

## Security Considerations
- Validate file type (only images)
- Validate file size (max 5MB)
- Sanitize filenames
- Store in non-executable directory
- No direct file path exposure

## Next Steps
1. Run SQL migration
2. Update entity class
3. Create image upload utility
4. Update controller
5. Update frontend form
6. Test end-to-end
