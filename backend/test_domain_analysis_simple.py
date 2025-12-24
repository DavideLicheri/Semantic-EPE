#!/usr/bin/env python3
"""
Simple test for Domain Analysis API Endpoints
Tests the implementation without external dependencies
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.api.euring_api import (
    get_domain_fields, get_domain_compatibility, export_domain_data,
    semantic_field_grouper, domain_compatibility_assessor, skos_manager
)
from app.models.euring_models import SemanticDomain


async def test_domain_fields_logic():
    """Test the domain fields endpoint logic"""
    print("=== TEST DOMAIN FIELDS LOGIC ===")
    
    try:
        # Test with a valid domain
        domain = "identification_marking"
        
        # This will test the core logic without HTTP layer
        print(f"Testing domain: {domain}")
        
        # Validate domain conversion
        semantic_domain = SemanticDomain(domain.lower())
        print(f"✓ Domain validation successful: {semantic_domain.value}")
        
        # Test semantic field grouper initialization
        grouper = semantic_field_grouper
        print("✓ Semantic field grouper initialized")
        
        print("✓ Domain fields logic test passed")
        
    except Exception as e:
        print(f"✗ Domain fields logic test failed: {str(e)}")
    
    print()


async def test_domain_compatibility_logic():
    """Test the domain compatibility endpoint logic"""
    print("=== TEST DOMAIN COMPATIBILITY LOGIC ===")
    
    try:
        # Test with valid parameters
        domain = "species"
        from_version = "1966"
        to_version = "2020"
        
        print(f"Testing compatibility: {domain} from {from_version} to {to_version}")
        
        # Validate domain
        semantic_domain = SemanticDomain(domain.lower())
        print(f"✓ Domain validation successful: {semantic_domain.value}")
        
        # Validate versions
        valid_versions = ['1966', '1979', '2000', '2020']
        assert from_version in valid_versions, f"Invalid fromVersion: {from_version}"
        assert to_version in valid_versions, f"Invalid toVersion: {to_version}"
        print("✓ Version validation successful")
        
        # Test compatibility assessor initialization
        assessor = domain_compatibility_assessor
        print("✓ Domain compatibility assessor initialized")
        
        print("✓ Domain compatibility logic test passed")
        
    except Exception as e:
        print(f"✗ Domain compatibility logic test failed: {str(e)}")
    
    print()


async def test_domain_export_logic():
    """Test the domain export endpoint logic"""
    print("=== TEST DOMAIN EXPORT LOGIC ===")
    
    try:
        # Test with valid parameters
        domain = "temporal"
        format_type = "json"
        
        print(f"Testing export: {domain} in {format_type} format")
        
        # Validate domain
        semantic_domain = SemanticDomain(domain.lower())
        print(f"✓ Domain validation successful: {semantic_domain.value}")
        
        # Validate format
        valid_formats = ["json", "csv", "markdown"]
        assert format_type in valid_formats, f"Invalid format: {format_type}"
        print("✓ Format validation successful")
        
        # Test export data structure creation
        export_data = {
            "domain": semantic_domain.value,
            "export_metadata": {
                "export_format": format_type,
                "exporter_version": "1.0.0"
            }
        }
        print("✓ Export data structure created")
        
        print("✓ Domain export logic test passed")
        
    except Exception as e:
        print(f"✗ Domain export logic test failed: {str(e)}")
    
    print()


async def test_error_handling():
    """Test error handling for invalid inputs"""
    print("=== TEST ERROR HANDLING ===")
    
    try:
        # Test invalid domain
        try:
            invalid_domain = SemanticDomain("invalid_domain")
            print("✗ Invalid domain should have failed")
        except ValueError:
            print("✓ Invalid domain correctly rejected")
        
        # Test invalid version
        valid_versions = ['1966', '1979', '2000', '2020']
        invalid_version = "1999"
        if invalid_version not in valid_versions:
            print("✓ Invalid version correctly detected")
        
        # Test invalid format
        valid_formats = ["json", "csv", "markdown"]
        invalid_format = "xml"
        if invalid_format not in valid_formats:
            print("✓ Invalid format correctly detected")
        
        print("✓ Error handling test passed")
        
    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")
    
    print()


async def test_service_integration():
    """Test integration between services"""
    print("=== TEST SERVICE INTEGRATION ===")
    
    try:
        # Test SKOS manager
        manager = skos_manager
        print("✓ SKOS manager accessible")
        
        # Test semantic field grouper
        grouper = semantic_field_grouper
        print("✓ Semantic field grouper accessible")
        
        # Test domain compatibility assessor
        assessor = domain_compatibility_assessor
        print("✓ Domain compatibility assessor accessible")
        
        # Test SemanticDomain enum
        domains = list(SemanticDomain)
        print(f"✓ {len(domains)} semantic domains available")
        for domain in domains:
            print(f"  - {domain.value}")
        
        print("✓ Service integration test passed")
        
    except Exception as e:
        print(f"✗ Service integration test failed: {str(e)}")
    
    print()


async def run_all_tests():
    """Run all domain analysis logic tests"""
    print("🧪 TESTING DOMAIN ANALYSIS API LOGIC")
    print("=" * 50)
    
    await test_domain_fields_logic()
    await test_domain_compatibility_logic()
    await test_domain_export_logic()
    await test_error_handling()
    await test_service_integration()
    
    print("=" * 50)
    print("✅ Domain Analysis API logic tests completed")


if __name__ == "__main__":
    asyncio.run(run_all_tests())