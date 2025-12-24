#!/usr/bin/env python3
"""
Simple test script for Domain Documentation API endpoints
Tests the endpoint functions directly without HTTP client
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.euring_api import get_available_domains, get_domain_documentation, get_domain_examples


async def test_domains_list():
    """Test get_available_domains function"""
    print("🧪 Testing get_available_domains()")
    
    try:
        response = await get_available_domains()
        
        print(f"✅ Success: {response.success}")
        print(f"📊 Total domains: {response.total_domains}")
        
        if response.domains:
            print("\n📋 Available domains:")
            for domain in response.domains[:3]:  # Show first 3
                print(f"  - {domain['name']} ({domain['domain']})")
                print(f"    Description: {domain['description']}")
                print(f"    Fields: {domain['statistics']['total_fields']}")
                print(f"    Stability: {domain['stability_score']}/10")
                print()
        
        return response.success
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_domain_documentation():
    """Test get_domain_documentation function"""
    print("🧪 Testing get_domain_documentation('species')")
    
    try:
        response = await get_domain_documentation("species")
        
        print(f"✅ Success: {response.success}")
        print(f"📖 Domain: {response.domain}")
        
        if response.documentation:
            doc = response.documentation
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
        
        return response.success
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_domain_examples():
    """Test get_domain_examples function"""
    print("🧪 Testing get_domain_examples('identification_marking')")
    
    try:
        response = await get_domain_examples("identification_marking")
        
        print(f"✅ Success: {response.success}")
        print(f"🔍 Domain: {response.domain}")
        
        if response.examples:
            examples = response.examples
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
        
        return response.success
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_invalid_domain():
    """Test with invalid domain"""
    print("🧪 Testing invalid domain")
    
    try:
        response = await get_domain_documentation("invalid_domain")
        
        if not response.success and response.error:
            print(f"✅ Correctly rejected invalid domain: {response.error}")
            return True
        else:
            print(f"❌ Should have rejected invalid domain")
            return False
    except Exception as e:
        # HTTPException is expected for invalid domain
        if "Invalid domain" in str(e):
            print(f"✅ Correctly rejected invalid domain with exception")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False


async def main():
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
            result = await test()
            results.append(result)
            print("-" * 60)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
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
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
