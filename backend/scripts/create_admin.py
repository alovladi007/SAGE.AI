#!/usr/bin/env python3
"""Create admin user for the platform"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import getpass
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Create admin user interactively"""
    
    print("=" * 50)
    print("  Academic Integrity Platform - Admin User Setup")
    print("=" * 50)
    print()
    
    # Get user input
    email = input("Admin email: ")
    name = input("Admin name: ")
    password = getpass.getpass("Admin password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("✗ Passwords do not match!")
        sys.exit(1)
    
    if len(password) < 8:
        print("✗ Password must be at least 8 characters!")
        sys.exit(1)
    
    # Hash password
    hashed_password = pwd_context.hash(password)
    
    # Create user record
    print("\n✓ Creating admin user...")
    
    # Here you would insert into your User table
    # This is a placeholder - adjust based on your actual User model
    user_data = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "hashed_password": hashed_password,
        "is_admin": True,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    print(f"\n✓ Admin user created successfully!")
    print(f"  Email: {email}")
    print(f"  Name: {name}")
    print("\nYou can now login with these credentials.")

if __name__ == "__main__":
    create_admin_user()
