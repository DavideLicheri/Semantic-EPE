#!/usr/bin/env python3
"""
Final test of the API endpoints using the actual FastAPI server
"""

import asyncio
import sys
import os
import requests
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Start the server in background and test the endpoints
def test_api_endpoints():
    """Test the API endpoints with HTTP requests"""
    base_url = "http://localhost:8000/api/euring"
    
    print("🧪 Testing Domain Documentation API Endpoints via HTTP")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        ("/domains/list", "Domains List"),
        ("/domains/species/documentation", "Species Documentation"),
        ("/domains/identification_marking/examples", "Identification Marking Examples"),
        ("/domains/invalid_domain/documentation", "Invalid Domain (should fail)")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        print(f"\n🔍 Testing {description}")
        print(f"   Endpoint: GET {endpoint}")
        
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Success")
                    
                    # Show specific details based on endpoint
                    if 'domains' in data:
                        print(f"   📊 Found {data.get('total_domains', 0)} domains")
                    elif 'documentation' in data:
                        stats = data['documentation'].get('statistics', {})
                        print(f"   📖 {stats.get('total_fields_across_versions', 0)} fields across {stats.get('total_versions', 0)} versions")
                    elif 'examples' in data:
                        stats = data['examples'].get('statistics', {})
                        print(f"   📝 {stats.get('total_domain_fields', 0)} domain fields, {stats.get('versions_with_examples', 0)} versions with examples")
                    
                    results.append(True)
                else:
                    print(f"   ❌ API returned success=false: {data.get('error', 'Unknown error')}")
                    results.append(False)
            elif response.status_code == 400 and "invalid_domain" in endpoint:
                print(f"   ✅ Correctly rejected invalid domain")
                results.append(True)
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Error text: {response.text[:200]}")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            results.append(False)
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} endpoints working correctly")
    
    if passed == total:
        print("🎉 All API endpoints are working!")
        return True
    else:
        print("⚠️  Some endpoints have issues")
        return False


def check_server_running():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8000/api/euring/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main test function"""
    print("🚀 Testing Domain Documentation API Endpoints")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Server is not running on localhost:8000")
        print("   Please start the server with: python3 main.py")
        print("   Then run this test again.")
        return 1
    
    print("✅ Server is running")
    
    # Test the endpoints
    success = test_api_endpoints()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)