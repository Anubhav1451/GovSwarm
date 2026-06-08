#!/usr/bin/env python3
"""
Script to check for existing users and organizations in the database.
"""

import psycopg2
from app.core.config import settings

def check_existing_data():
    """Check for existing users and organizations."""
    
    # Parse DATABASE_URL to get connection parameters
    db_url = settings.DATABASE_URL
    if "postgresql://" in db_url:
        db_url = db_url.replace("postgresql://", "")
    
    auth_part, rest = db_url.split("@")
    username_password = auth_part.split(":")
    username = username_password[0]
    password = username_password[1]
    
    host_port_db = rest.split("/")
    host_port = host_port_db[0]
    database = host_port_db[1].split("?")[0]
    
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host = host_port
        port = 5432
    
    print(f"Connecting to database: {database} at {host}:{port}")
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            sslmode='require'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check existing organizations
        print("\n=== Existing Organizations ===")
        cursor.execute("SELECT id, name FROM organizations LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Name: {row[1]}")
        
        # Check existing users
        print("\n=== Existing Users ===")
        cursor.execute("SELECT id, email, username FROM users LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Email: {row[1]}, Username: {row[2]}")
        
        # Check existing profiles
        print("\n=== Existing Profiles ===")
        cursor.execute("SELECT id, full_name FROM profiles LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Full Name: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error checking existing data: {e}")
        raise

if __name__ == "__main__":
    check_existing_data()
