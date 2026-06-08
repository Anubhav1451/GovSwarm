import requests
import time
import os
import random
import uuid
from pathlib import Path
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Configuration - URL failover logic
API_HOSTS = ["http://127.0.0.1:8000", "http://localhost:8000"]
API_BASE_URL = None
UPLOAD_URL = None
METRICS_URL = None
LOGIN_URL = None

# Test credentials (ensure user exists in database)
TEST_EMAIL = "auditor@govswarm.com"
TEST_PASSWORD = "password123"
TEST_ORGANIZATION_ID = "f5e712ef-bd06-4750-83c2-4adc99a2ba80"
TEST_USER_ID = "1822270a-cde5-4761-a8e2-122f1c4e9dc2"

# Test file path (create a dummy PDF file for testing)
TEST_FILE_PATH = "test_document.pdf"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def determine_api_url():
    """Determine the working API URL by testing both 127.0.0.1 and localhost."""
    global API_BASE_URL, UPLOAD_URL, METRICS_URL, LOGIN_URL
    
    for host in API_HOSTS:
        try:
            test_url = f"{host}/"
            response = requests.get(test_url, timeout=2)
            if response.status_code == 200:
                API_BASE_URL = f"{host}/api/v1"
                UPLOAD_URL = f"{API_BASE_URL}/documents/upload"
                METRICS_URL = f"{host}/metrics"
                LOGIN_URL = f"{API_BASE_URL}/auth/login"
                print(f"API URL determined: {API_BASE_URL}")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            continue
    
    print("Failed to connect to API on both 127.0.0.1:8000 and localhost:8000")
    return False


def seed_test_organization():
    """Auto-seed the test organization in the database if it doesn't exist."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment. Skipping organization seeding.")
        return
    
    try:
        print("Checking if test organization exists in database...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if organization already exists
            result = conn.execute(text("SELECT id FROM organizations WHERE id = :id"), {"id": TEST_ORGANIZATION_ID})
            existing_org = result.fetchone()
            
            if existing_org:
                print(f"Test organization {TEST_ORGANIZATION_ID} already exists. Skipping seeding.")
                return
            
            print(f"Test organization {TEST_ORGANIZATION_ID} not found. Creating...")
            
            # Insert the organization with all required fields
            conn.execute(
                text("""
                    INSERT INTO organizations (id, name, owner_id, status, country_code, created_at, updated_at)
                    VALUES (:id, :name, :owner_id, :status, :country_code, NOW(), NOW())
                """),
                {
                    "id": TEST_ORGANIZATION_ID,
                    "name": "GovSwarm Test Org",
                    "owner_id": TEST_USER_ID,
                    "status": "active",
                    "country_code": "IND"
                }
            )
            conn.commit()
            
            print(f"Successfully created test organization:")
            print(f"  Organization ID: {TEST_ORGANIZATION_ID}")
            print(f"  Name: GovSwarm Test Org")
            print(f"  Owner ID: {TEST_USER_ID}")
            print(f"  Status: active")
            print(f"  Country Code: IND")
            
    except Exception as e:
        print(f"Error seeding test organization: {e}")
        print("Organization seeding failed. You may need to create the organization manually.")


def seed_test_user():
    """Auto-seed the test user in the database if it doesn't exist."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment. Skipping user seeding.")
        return
    
    try:
        print("Checking if test user exists in database...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if user already exists
            result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": TEST_EMAIL})
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"Test user {TEST_EMAIL} already exists. Skipping seeding.")
                return
            
            print(f"Test user {TEST_EMAIL} not found. Creating...")
            
            # Hash the password
            hashed_password = pwd_context.hash(TEST_PASSWORD)
            user_id = str(uuid.uuid4())
            
            # Insert the user
            conn.execute(
                text("""
                    INSERT INTO users (id, email, username, full_name, hashed_password, role, organization_id, is_active)
                    VALUES (:id, :email, :username, :full_name, :hashed_password, :role, :organization_id, :is_active)
                """),
                {
                    "id": user_id,
                    "email": TEST_EMAIL,
                    "username": "auditor",
                    "full_name": "Test Auditor",
                    "hashed_password": hashed_password,
                    "role": "AUDITOR",
                    "organization_id": TEST_ORGANIZATION_ID,
                    "is_active": True
                }
            )
            conn.commit()
            
            print(f"Successfully created test user:")
            print(f"  Email: {TEST_EMAIL}")
            print(f"  Password: {TEST_PASSWORD}")
            print(f"  User ID: {user_id}")
            print(f"  Organization ID: {TEST_ORGANIZATION_ID}")
            print(f"  Role: AUDITOR")
            
    except Exception as e:
        print(f"Error seeding test user: {e}")
        print("User seeding failed. You may need to create the user manually.")


def create_test_file():
    """Create a dummy test file for upload simulation."""
    # Generate a minimal valid PDF format dynamically
    timestamp = f"% Dynamic: {time.time()}-{random.randint(1000, 9999)}\n"
    minimal_pdf_bytes = (
        b"%PDF-1.4\n"
        + timestamp.encode('utf-8')
        + b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        + b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        + b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R>> endobj\n"
        + b"4 0 obj <</Length 48>> stream\n"
        + b"BT /F1 24 Tf 100 700 Td (GovSwarm Live Traffic Audit Test) Tj ET\n"
        + b"endstream\n"
        + b"endobj\n"
        + b"xref\n"
        + b"0 5\n"
        + b"0000000000 65535 f \n"
        + b"0000000009 00000 n \n"
        + b"0000000056 00000 n \n"
        + b"0000000111 00000 n \n"
        + b"0000000212 00000 n \n"
        + b"trailer <</Size 5 /Root 1 0 R>>\n"
        + b"startxref\n"
        + b"311\n"
        + b"%%EOF"
    )
    with open(TEST_FILE_PATH, "wb") as f:
        f.write(minimal_pdf_bytes)


def login():
    """Authenticate with the API and obtain JWT access token."""
    print("Authenticating with API...")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            access_token = result.get("access_token")
            print(f"Login successful! User ID: {result.get('user_id')}, Role: {result.get('role')}")
            return access_token
        else:
            print(f"Login failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            print("\n" + "="*60)
            print("IMPORTANT: Ensure a user with these credentials exists:")
            print(f"  Email: {TEST_EMAIL}")
            print(f"  Password: {TEST_PASSWORD}")
            print("  Role: AUDITOR or ADMIN")
            print("  Organization ID must be set")
            print("="*60 + "\n")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        print("\n" + "="*60)
        print("IMPORTANT: Ensure a user with these credentials exists:")
        print(f"  Email: {TEST_EMAIL}")
        print(f"  Password: {TEST_PASSWORD}")
        print("  Role: AUDITOR or ADMIN")
        print("  Organization ID must be set")
        print("="*60 + "\n")
        return None


def simulate_upload(access_token):
    """Simulate document upload to the API with JWT authentication."""
    print("Simulating document upload...")
    
    # Create test file if it doesn't exist
    if not os.path.exists(TEST_FILE_PATH):
        create_test_file()
    
    # Prepare upload data with JWT authorization header
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    files = {
        "file": (TEST_FILE_PATH, open(TEST_FILE_PATH, "rb"), "application/pdf")
    }
    
    try:
        response = requests.post(UPLOAD_URL, files=files, headers=headers)
        print(f"Upload Response Status: {response.status_code}")
        print(f"Upload Response Body: {response.json()}")
        
        if response.status_code == 202:
            result = response.json()
            document_id = result.get("document_id")
            status = result.get("status")
            print(f"Document ID: {document_id}")
            print(f"Initial Status: {status}")
            return document_id
        else:
            print(f"Upload failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Upload error: {e}")
        return None
    finally:
        files["file"][1].close()


def poll_document_status(document_id, access_token, max_retries=30, interval=2):
    """Poll document status until terminal state is reached with JWT authentication."""
    print(f"\nPolling document status for ID: {document_id}")
    
    status_url = f"{API_BASE_URL}/documents/{document_id}/status"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(status_url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                current_status = result.get("status")
                print(f"Attempt {attempt + 1}/{max_retries}: Status = {current_status}")
                
                if current_status in ["COMPLETED", "FAILED"]:
                    print(f"Terminal state reached: {current_status}")
                    return result
            else:
                print(f"Status check failed with status code: {response.status_code}")
        except Exception as e:
            print(f"Status polling error: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(interval)
    
    print("Max retries reached without terminal state")
    return None


def fetch_metrics():
    """Fetch and display Prometheus metrics."""
    print("\nFetching Prometheus metrics...")
    
    try:
        response = requests.get(METRICS_URL)
        if response.status_code == 200:
            metrics = response.text
            print(f"Metrics Response Status: {response.status_code}")
            print("Metrics Output (first 500 chars):")
            print(metrics[:500])
            print("...")
            return metrics
        else:
            print(f"Metrics fetch failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Metrics fetch error: {e}")
        return None


def main():
    """Main simulation workflow with JWT authentication."""
    print("=== GovSwarm Traffic Simulation ===\n")
    
    # Step -2: Seed test organization if not exists
    seed_test_organization()
    print()
    
    # Step -1: Seed test user if not exists
    seed_test_user()
    print()
    
    # Step 0: Determine working API URL
    if not determine_api_url():
        print("\nSimulation failed: Could not connect to API")
        return
    
    # Step 1: Authenticate and get access token
    access_token = login()
    
    if not access_token:
        print("\nSimulation failed at authentication stage")
        return
    
    # Step 2: Simulate upload with authentication
    document_id = simulate_upload(access_token)
    
    if document_id:
        # Step 3: Poll status until terminal state with authentication
        final_status = poll_document_status(document_id, access_token)
        
        if final_status:
            print(f"\nFinal Document Status: {final_status}")
        
        # Step 4: Fetch metrics
        metrics = fetch_metrics()
        
        if metrics:
            print("\nSimulation completed successfully!")
        else:
            print("\nSimulation completed with metrics fetch failure")
    else:
        print("\nSimulation failed at upload stage")
    
    # Cleanup test file
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
        print("Test file cleaned up")


if __name__ == "__main__":
    main()
