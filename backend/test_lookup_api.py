#!/usr/bin/env python3
"""
Test the lookup table API endpoints directly
"""
import asyncio
import json
from fastapi.testclient import TestClient
from main import app

def test_lookup_api():
    """Test the lookup table API endpoints"""
    
    print("🔍 Testing lookup table API endpoints...")
    
    client = TestClient(app)
    
    # Test field and version
    field_name = "metal_ring_info"
    version = "2020"
    
    print(f"\n📋 Testing field: {field_name} in version {version}")
    
    # Test GET endpoint
    print("\n1. Testing GET lookup table endpoint...")
    response = client.get(f"/api/euring/versions/{version}/field/{field_name}/lookup")
    
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        if data.get('success'):
            lookup_table = data.get('lookup_table')
            print(f"   Lookup table name: {lookup_table.get('name')}")
            print(f"   Values count: {len(lookup_table.get('values', []))}")
        else:
            print(f"   Error: {data.get('error')}")
    else:
        print(f"   Error response: {response.text}")
    
    # Test PUT endpoint
    print("\n2. Testing PUT lookup table endpoint...")
    
    # Create test update data
    update_data = {
        "field_name": field_name,
        "version": version,
        "lookup_data": {
            "name": "Metal Ring Information",
            "description": "Status and type of metal ring",
            "values": [
                {"code": "0", "meaning": "Ring not mentioned"},
                {"code": "1", "meaning": "Ring confirmed present"},
                {"code": "2", "meaning": "Ring confirmed absent"},
                {"code": "NEW", "meaning": "New test value from API"}
            ]
        }
    }
    
    response = client.put(f"/api/euring/versions/{version}/field/{field_name}/lookup", json=update_data)
    
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        if data.get('success'):
            lookup_table = data.get('lookup_table')
            print(f"   Updated lookup table name: {lookup_table.get('name')}")
            print(f"   Updated values count: {len(lookup_table.get('values', []))}")
            
            # Check if our new value is there
            values = lookup_table.get('values', [])
            new_value_found = any(item.get('code') == 'NEW' for item in values)
            print(f"   New value found: {new_value_found}")
        else:
            print(f"   Error: {data.get('error')}")
    else:
        print(f"   Error response: {response.text}")
    
    # Verify the update with another GET
    print("\n3. Verifying update with GET...")
    response = client.get(f"/api/euring/versions/{version}/field/{field_name}/lookup")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            lookup_table = data.get('lookup_table')
            values = lookup_table.get('values', [])
            new_value_found = any(item.get('code') == 'NEW' for item in values)
            print(f"   New value persisted: {new_value_found}")
            print(f"   Final values: {[item.get('code') for item in values]}")
        else:
            print(f"   Error: {data.get('error')}")
    else:
        print(f"   Error response: {response.text}")
    
    print("\n🏁 API test completed")

if __name__ == "__main__":
    test_lookup_api()