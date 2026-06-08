import requests
import time
import os
import random
from pathlib import Path

# Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
UPLOAD_URL = f"{API_BASE_URL}/documents/upload"
METRICS_URL = "http://127.0.0.1:8000/metrics"

# Test file path (create a dummy PDF file for testing)
TEST_FILE_PATH = "test_document.pdf"


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


def simulate_upload():
    """Simulate document upload to the API."""
    print("Simulating document upload...")
    
    # Create test file if it doesn't exist
    if not os.path.exists(TEST_FILE_PATH):
        create_test_file()
    
    # Prepare upload data
    files = {
        "file": (TEST_FILE_PATH, open(TEST_FILE_PATH, "rb"), "application/pdf")
    }
    data = {
        "organization_id": "11111111-1111-1111-1111-111111111111",
        "uploaded_by": "22222222-2222-2222-2222-222222222222"
    }
    
    try:
        response = requests.post(UPLOAD_URL, files=files, data=data)
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


def poll_document_status(document_id, max_retries=30, interval=2):
    """Poll document status until terminal state is reached."""
    print(f"\nPolling document status for ID: {document_id}")
    
    status_url = f"{API_BASE_URL}/documents/{document_id}/status"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(status_url)
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
    """Main simulation workflow."""
    print("=== GovSwarm Traffic Simulation ===\n")
    
    # Step 1: Simulate upload
    document_id = simulate_upload()
    
    if document_id:
        # Step 2: Poll status until terminal state
        final_status = poll_document_status(document_id)
        
        if final_status:
            print(f"\nFinal Document Status: {final_status}")
        
        # Step 3: Fetch metrics
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
