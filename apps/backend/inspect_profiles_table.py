#!/usr/bin/env python3
"""
Script to inspect the profiles table structure.
"""

import psycopg2
from app.core.config import settings

def inspect_profiles_table():
    """Inspect profiles table structure."""
    
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
        
        # Inspect profiles table
        print("\n=== Profiles Table Structure ===")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'profiles'
            ORDER BY ordinal_position
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error inspecting profiles table: {e}")
        raise

if __name__ == "__main__":
    inspect_profiles_table()
