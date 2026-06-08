#!/usr/bin/env python3
"""
Hot-fix script to add all missing metadata columns to the documents table.
"""

import psycopg2
from app.core.config import settings

def add_all_metadata_columns():
    """Add all missing metadata columns to documents table."""
    
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
        
        # Add all missing metadata columns in a single statement
        alter_sql = """
            ALTER TABLE documents 
            ADD COLUMN IF NOT EXISTS page_count INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS author VARCHAR DEFAULT '',
            ADD COLUMN IF NOT EXISTS title VARCHAR DEFAULT '',
            ADD COLUMN IF NOT EXISTS extracted_text TEXT DEFAULT '',
            ADD COLUMN IF NOT EXISTS extracted_entities JSONB DEFAULT '{}'::jsonb
        """
        
        cursor.execute(alter_sql)
        print("✓ Successfully added all metadata columns to documents table")
        print("  - page_count (INTEGER, default 0)")
        print("  - author (VARCHAR, default '')")
        print("  - title (VARCHAR, default '')")
        print("  - extracted_text (TEXT, default '')")
        print("  - extracted_entities (JSONB, default {})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error adding metadata columns: {e}")
        raise

if __name__ == "__main__":
    add_all_metadata_columns()
