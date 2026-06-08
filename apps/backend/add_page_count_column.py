#!/usr/bin/env python3
"""
Hot-fix script to add the missing page_count column to the documents table.
"""

import psycopg2
from app.core.config import settings

def add_page_count_column():
    """Add page_count column to documents table if it doesn't exist."""
    
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
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'documents' 
            AND column_name = 'page_count'
        """)
        
        if cursor.fetchone():
            print("✓ page_count column already exists in documents table")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE documents 
                ADD COLUMN IF NOT EXISTS page_count INTEGER DEFAULT 0
            """)
            print("✓ Successfully added page_count column to documents table")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error adding page_count column: {e}")
        raise

if __name__ == "__main__":
    add_page_count_column()
