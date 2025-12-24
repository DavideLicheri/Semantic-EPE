#!/usr/bin/env python3
"""
Final test script for Domain Documentation API endpoints
This script assigns domains to fields and then tests all three endpoints
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.skos_manager import SKOSManagerImpl
from app.models.euring_models import SemanticDomain
from app.api.euring_api import get_available_domains, get_domain_documentation, get_domain_examples


class DomainAssigner:
    """Helper class to assign semantic domains to fields"""
    
    def __init__(self):
        self.domain_assignments = {
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
    
    def assign_domain_to_field(self, field):
        """Assign semantic domain to a field based on name and description"""
        # Try exact match first
        if field.name in self.domain_assignments:
            return self.domain_assignments[field.name]
        
        # Try partial matches in field name
        field_name_lower = field.name.lower()
        for pattern, domain in self.domain_assignments.items():
            if pattern in field_name_lower:
                return domain
        
        # Try partial matches in description
        if field.description:
            field_desc_lower = field.description.lower()
            for pattern, domain in self.domain_assignments.items():
                if pattern in field_desc_lower:
                    return domain
        
        # Pattern-based assignment
        if any(word in field_name_lower for word in ['ring', 'scheme', 'mark', 'metal', 'verify']):
            return SemanticDomain.IDENTIFICATION_MARKING
        elif any(word in field_name_lower for word in ['species', 'code']):
            return SemanticDomain.SPECIES
        elif any(word in field_name_lower for word in ['age', 'sex', 'adult', 'juvenile']):
            return SemanticDomain.DEMOGRAPHICS
        elif any(word in field_name_lower for word in ['date', 'time', 'current', 'first']):
            return SemanticDomain.TEMPORAL
        elif any(word in field_name_lower for word in ['lat', 'lon', 'coordinate', 'accuracy', 'place']):
            return SemanticDomain.SPATIAL
        elif any(word in field_name_lower for word in ['wing', 'weight', 'bill', 'tarsus', 'fat', 'muscle']):
            return SemanticDomain.BIOMETRICS
        else:
            return SemanticDomain.METHODOLOGY


async def setup_domains_and_test():
    """Setup domain assignments and test all endpoints"""
    print("🚀 Setting up domain assignments and testing endpoints")
    print("=" * 70)
    
    # Create a global SKOS manager instance
    global_skos_manager = SKOSManagerImpl()
    
    # Monkey patch the API endpoints to use our configured SKOS manager
    import app.api.euring_api as api_module
    api_module.skos_manager = global_skos_manager
    
    # Load the version model
    await global_skos_manager.load_version_model()
    versions = await global_skos_manager.get_all_versions()
    
    # Assign domains to fields
    print("🔧 Assigning semantic domains to fields...")
    assigner = DomainAssigner()
    total_assigned = 0
    
    for version in versions:
        assigned_count = 0
        for field in version.field_definitions:
            if not field.semantic_domain:  # Only assign if not already assigned
                field.semantic_domain = assigner.assign_domain_to_field(field)
                assigned_count += 1
        
        print(f"   {version.name}: {assigned_count}/{len(version.field_definitions)} fields assigned")
        total_assigned += assigned_count
    
    print(f"✅ Total fields assigned: {total_assigned}")
    
    # Show domain distribution
    print("\n📊 Domain distribution:")
    for domain in SemanticDomain:
        count = sum(
            1 for version in versions 
            for field in version.field_definitions 
            if field.semantic_domain == domain
        )
        print(f"   {domain.value}: {count} fields")
    
    # Test the endpoints
    print("\n🧪 Testing Domain Documentation API Endpoints")
    print("-" * 50)
    
    # Test 1: Domains list
    print("\n1. Testing /api/euring/domains/list")
    try:
        response = await get_available_domains()
        if response.success and response.domains:
            print(f"✅ Success: Found {response.total_domains} domains")
            for domain in response.domains[:3]:
                print(f"   - {domain['name']}: {domain['statistics']['total_fields']} fields")
        else:
            print(f"❌ Failed: {response.error}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Domain documentation
    print("\n2. Testing /api/euring/domains/species/documentation")
    try:
        response = await get_domain_documentation("species")
        if response.success and response.documentation:
            stats = response.documentation['statistics']
            print(f"✅ Success: {stats['total_fields_across_versions']} total fields")
            print(f"   Versions with domain: {stats['versions_with_domain']}")
            print(f"   Usage guidelines: {len(response.documentation['usage_guidelines'])}")
        else:
            print(f"❌ Failed: {response.error}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Domain examples
    print("\n3. Testing /api/euring/domains/identification_marking/examples")
    try:
        response = await get_domain_examples("identification_marking")
        if response.success and response.examples:
            stats = response.examples['statistics']
            print(f"✅ Success: {stats['total_domain_fields']} domain fields")
            print(f"   Versions with examples: {stats['versions_with_examples']}")
            print(f"   Use cases: {len(response.examples['use_cases'])}")
        else:
            print(f"❌ Failed: {response.error}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Invalid domain
    print("\n4. Testing invalid domain handling")
    try:
        response = await get_domain_documentation("invalid_domain")
        if not response.success:
            print("✅ Correctly rejected invalid domain")
        else:
            print("❌ Should have rejected invalid domain")
    except Exception as e:
        if "Invalid domain" in str(e):
            print("✅ Correctly rejected invalid domain with exception")
        else:
            print(f"❌ Unexpected error: {e}")
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(setup_domains_and_test())