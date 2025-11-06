"""
Image Upload Utility for PIN Requests
Handles base64 image upload and storage
"""

import os
import base64
import uuid
from datetime import datetime
from typing import Optional, Tuple

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_base64_image(base64_string: str, original_filename: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Save base64 encoded image to file system
    
    Args:
        base64_string: Base64 encoded image string (with or without data:image prefix)
        original_filename: Original filename (optional, for extension detection)
    
    Returns:
        Tuple of (success, image_url, error_message)
    """
    try:
        # Remove data:image prefix if present
        if ',' in base64_string:
            header, base64_string = base64_string.split(',', 1)
            # Extract extension from header (e.g., data:image/png;base64)
            if 'image/' in header:
                ext = header.split('image/')[1].split(';')[0]
                if ext == 'jpeg':
                    ext = 'jpg'
            else:
                ext = 'jpg'  # default
        else:
            # Try to get extension from original filename
            if original_filename and '.' in original_filename:
                ext = original_filename.rsplit('.', 1)[1].lower()
            else:
                ext = 'jpg'  # default
        
        # Validate extension
        if ext not in ALLOWED_EXTENSIONS:
            return False, None, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Decode base64
        try:
            image_data = base64.b64decode(base64_string)
        except Exception as e:
            return False, None, f"Invalid base64 encoding: {str(e)}"
        
        # Check file size
        if len(image_data) > MAX_FILE_SIZE:
            return False, None, f"File too large. Maximum size: 5MB"
        
        # Generate unique filename
        timestamp = int(datetime.utcnow().timestamp())
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}.{ext}"
        
        # Get upload directory
        # Assuming app.py is in root, static is in root/static
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_dir = os.path.join(base_dir, 'static', 'uploads', 'requests')
        
        # Create directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Full file path
        filepath = os.path.join(upload_dir, filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # Return URL path (relative to static folder)
        image_url = f"/static/uploads/requests/{filename}"
        
        return True, image_url, None
        
    except Exception as e:
        return False, None, f"Failed to save image: {str(e)}"

def delete_image(image_url: str) -> bool:
    """
    Delete image file from file system
    
    Args:
        image_url: URL path of image (e.g., /static/uploads/requests/123_abc.jpg)
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if not image_url or not image_url.startswith('/static/uploads/requests/'):
            return False
        
        # Extract filename from URL
        filename = image_url.split('/')[-1]
        
        # Get full file path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        filepath = os.path.join(base_dir, 'static', 'uploads', 'requests', filename)
        
        # Delete file if exists
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False
