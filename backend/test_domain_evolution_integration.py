#!/usr/bin/env python3
"""
Integration test for Domain Evolution API endpoints
Tests the complete functionality of the three new endpoints
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.euring_api import get_domain_evolution, compare_domain_versions, get_domains_timeline
from app.models.euring_models import SemanticDomain
from app.services.skos_manager import SKOSManagerImpl

async def test_integration():
    """Test the complete integration of domain evolution endpoints"""
    print("=== Domain Evolution API Integration Test ===\n")
    
    # Initialize SKOS manager to ensure data is loaded
    print("1. Initializing SKOS Manager...")
    skos_manager = SKOSManagerImpl()
    try:
        await skos_manager.load_version_model()
        versions = await skos_manager.get_all_versions()
        print(f"   ✓ Loaded {len(versions)} EURING versions")
        
        domains = await skos_manager.get_semantic_domains()
        print(f"   ✓ Found {len(domains)} semantic domains")
        
    except Exception as e:
        print(f"   ✗ Error loading SKOS data: {e}")
    
    print()
    
    # Test 1: Domain Evolution Endpoint
    print("2. Testing Domain Evolution Endpoint...")
    for domain in ["species", "temporal", "spatial"]:
        try:
            result = await get_domain_evolution(domain)
            print(f"   Domain '{domain}': Success={result.success}")
            if result.error:
                print(f"     Error: {result.error}")
            if result.evolution_data:
                entries = result.evolution_data.get('evolution_entries', [])
                print(f"     Evolution entries: {len(entries)}")
        except Exception as e:
            print(f"   Domain '{domain}': Exception - {e}")
    
    print()
    
    # Test 2: Domain Comparison Endpoint
    print("3. Testing Domain Comparison Endpoint...")
    test_comparisons = [
        ("species", "1966", "2020"),
        ("temporal", "1979", "2000"),
        ("spatial", "1966", "1979")
    ]
    
    for domain, v1, v2 in test_comparisons:
        try:
            result = await compare_domain_versions(domain, v1, v2)
            print(f"   {domain} ({v1} vs {v2}): Success={result.success}")
            if result.error:
                print(f"     Error: {result.error}")
            if result.comparison_data:
                summary = result.comparison_data.get('summary', {})
                print(f"     Changes: {summary.get('total_changes', 0)}")
                print(f"     Compatibility: {summary.get('compatibility_level', 'unknown')}")
        except Exception as e:
            print(f"   {domain} ({v1} vs {v2}): Exception - {e}")
    
    print()
    
    # Test 3: Domain Timeline Endpoint
    print("4. Testing Domain Timeline Endpoint...")
    
    # Test all domains timeline
    try:
        result = await get_domains_timeline()
        print(f"   All domains timeline: Success={result.success}")
        if result.error:
            print(f"     Error: {result.error}")
        if result.timeline_data:
            timeline_type = result.timeline_data.get('type')
            print(f"     Timeline type: {timeline_type}")
            if timeline_type == 'all_domains':
                stats = result.timeline_data.get('overall_statistics', {})
                print(f"     Total domains: {stats.get('total_domains', 0)}")
    except Exception as e:
        print(f"   All domains timeline: Exception - {e}")
    
    # Test specific domain timeline
    try:
        result = await get_domains_timeline(domain="species", include_details=True)
        print(f"   Species timeline: Success={result.success}")
        if result.error:
            print(f"     Error: {result.error}")
        if result.timeline_data:
            timeline_type = result.timeline_data.get('type')
            print(f"     Timeline type: {timeline_type}")
    except Exception as e:
        print(f"   Species timeline: Exception - {e}")
    
    print()
    
    # Test 4: Error Handling
    print("5. Testing Error Handling...")
    
    # Test invalid domain
    try:
        result = await get_domain_evolution("invalid_domain")
        print(f"   Invalid domain: Success={result.success}")
        if not result.success:
            print(f"     ✓ Properly handled invalid domain")
    except Exception as e:
        print(f"   Invalid domain: Exception - {e}")
    
    # Test invalid versions
    try:
        result = await compare_domain_versions("species", "invalid", "2020")
        print(f"   Invalid version: Success={result.success}")
        if not result.success:
            print(f"     ✓ Properly handled invalid version")
    except Exception as e:
        print(f"   Invalid version: Exception - {e}")
    
    print()
    print("=== Integration test completed ===")

if __name__ == "__main__":
    asyncio.run(test_integration())