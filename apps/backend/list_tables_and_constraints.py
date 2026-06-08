#!/usr/bin/env python3
"""
Script to list all tables and their foreign key constraints.
"""

import psycopg2
from app.core.config import settings

def list_tables_and_constraints():
    """List all tables and their foreign key constraints."""
    
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
        
        # List all tables
        print("\n=== All Tables ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}")
        
        # List foreign key constraints for profiles table
        print("\n=== Foreign Key Constraints for profiles ===")
        cursor.execute("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'profiles'
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} -> {row[2]}.{row[3]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error listing tables and constraints: {e}")
        raise

if __name__ == "__main__":
    list_tables_and_constraints()
