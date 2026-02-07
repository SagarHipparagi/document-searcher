"""Test upload with better error reporting"""
import requests

# Test uploading the test file
filepath = 'uploads/iphone17_test.pdf'

with open(filepath, 'rb') as f:
    files = {'files': (filepath, f, 'application/pdf')}
    
    try:
        print("📤 Uploading iphone17_test.pdf to http://localhost:5000/api/upload...")
        response = requests.post('http://localhost:5000/api/upload', files=files, timeout=120)
        
        print(f"\n✓ Status Code: {response.status_code}")
        print(f"✓ Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success: {data.get('success')}")
            print(f"📝 Message: {data.get('message')}")
        else:
            print(f"\n❌ Error response:")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Raw response: {response.text}")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 120 seconds")
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
