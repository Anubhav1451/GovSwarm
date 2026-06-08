#!/usr/bin/env python3
"""
Database schema synchronization script.
This script creates missing tables and columns in the database based on SQLAlchemy models.
"""

from app.db.session import engine, Base
from app.models import document, organization, user, user_role, audit_log, audit_run, audit_finding, dead_letter_job, verification_result, document_status

def sync_database():
    """Create all tables and columns that don't exist in the database."""
    print("Synchronizing database schema with SQLAlchemy models...")
    try:
        # This will create any missing tables and columns
        # It won't drop existing tables or columns
        Base.metadata.create_all(bind=engine)
        print("✓ Database schema synchronized successfully!")
        print("✓ Missing tables and columns have been created.")
    except Exception as e:
        print(f"✗ Error synchronizing database: {e}")
        raise

if __name__ == "__main__":
    sync_database()
