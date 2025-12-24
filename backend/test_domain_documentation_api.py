#!/usr/bin/env python3
"""
Test script for Domain Documentation API endpoints
Tests the three new endpoints: /domains/list, /domains/{domain}/documentation, /domains/{domain}/examples
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.euring_api import router
from app.models.euring_models import SemanticDomain
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_domains_list():
    """Test /api/euring/domains/list endpoint"""
    print("🧪 Testing /api/euring/domains/list")
    
    response = client.get("/api/euring/domains/list")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['success']}")
        print(f"📊 Total domains: {data['total_domains']}")
        
        if data['domains']:
            print("\n📋 Available domains:")
            for domain in data['domains'][:3]:  # Show first 3
                print(f"  - {domain['name']} ({domain['domain']})")
                print(f"    Description: {domain['description']}")
                print(f"    Fields: {domain['statistics']['total_fields']}")
                print(f"    Stability: {domain['stability_score']}/10")
                print()
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_domain_documentation():
    """Test /api/euring/domains/{domain}/documentation endpoint"""
    print("🧪 Testing /api/euring/domains/species/documentation")
    
    response = client.get("/api/euring/domains/species/documentation")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['success']}")
        print(f"📖 Domain: {data['domain']}")
        
        if data['documentation']:
            doc = data['documentation']
            print(f"\n📋 Domain Info:")
            print(f"  Name: {doc['domain_info']['name']}")
            print(f"  Description: {doc['domain_info']['description']}")
            print(f"  Key Concepts: {', '.join(doc['domain_info']['key_concepts'])}")
            
            print(f"\n📊 Statistics:")
            stats = doc['statistics']
            print(f"  Total versions: {stats['total_versions']}")
            print(f"  Versions with domain: {stats['versions_with_domain']}")
            print(f"  Total fields: {stats['total_fields_across_versions']}")
            
            print(f"\n📚 Usage Guidelines ({len(doc['usage_guidelines'])} items):")
            for guideline in doc['usage_guidelines'][:2]:  # Show first 2
                print(f"  - {guideline}")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_domain_examples():
    """Test /api/euring/domains/{domain}/examples endpoint"""
    print("🧪 Testing /api/euring/domains/identification_marking/examples")
    
    response = client.get("/api/euring/domains/identification_marking/examples")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['success']}")
        print(f"🔍 Domain: {data['domain']}")
        
        if data['examples']:
            examples = data['examples']
            print(f"\n📋 Domain Focus:")
            print(f"  Description: {examples['domain_info']['focus_description']}")
            print(f"  Highlighted Fields: {', '.join(examples['domain_info']['highlighted_fields'])}")
            
            print(f"\n📊 Statistics:")
            stats = examples['statistics']
            print(f"  Versions with examples: {stats['versions_with_examples']}")
            print(f"  Total domain fields: {stats['total_domain_fields']}")
            print(f"  Example coverage: {stats['example_coverage']}%")
            
            print(f"\n📝 Version Examples ({len(examples['version_examples'])} versions):")
            for example in examples['version_examples'][:2]:  # Show first 2
                print(f"  - {example['version_name']} ({example['year']})")
                print(f"    Fields in domain: {example['field_count']}")
                print(f"    Example: {example['example_string'][:50]}...")
            
            print(f"\n🎯 Use Cases ({len(examples['use_cases'])} cases):")
            for use_case in examples['use_cases'][:2]:  # Show first 2
                print(f"  - {use_case['title']}: {use_case['description']}")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_invalid_domain():
    """Test with invalid domain"""
    print("🧪 Testing invalid domain")
    
    response = client.get("/api/euring/domains/invalid_domain/documentation")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Correctly rejected invalid domain")
        return True
    else:
        print(f"❌ Unexpected response: {response.text}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Domain Documentation API Endpoints")
    print("=" * 60)
    
    tests = [
        test_domains_list,
        test_domain_documentation,
        test_domain_examples,
        test_invalid_domain
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print("-" * 60)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
            print("-" * 60)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)