#!/usr/bin/env python3
"""
Hot-fix script to insert dummy organization and user rows for testing.
"""

import psycopg2
from app.core.config import settings

def insert_dummy_data():
    """Insert dummy organization and user rows."""
    
    # Parse DATABASE_URL to get connection parameters
    db_url = settings.DATABASE_URL
    # Format: postgresql://postgres.lmtxruivxlhvxrilruiv:Anubhav8789@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require
    
    # Extract connection details
    if "postgresql://" in db_url:
        db_url = db_url.replace("postgresql://", "")
    
    # Split user:password@host:port/database
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
        
        # Disable foreign key constraints temporarily
        cursor.execute("SET session_replication_role = replica")
        print("✓ Disabled foreign key constraints temporarily")
        
        # Insert dummy organization with owner_id pointing to same UUID as user (breaks circular dependency)
        org_sql = """
            INSERT INTO organizations (id, owner_id, name, organization_type, status, country_code, created_at, updated_at) 
            VALUES ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 'Test Org', 'VENDOR', 'active', 'IND', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """
        cursor.execute(org_sql)
        print("✓ Successfully inserted/verified dummy organization")
        
        # Insert dummy user (references organization)
        user_sql = """
            INSERT INTO users (id, email, username, full_name, role, organization_id, created_at, updated_at) 
            VALUES ('22222222-2222-2222-2222-222222222222', 'test@example.com', 'simulator_bot', 'Simulator Bot', 'VENDOR', '11111111-1111-1111-1111-111111111111', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """
        cursor.execute(user_sql)
        print("✓ Successfully inserted/verified dummy user")
        
        # Insert dummy profile (references users.id)
        profile_sql = """
            INSERT INTO profiles (id, full_name, role, created_at, updated_at) 
            VALUES ('22222222-2222-2222-2222-222222222222', 'Simulator Bot', 'VENDOR', NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """
        cursor.execute(profile_sql)
        print("✓ Successfully inserted/verified dummy profile")
        
        # Re-enable foreign key constraints
        cursor.execute("SET session_replication_role = DEFAULT")
        print("✓ Re-enabled foreign key constraints")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error inserting dummy data: {e}")
        raise

if __name__ == "__main__":
    insert_dummy_data()
