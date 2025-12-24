#!/usr/bin/env python3
"""
Debug script for lookup table update functionality
"""
import asyncio
import json
from pathlib import Path
from app.services.lookup_table_service import LookupTableService

async def test_lookup_table_update():
    """Test the lookup table update functionality"""
    
    print("🔍 Testing lookup table update functionality...")
    
    # Initialize service
    service = LookupTableService()
    
    # Test field and version
    field_name = "metal_ring_info"
    version = "2020"
    
    print(f"\n📋 Testing field: {field_name} in version {version}")
    
    # Get current lookup table
    print("\n1. Getting current lookup table...")
    current_lookup = await service.get_field_lookup_table(field_name, version)
    
    if current_lookup:
        print(f"✅ Current lookup table found: {current_lookup['name']}")
        print(f"   Current values count: {len(current_lookup['values'])}")
        print(f"   First few values: {current_lookup['values'][:3]}")
    else:
        print("❌ No current lookup table found")
        return
    
    # Create test update data
    print("\n2. Creating test update data...")
    test_lookup_data = {
        "name": current_lookup["name"],
        "description": current_lookup["description"],
        "values": current_lookup["values"] + [
            {"code": "TEST", "meaning": "Test value added by debug script"}
        ]
    }
    
    print(f"   New values count: {len(test_lookup_data['values'])}")
    
    # Update the lookup table
    print("\n3. Updating lookup table...")
    success = await service.update_field_lookup_table(field_name, version, test_lookup_data)
    
    if success:
        print("✅ Update reported as successful")
    else:
        print("❌ Update reported as failed")
        return
    
    # Verify the update
    print("\n4. Verifying update...")
    updated_lookup = await service.get_field_lookup_table(field_name, version)
    
    if updated_lookup:
        print(f"✅ Updated lookup table retrieved")
        print(f"   Updated values count: {len(updated_lookup['values'])}")
        
        # Check if our test value is there
        test_value_found = any(item["code"] == "TEST" for item in updated_lookup["values"])
        if test_value_found:
            print("✅ Test value found in updated lookup table")
        else:
            print("❌ Test value NOT found in updated lookup table")
            
        # Show last few values
        print(f"   Last few values: {updated_lookup['values'][-3:]}")
    else:
        print("❌ Could not retrieve updated lookup table")
    
    # Check the actual JSON file
    print("\n5. Checking JSON file directly...")
    json_file = Path(f"data/euring_versions/versions/euring_{version}.json")
    
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
        
        # Find the field in JSON
        field_found = False
        for field in version_data.get("field_definitions", []):
            if field.get("name") == field_name:
                field_found = True
                valid_values = field.get("valid_values", [])
                print(f"✅ Field found in JSON file")
                print(f"   Valid values count in JSON: {len(valid_values)}")
                
                if "TEST" in valid_values:
                    print("✅ Test value found in JSON file")
                else:
                    print("❌ Test value NOT found in JSON file")
                    print(f"   Current valid_values: {valid_values}")
                break
        
        if not field_found:
            print(f"❌ Field {field_name} not found in JSON file")
    else:
        print(f"❌ JSON file not found: {json_file}")
    
    print("\n🏁 Debug test completed")

if __name__ == "__main__":
    asyncio.run(test_lookup_table_update())