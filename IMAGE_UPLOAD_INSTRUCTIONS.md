# Image Upload Feature - Setup Instructions

## ✅ Backend Implementation Complete

The backend infrastructure for image uploads is now complete:

1. ✅ **Image Upload Utility** (`src/utils/image_upload.py`)
   - Handles base64 image conversion
   - Validates file types (PNG, JPG, JPEG, GIF, WEBP)
   - Validates file size (max 5MB)
   - Generates unique filenames
   - Stores in `static/uploads/requests/`

2. ✅ **Entity Layer** (`src/entity/request.py`)
   - `create_request()` now accepts `image_url` parameter
   - `update_request()` supports image_url updates

3. ✅ **Controller Layer** (`src/controller/request/create_pin_new_request.py`)
   - Handles `image` field in POST request
   - Calls `save_base64_image()` utility
   - Passes image URL to entity
   - Returns appropriate errors if upload fails

## ✅ Frontend Implementation Complete

The frontend now supports image uploads:

1. ✅ **Create Request Form** (`src/app/pin/request/new/page.js`)
   - File input with drag-and-drop area
   - Image preview before submission
   - File type validation
   - File size validation (max 5MB)
   - Base64 encoding for API submission

2. ✅ **Request Detail Page** (`src/app/pin/request/[id]/page.js`)
   - Displays uploaded image if available
   - Responsive image display with proper sizing

## ⚠️ REQUIRED: Database Migration

Before the feature will work, you **MUST** add the `image_url` column to your database:

### Step 1: Open Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**

### Step 2: Run Migration

Copy and paste this SQL command:

```sql
ALTER TABLE requests 
ADD COLUMN IF NOT EXISTS image_url TEXT;
```

Click **Run** to execute.

### Step 3: Verify Column Added

Run this query to confirm:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'requests' 
AND column_name = 'image_url';
```

You should see:
```
column_name | data_type
image_url   | text
```

## 📋 Testing the Feature

Once database migration is complete:

### Test 1: Create Request with Image

1. Start servers:
   ```powershell
   python app.py
   npm run dev
   ```

2. Login as PIN user:
   - Email: `pin_user1@test.com`
   - Password: `password123`

3. Navigate to **Create New Request**

4. Fill out the form and upload an image:
   - Click the upload area
   - Select an image (PNG, JPG, GIF, or WEBP, under 5MB)
   - Verify preview appears
   - Submit form

5. Verify:
   - Request created successfully
   - Redirected to request detail page
   - Image displays on detail page

### Test 2: View Request with Image

1. Navigate to **PIN Dashboard**
2. Click on a request that has an image
3. Verify image displays properly

### Test 3: Image Validation

Test error handling:
- Try uploading file > 5MB (should show error)
- Try uploading non-image file (should show error)
- Try uploading unsupported format like PDF (should show error)

## 🔧 Configure Flask Static Files

Ensure Flask is configured to serve static files. In `app.py`:

```python
from flask import Flask

app = Flask(__name__, static_folder='static')

# This allows accessing /static/uploads/requests/image.jpg
```

This should already be configured, but verify it if images don't load.

## 📁 File Structure

```
csr_app/
├── src/
│   ├── utils/
│   │   └── image_upload.py          ✅ NEW
│   ├── entity/
│   │   └── request.py                ✅ MODIFIED
│   ├── controller/
│   │   └── request/
│   │       └── create_pin_new_request.py  ✅ MODIFIED
│   └── app/
│       └── pin/
│           └── request/
│               ├── new/
│               │   └── page.js       ✅ MODIFIED
│               └── [id]/
│                   └── page.js       ✅ MODIFIED
└── static/
    └── uploads/
        └── requests/                 ✅ NEW (storage directory)
```

## 🎯 Feature Summary

**What Works:**
- PIN users can upload images when creating requests
- Images are validated for type and size
- Images are stored securely on the server
- Images display on request detail pages
- Preview images before submission
- Remove images before submission

**Image Requirements:**
- Formats: PNG, JPG, JPEG, GIF, WEBP
- Max Size: 5MB
- Transport: Base64 encoding via JSON
- Storage: Local filesystem (`static/uploads/requests/`)

**Security Features:**
- File type validation
- File size limits
- Unique filenames (prevents collisions)
- Non-executable directory (no script execution)

## 🚀 Next Steps

After completing the database migration:

1. **Test thoroughly** with different image types and sizes
2. **Verify error handling** works for invalid files
3. **Check CSR browse page** to see if images display there too (may need additional work)
4. **Consider adding image update** functionality (allow editing request images)
5. **Consider adding image delete** functionality (remove image from existing request)

## 📝 API Documentation Update

The `/api/requests` POST endpoint now accepts an optional `image` field:

```json
POST /api/requests
Authorization: Bearer <token>

{
  "title": "Need grocery delivery",
  "description": "Heavy groceries, need help carrying",
  "category": "Food",
  "service_type": "Delivery",
  "priority": "HIGH",
  "location_city": "Bangkok",
  "location_detail": "44/123 Sukhumvit Rd",
  "requested_by_date": "2025-10-31",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."  // OPTIONAL
}
```

Response includes `image_url` if image was uploaded:

```json
{
  "success": true,
  "data": {
    "id": 123,
    "title": "Need grocery delivery",
    "image_url": "/static/uploads/requests/1699276800_abc123.jpg",
    ...
  }
}
```

## ❓ Troubleshooting

### Images not displaying?

1. Check Flask static folder configuration
2. Verify file exists in `static/uploads/requests/`
3. Check browser console for 404 errors
4. Ensure backend URL is correct (`http://localhost:5000`)

### Upload fails with "Image upload failed"?

1. Check file size (must be under 5MB)
2. Check file type (must be PNG/JPG/GIF/WEBP)
3. Check backend logs for detailed error messages
4. Verify `static/uploads/requests/` directory exists and is writable

### Database errors?

1. Verify `image_url` column exists in `requests` table
2. Check column is TEXT type
3. Verify no NOT NULL constraints on the column (should be optional)

---

**Status:** ✅ Implementation Complete - Requires Database Migration
