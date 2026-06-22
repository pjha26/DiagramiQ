import time
import requests
import os
import zipfile
import json

def test_flow():
    BASE_URL = 'http://localhost:8000'
    
    # Try both endpoints just in case
    upload_url = f"{BASE_URL}/api/upload"
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print("Server is running.")
    except requests.exceptions.ConnectionError:
        print("Server is NOT running. Please start the server on port 8000 first.")
        return

    # 1. Upload file
    with open('Code Breaker.pdf', 'rb') as f:
        files = {'file': ('Code Breaker.pdf', f, 'application/pdf')}
        print(f"Uploading Code Breaker.pdf to {upload_url}...")
        resp = requests.post(upload_url, files=files)
        if resp.status_code == 404:
            upload_url = f"{BASE_URL}/api/api/upload"
            print(f"Retrying upload at {upload_url}...")
            f.seek(0)
            resp = requests.post(upload_url, files=files)
        
        resp.raise_for_status()
        data = resp.json()
        job_id = data['job_id']
        print(f"Upload successful. Job ID: {job_id}")

    # 2. Wait for completion and get export
    export_url = f"{BASE_URL}/api/export/{job_id}"
    print(f"Waiting for job {job_id} to complete (polling {export_url})...")
    max_retries = 60
    for i in range(max_retries):
        time.sleep(2)
        resp = requests.get(export_url)
        if resp.status_code == 200:
            print("Job completed!")
            print(json.dumps(resp.json(), indent=2))
            break
        elif resp.status_code == 404:
            print("Still processing... 404 No symbols found")
        elif resp.status_code == 500:
             print("500 Server error. Something went wrong.")
             print(resp.text)
             break
        else:
            print(f"Unexpected status: {resp.status_code}")
            print(resp.text)
    else:
        print("Timeout waiting for job completion.")

    # 3. Create ZIP
    print("Creating DiagramIQ.zip...")
    zip_filename = 'DiagramIQ.zip'
    exclude_dirs = {'.venv', '__pycache__', 'redis', '.git'}
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files_list in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files_list:
                if file == zip_filename or file == 'test_flow.py' or file.endswith('.log'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)

    size_bytes = os.path.getsize(zip_filename)
    size_mb = size_bytes / (1024 * 1024)
    print(f"\nZIP ready: {zip_filename}")
    print(f"File size: {size_mb:.2f} MB")

if __name__ == '__main__':
    test_flow()
