#!/usr/bin/env python3
"""Test password for admin1 user"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entity import User
from werkzeug.security import check_password_hash

user = User.get_user_by_username('admin1')

if user:
    print(f"\n{'='*60}")
    print(f"User: {user['username']}")
    print(f"Full Name: {user['full_name']}")
    print(f"Email: {user['email']}")
    print(f"Is Active: {user['is_active']}")
    print(f"{'='*60}")

    # Test different passwords
    print(f"Full Name: {user['full_name']}")
    print(f"Email: {user['email']}")
    print(f"Is Active: {user['is_active']}")
    print(f"{'='*60}")
    
    # Test different passwords
    passwords_to_test = ['csr123', 'admin123', 'password', '123456']
    
    print(f"\nTesting passwords:")
    for pwd in passwords_to_test:
        is_correct = check_password_hash(user['password'], pwd)
        status = "✓ CORRECT" if is_correct else "✗ Wrong"
        print(f"  {pwd:15} -> {status}")
    
    print(f"\n{'='*60}")
    print("❓ Which password should be used?")
    print("Try one of the correct passwords above!")
    print(f"{'='*60}\n")
else:
    print("User admin1 not found!")
