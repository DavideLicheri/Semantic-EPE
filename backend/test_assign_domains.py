#!/usr/bin/env python3
"""
Test script to manually assign semantic domains to fields and test the documentation endpoints
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.skos_manager import SKOSManagerImpl
from app.services.version_loader import VersionLoaderService
from app.models.euring_models import SemanticDomain


async def assign_domains_manually():
    """Manually assign semantic domains to fields for testing"""
    print("🔧 Manually assigning semantic domains to fields")
    
    skos_manager = SKOSManagerImpl()
    await skos_manager.load_version_model()
    
    versions = await skos_manager.get_all_versions()
    
    # Manual domain assignments based on field names
    domain_assignments = {
        # IDENTIFICATION_MARKING
        'species_code': SemanticDomain.SPECIES,
        'ring_number': SemanticDomain.IDENTIFICATION_MARKING,
        'scheme': SemanticDomain.IDENTIFICATION_MARKING,
        'scheme_country': SemanticDomain.IDENTIFICATION_MARKING,
        'scheme_code': SemanticDomain.IDENTIFICATION_MARKING,
        'ring_prefix': SemanticDomain.IDENTIFICATION_MARKING,
        'metal_ring_info': SemanticDomain.IDENTIFICATION_MARKING,
        'other_marks': SemanticDomain.IDENTIFICATION_MARKING,
        'verification': SemanticDomain.IDENTIFICATION_MARKING,
        'identification_number': SemanticDomain.IDENTIFICATION_MARKING,
        'ringing_scheme': SemanticDomain.IDENTIFICATION_MARKING,
        'primary_identification_method': SemanticDomain.IDENTIFICATION_MARKING,
        
        # SPECIES
        'finder_species': SemanticDomain.SPECIES,
        'scheme_species': SemanticDomain.SPECIES,
        
        # DEMOGRAPHICS
        'age_code': SemanticDomain.DEMOGRAPHICS,
        'sex_code': SemanticDomain.DEMOGRAPHICS,
        'age': SemanticDomain.DEMOGRAPHICS,
        'sex': SemanticDomain.DEMOGRAPHICS,
        'finder_age': SemanticDomain.DEMOGRAPHICS,
        'scheme_age': SemanticDomain.DEMOGRAPHICS,
        'finder_sex': SemanticDomain.DEMOGRAPHICS,
        'scheme_sex': SemanticDomain.DEMOGRAPHICS,
        
        # TEMPORAL
        'date': SemanticDomain.TEMPORAL,
        'time': SemanticDomain.TEMPORAL,
        'first_date': SemanticDomain.TEMPORAL,
        'current_date': SemanticDomain.TEMPORAL,
        'date_first': SemanticDomain.TEMPORAL,
        'date_current': SemanticDomain.TEMPORAL,
        
        # SPATIAL
        'latitude': SemanticDomain.SPATIAL,
        'longitude': SemanticDomain.SPATIAL,
        'coordinate_accuracy': SemanticDomain.SPATIAL,
        'place_code': SemanticDomain.SPATIAL,
        'region': SemanticDomain.SPATIAL,
        'lat_deg': SemanticDomain.SPATIAL,
        'lat_min': SemanticDomain.SPATIAL,
        'lon_deg': SemanticDomain.SPATIAL,
        'lon_min': SemanticDomain.SPATIAL,
        'lat_dir': SemanticDomain.SPATIAL,
        'lon_dir': SemanticDomain.SPATIAL,
        
        # BIOMETRICS
        'wing_length': SemanticDomain.BIOMETRICS,
        'weight': SemanticDomain.BIOMETRICS,
        'bill_length': SemanticDomain.BIOMETRICS,
        'tarsus_length': SemanticDomain.BIOMETRICS,
        'fat_score': SemanticDomain.BIOMETRICS,
        'muscle_score': SemanticDomain.BIOMETRICS,
        'moult_score': SemanticDomain.BIOMETRICS,
        'wing': SemanticDomain.BIOMETRICS,
        'bill': SemanticDomain.BIOMETRICS,
        'tarsus': SemanticDomain.BIOMETRICS,
        'fat': SemanticDomain.BIOMETRICS,
        'muscle': SemanticDomain.BIOMETRICS,
        'moult': SemanticDomain.BIOMETRICS,
        
        # METHODOLOGY
        'capture_method': SemanticDomain.METHODOLOGY,
        'condition': SemanticDomain.METHODOLOGY,
        'status': SemanticDomain.METHODOLOGY,
        'method': SemanticDomain.METHODOLOGY,
        'circumstances': SemanticDomain.METHODOLOGY,
        'manipulation': SemanticDomain.METHODOLOGY,
        'moved': SemanticDomain.METHODOLOGY,
        'lure': SemanticDomain.METHODOLOGY,
        'catch_method': SemanticDomain.METHODOLOGY,
        'catch_lure': SemanticDomain.METHODOLOGY,
        'catch_moved': SemanticDomain.METHODOLOGY,
    }
    
    # Apply assignments
    total_assigned = 0
    for version in versions:
        print(f"\n📋 Processing {version.name} ({version.id})")
        assigned_count = 0
        
        for field in version.field_definitions:
            # Try exact match first
            if field.name in domain_assignments:
                field.semantic_domain = domain_assignments[field.name]
                assigned_count += 1
            else:
                # Try partial matches
                for field_pattern, domain in domain_assignments.items():
                    if field_pattern in field.name.lower() or field_pattern in field.description.lower():
                        field.semantic_domain = domain
                        assigned_count += 1
                        break
                else:
                    # Default to methodology for unassigned fields
                    field.semantic_domain = SemanticDomain.METHODOLOGY
                    assigned_count += 1
        
        print(f"   Assigned {assigned_count}/{len(version.field_definitions)} fields to domains")
        total_assigned += assigned_count
    
    print(f"\n✅ Total fields assigned: {total_assigned}")
    
    # Show domain distribution
    print("\n📊 Domain distribution:")
    for domain in SemanticDomain:
        count = sum(
            1 for version in versions 
            for field in version.field_definitions 
            if field.semantic_domain == domain
        )
        print(f"   {domain.value}: {count} fields")
    
    return versions


async def test_documentation_endpoints_with_domains():
    """Test the documentation endpoints after assigning domains"""
    print("\n🧪 Testing documentation endpoints with assigned domains")
    
    from app.api.euring_api import get_available_domains, get_domain_documentation, get_domain_examples
    
    # Test domains list
    print("\n1. Testing domains list:")
    response = await get_available_domains()
    if response.success and response.domains:
        for domain in response.domains[:3]:
            print(f"   - {domain['name']}: {domain['statistics']['total_fields']} fields")
    
    # Test domain documentation
    print("\n2. Testing species documentation:")
    response = await get_domain_documentation("species")
    if response.success and response.documentation:
        stats = response.documentation['statistics']
        print(f"   - Total fields: {stats['total_fields_across_versions']}")
        print(f"   - Versions with domain: {stats['versions_with_domain']}")
    
    # Test domain examples
    print("\n3. Testing identification_marking examples:")
    response = await get_domain_examples("identification_marking")
    if response.success and response.examples:
        stats = response.examples['statistics']
        print(f"   - Versions with examples: {stats['versions_with_examples']}")
        print(f"   - Total domain fields: {stats['total_domain_fields']}")


async def main():
    """Main test function"""
    print("🚀 Testing Domain Assignment and Documentation Endpoints")
    print("=" * 70)
    
    try:
        # Assign domains manually
        versions = await assign_domains_manually()
        
        # Test the documentation endpoints
        await test_documentation_endpoints_with_domains()
        
        print("\n🎉 All tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)