#!/usr/bin/env python3
"""
Test rapido per verificare il fix dell'API
"""
import requests
import json

def test_recognition_api():
    """Test dell'endpoint di riconoscimento"""
    
    url = "http://localhost:8000/api/euring/recognize"
    
    test_data = {
        "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
        "include_analysis": True
    }
    
    try:
        print("🧪 Testing recognition API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend not running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_recognition_api()
    if success:
        print("\n🎉 API fix successful!")
    else:
        print("\n💥 API still has issues")