#!/usr/bin/env python3
"""
Hot-fix script to add all missing timestamp columns to the documents table.
"""

import psycopg2
from app.core.config import settings

def add_timestamp_columns():
    """Add all missing timestamp columns to documents table."""
    
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
        
        # Add all missing timestamp columns in a single statement
        alter_sql = """
            ALTER TABLE documents 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS processing_completed_at TIMESTAMP WITH TIME ZONE
        """
        
        cursor.execute(alter_sql)
        print("✓ Successfully added all timestamp columns to documents table")
        print("  - updated_at (TIMESTAMP WITH TIME ZONE, default CURRENT_TIMESTAMP)")
        print("  - processing_started_at (TIMESTAMP WITH TIME ZONE, nullable)")
        print("  - processing_completed_at (TIMESTAMP WITH TIME ZONE, nullable)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error adding timestamp columns: {e}")
        raise

if __name__ == "__main__":
    add_timestamp_columns()
