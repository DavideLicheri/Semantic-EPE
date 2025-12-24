#!/usr/bin/env python3
"""
Simple test script for Domain Evolution API endpoints
Tests the implementation without requiring additional dependencies
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.euring_api import get_domain_evolution, compare_domain_versions, get_domains_timeline
from app.models.euring_models import SemanticDomain

async def test_domain_evolution():
    """Test the domain evolution endpoint function"""
    print("Testing domain evolution function...")
    
    try:
        # Test valid domain
        result = await get_domain_evolution("species")
        print(f"Species evolution success: {result.success}")
        print(f"Domain: {result.domain}")
        if result.error:
            print(f"Error: {result.error}")
        else:
            print("✓ Domain evolution function works")
    except Exception as e:
        print(f"Error in domain evolution: {e}")
    
    print()

async def test_domain_comparison():
    """Test the domain comparison endpoint function"""
    print("Testing domain comparison function...")
    
    try:
        # Test valid comparison
        result = await compare_domain_versions("species", "1966", "2020")
        print(f"Species comparison success: {result.success}")
        print(f"Domain: {result.domain}")
        print(f"Versions: {result.version1} vs {result.version2}")
        if result.error:
            print(f"Error: {result.error}")
        else:
            print("✓ Domain comparison function works")
    except Exception as e:
        print(f"Error in domain comparison: {e}")
    
    print()

async def test_domain_timeline():
    """Test the domain timeline endpoint function"""
    print("Testing domain timeline function...")
    
    try:
        # Test all domains timeline
        result = await get_domains_timeline()
        print(f"All domains timeline success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")
        else:
            print("✓ Domain timeline function works")
    except Exception as e:
        print(f"Error in domain timeline: {e}")
    
    print()

async def test_semantic_domains():
    """Test that semantic domains are properly defined"""
    print("Testing semantic domains...")
    
    try:
        domains = list(SemanticDomain)
        print(f"Available semantic domains: {len(domains)}")
        for domain in domains:
            print(f"  - {domain.value}")
        print("✓ Semantic domains are properly defined")
    except Exception as e:
        print(f"Error with semantic domains: {e}")
    
    print()

async def main():
    """Run all tests"""
    print("=== Domain Evolution API Implementation Tests ===\n")
    
    await test_semantic_domains()
    await test_domain_evolution()
    await test_domain_comparison()
    await test_domain_timeline()
    
    print("=== All implementation tests completed! ===")

if __name__ == "__main__":
    asyncio.run(main())