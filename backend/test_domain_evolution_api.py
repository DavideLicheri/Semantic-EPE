#!/usr/bin/env python3
"""
Test script for Domain Evolution API endpoints
Tests the three new domain evolution endpoints: evolution, compare, and timeline
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.api.euring_api import router
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_domain_evolution_endpoint():
    """Test the /api/domains/{domain}/evolution endpoint"""
    print("Testing domain evolution endpoint...")
    
    # Test valid domain
    response = client.get("/api/euring/domains/species/evolution")
    print(f"Species evolution status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Domain: {data['domain']}")
        if data['evolution_data']:
            print(f"Evolution entries: {len(data['evolution_data'].get('evolution_entries', []))}")
    else:
        print(f"Error: {response.text}")
    
    # Test invalid domain
    response = client.get("/api/euring/domains/invalid_domain/evolution")
    print(f"Invalid domain status: {response.status_code}")
    assert response.status_code == 400
    
    print("✓ Domain evolution endpoint test completed\n")

def test_domain_comparison_endpoint():
    """Test the /api/domains/{domain}/compare/{version1}/{version2} endpoint"""
    print("Testing domain comparison endpoint...")
    
    # Test valid comparison
    response = client.get("/api/euring/domains/species/compare/1966/2020")
    print(f"Species comparison (1966 vs 2020) status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Domain: {data['domain']}")
        print(f"Versions: {data['version1']} vs {data['version2']}")
        if data['comparison_data']:
            summary = data['comparison_data'].get('summary', {})
            print(f"Total changes: {summary.get('total_changes', 0)}")
            print(f"Compatibility: {summary.get('compatibility_level', 'unknown')}")
    else:
        print(f"Error: {response.text}")
    
    # Test invalid version
    response = client.get("/api/euring/domains/species/compare/1966/invalid")
    print(f"Invalid version status: {response.status_code}")
    assert response.status_code == 400
    
    print("✓ Domain comparison endpoint test completed\n")

def test_domain_timeline_endpoint():
    """Test the /api/domains/timeline endpoint"""
    print("Testing domain timeline endpoint...")
    
    # Test all domains timeline
    response = client.get("/api/euring/domains/timeline")
    print(f"All domains timeline status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        if data['timeline_data']:
            timeline_type = data['timeline_data'].get('type')
            print(f"Timeline type: {timeline_type}")
            if timeline_type == 'all_domains':
                stats = data['timeline_data'].get('overall_statistics', {})
                print(f"Total domains: {stats.get('total_domains', 0)}")
                print(f"Domains with evolution data: {stats.get('domains_with_evolution_data', 0)}")
    else:
        print(f"Error: {response.text}")
    
    # Test specific domain timeline
    response = client.get("/api/euring/domains/timeline?domain=species&include_details=true")
    print(f"Species timeline status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        if data['timeline_data']:
            timeline_type = data['timeline_data'].get('type')
            print(f"Timeline type: {timeline_type}")
            if timeline_type == 'single_domain':
                domain = data['timeline_data'].get('domain')
                timeline = data['timeline_data'].get('timeline', {})
                print(f"Domain: {domain}")
                print(f"Timeline events: {len(timeline.get('timeline_events', []))}")
    else:
        print(f"Error: {response.text}")
    
    print("✓ Domain timeline endpoint test completed\n")

def main():
    """Run all tests"""
    print("=== Domain Evolution API Endpoint Tests ===\n")
    
    try:
        test_domain_evolution_endpoint()
        test_domain_comparison_endpoint()
        test_domain_timeline_endpoint()
        
        print("=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())