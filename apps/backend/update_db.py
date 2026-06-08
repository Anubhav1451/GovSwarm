import os
from sqlalchemy import create_engine, text

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("ERROR: DATABASE_URL not found in environment")
    exit(1)

print("Connecting to database...")
engine = create_engine(database_url)

try:
    with engine.connect() as conn:
        print("Adding hashed_password column if not exists...")
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)"))
        conn.commit()
        print("✓ hashed_password column added")
        
        print("Adding is_active column if not exists...")
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"))
        conn.commit()
        print("✓ is_active column added")
        
    print("\nDatabase schema update completed successfully!")
    
except Exception as e:
    print(f"ERROR: Failed to update database schema: {e}")
    exit(1)
