#!/usr/bin/env python3
"""
Test for Domain Analysis API Endpoints
Tests the three new endpoints: fields, compatibility, and export
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)


def test_domain_fields_endpoint():
    """Test /api/euring/domains/{domain}/fields endpoint"""
    print("=== TEST DOMAIN FIELDS ENDPOINT ===")
    
    # Test with valid domain
    domain = "identification_marking"
    response = client.get(f"/api/euring/domains/{domain}/fields")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Domain fields endpoint funzionante")
        print(f"  Domain: {data.get('domain')}")
        print(f"  Success: {data.get('success')}")
        print(f"  Field groups: {len(data.get('field_groups', []))}")
        print(f"  Processing time: {data.get('processing_time_ms')}ms")
        
        # Check semantic analysis
        semantic_analysis = data.get('semantic_analysis', {})
        if semantic_analysis:
            print(f"  Total fields analyzed: {semantic_analysis.get('total_fields', 0)}")
            print(f"  Versions analyzed: {semantic_analysis.get('versions_analyzed', 0)}")
    else:
        print(f"✗ Domain fields endpoint fallito: {response.text}")
    
    print()


def test_domain_compatibility_endpoint():
    """Test /api/euring/domains/{domain}/compatibility/{fromVersion}/{toVersion} endpoint"""
    print("=== TEST DOMAIN COMPATIBILITY ENDPOINT ===")
    
    # Test with valid parameters
    domain = "species"
    from_version = "1966"
    to_version = "2020"
    
    response = client.get(f"/api/euring/domains/{domain}/compatibility/{from_version}/{to_version}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Domain compatibility endpoint funzionante")
        print(f"  Domain: {data.get('domain')}")
        print(f"  From version: {data.get('from_version')}")
        print(f"  To version: {data.get('to_version')}")
        print(f"  Success: {data.get('success')}")
        print(f"  Processing time: {data.get('processing_time_ms')}ms")
        
        # Check compatibility data
        compatibility_data = data.get('compatibility_data', {})
        if compatibility_data:
            summary = compatibility_data.get('summary', {})
            print(f"  Overall compatibility: {summary.get('overall_compatibility')}")
            print(f"  Is lossy conversion: {summary.get('is_lossy_conversion')}")
            print(f"  Total warnings: {summary.get('total_warnings', 0)}")
    else:
        print(f"✗ Domain compatibility endpoint fallito: {response.text}")
    
    print()


def test_domain_export_endpoint():
    """Test /api/euring/domains/export/{domain} endpoint"""
    print("=== TEST DOMAIN EXPORT ENDPOINT ===")
    
    # Test with valid domain and parameters
    domain = "temporal"
    params = {
        "format": "json",
        "include_evolution": "true",
        "include_field_analysis": "true",
        "include_compatibility": "false"  # Skip compatibility to speed up test
    }
    
    response = client.get(f"/api/euring/domains/export/{domain}", params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Domain export endpoint funzionante")
        print(f"  Domain: {data.get('domain')}")
        print(f"  Success: {data.get('success')}")
        print(f"  Export format: {data.get('export_format')}")
        print(f"  Processing time: {data.get('processing_time_ms')}ms")
        
        # Check export data
        export_data = data.get('export_data', {})
        if export_data:
            metadata = export_data.get('export_metadata', {})
            print(f"  Versions included: {len(metadata.get('versions_included', []))}")
            print(f"  Export timestamp: {metadata.get('export_timestamp', 'N/A')}")
            
            # Check included sections
            if 'evolution_data' in export_data:
                print("  ✓ Evolution data included")
            if 'field_analysis' in export_data:
                print("  ✓ Field analysis included")
            if 'compatibility_data' in export_data:
                print("  ✓ Compatibility data included")
    else:
        print(f"✗ Domain export endpoint fallito: {response.text}")
    
    print()


def test_invalid_domain():
    """Test endpoints with invalid domain"""
    print("=== TEST INVALID DOMAIN ===")
    
    invalid_domain = "invalid_domain"
    response = client.get(f"/api/euring/domains/{invalid_domain}/fields")
    print(f"Status for invalid domain: {response.status_code}")
    
    if response.status_code == 400:
        print("✓ Invalid domain correctly rejected")
        data = response.json()
        print(f"  Error message: {data.get('detail')}")
    else:
        print(f"✗ Invalid domain not handled correctly: {response.text}")
    
    print()


def test_invalid_version():
    """Test compatibility endpoint with invalid version"""
    print("=== TEST INVALID VERSION ===")
    
    domain = "species"
    invalid_version = "1999"
    to_version = "2020"
    
    response = client.get(f"/api/euring/domains/{domain}/compatibility/{invalid_version}/{to_version}")
    print(f"Status for invalid version: {response.status_code}")
    
    if response.status_code == 400:
        print("✓ Invalid version correctly rejected")
        data = response.json()
        print(f"  Error message: {data.get('detail')}")
    else:
        print(f"✗ Invalid version not handled correctly: {response.text}")
    
    print()


def run_all_tests():
    """Run all domain analysis API tests"""
    print("🧪 TESTING DOMAIN ANALYSIS API ENDPOINTS")
    print("=" * 50)
    
    test_domain_fields_endpoint()
    test_domain_compatibility_endpoint()
    test_domain_export_endpoint()
    test_invalid_domain()
    test_invalid_version()
    
    print("=" * 50)
    print("✅ Domain Analysis API tests completed")


if __name__ == "__main__":
    run_all_tests()