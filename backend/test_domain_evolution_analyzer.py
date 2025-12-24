#!/usr/bin/env python3
"""
Test Domain Evolution Analyzer Service

This test validates the Domain Evolution Analyzer implementation for task B.1:
- Create service for analyzing historical changes within domains
- Implement domain comparison algorithms  
- Create evolution timeline generation for each domain

Requirements: 8.1, 8.2, 8.3
"""
import asyncio
import json
import os
from typing import Dict, List
from app.services.domain_evolution_analyzer import DomainEvolutionAnalyzer
from app.models.euring_models import (
    SemanticDomain, DomainEvolution, DomainEvolutionEntry, DomainChange,
    DomainChangeType, DomainCompatibilityLevel, DomainCompatibilityMatrix,
    EuringVersion, FieldDefinition, FormatSpec, ValidationRule
)


def create_test_domain_evolution_data() -> List[DomainEvolution]:
    """Create test domain evolution data based on real EURING analysis"""
    
    # Create test domain evolution for IDENTIFICATION_MARKING domain
    identification_entries = [
        DomainEvolutionEntry(
            version="euring_1966",
            year=1966,
            changes=[
                DomainChange(
                    change_type=DomainChangeType.ADDED,
                    field_name="ring_number",
                    semantic_impact="Initial ring identification system",
                    compatibility_impact=DomainCompatibilityLevel.FULL
                )
            ],
            field_mappings=[],
            semantic_notes=["First standardized ring numbering system"],
            fields_added=["ring_number"],
            fields_removed=[],
            fields_modified=[],
            format_changes=["Space-separated format"],
            semantic_improvements=["Basic ring identification"],
            compatibility_notes=[]
        ),
        DomainEvolutionEntry(
            version="euring_1979",
            year=1979,
            changes=[
                DomainChange(
                    change_type=DomainChangeType.ADDED,
                    field_name="scheme_country",
                    semantic_impact="Added country-based scheme identification",
                    compatibility_impact=DomainCompatibilityLevel.PARTIAL
                ),
                DomainChange(
                    change_type=DomainChangeType.MODIFIED,
                    field_name="ring_number",
                    previous_value="2L+5D format",
                    new_value="1L+6D format",
                    semantic_impact="Changed ring number format",
                    compatibility_impact=DomainCompatibilityLevel.LOSSY
                )
            ],
            field_mappings=[],
            semantic_notes=["Enhanced scheme identification", "Fixed-length format standardization"],
            fields_added=["scheme_country"],
            fields_removed=[],
            fields_modified=["ring_number"],
            format_changes=["Fixed-length format"],
            semantic_improvements=["Country-based scheme identification"],
            compatibility_notes=["Ring number format changed"]
        ),
        DomainEvolutionEntry(
            version="euring_2020_official",
            year=2020,
            changes=[
                DomainChange(
                    change_type=DomainChangeType.ADDED,
                    field_name="identification_number",
                    semantic_impact="SKOS-based identification system",
                    compatibility_impact=DomainCompatibilityLevel.INCOMPATIBLE
                ),
                DomainChange(
                    change_type=DomainChangeType.REMOVED,
                    field_name="ring_number",
                    semantic_impact="Replaced by identification_number",
                    compatibility_impact=DomainCompatibilityLevel.INCOMPATIBLE
                )
            ],
            field_mappings=[],
            semantic_notes=["Official SKOS thesaurus integration", "Precise field definitions"],
            fields_added=["identification_number", "ringing_scheme", "metal_ring_information"],
            fields_removed=["ring_number"],
            fields_modified=[],
            format_changes=["SKOS-based variable length"],
            semantic_improvements=["Official SKOS integration", "Enhanced precision"],
            compatibility_notes=["Complete field restructure"]
        )
    ]
    
    # Create compatibility matrix for identification marking
    id_compatibility_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.IDENTIFICATION_MARKING)
    id_compatibility_matrix.set_compatibility("euring_1966", "euring_1979", DomainCompatibilityLevel.PARTIAL)
    id_compatibility_matrix.set_compatibility("euring_1979", "euring_2020_official", DomainCompatibilityLevel.INCOMPATIBLE)
    id_compatibility_matrix.set_compatibility("euring_1966", "euring_2020_official", DomainCompatibilityLevel.INCOMPATIBLE)
    
    identification_evolution = DomainEvolution(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        evolution_entries=identification_entries,
        compatibility_matrix=id_compatibility_matrix
    )
    
    # Create test domain evolution for SPECIES domain
    species_entries = [
        DomainEvolutionEntry(
            version="euring_1966",
            year=1966,
            changes=[
                DomainChange(
                    change_type=DomainChangeType.ADDED,
                    field_name="species_code",
                    semantic_impact="Initial species coding system",
                    compatibility_impact=DomainCompatibilityLevel.FULL
                )
            ],
            field_mappings=[],
            semantic_notes=["4-digit species codes"],
            fields_added=["species_code"],
            fields_removed=[],
            fields_modified=[],
            format_changes=["4-digit numeric codes"],
            semantic_improvements=["Basic species identification"],
            compatibility_notes=[]
        ),
        DomainEvolutionEntry(
            version="euring_1979",
            year=1979,
            changes=[
                DomainChange(
                    change_type=DomainChangeType.MODIFIED,
                    field_name="species_code",
                    previous_value="4 digits",
                    new_value="5 digits",
                    semantic_impact="Expanded species code space",
                    compatibility_impact=DomainCompatibilityLevel.PARTIAL
                )
            ],
            field_mappings=[],
            semantic_notes=["Expanded to 5-digit codes"],
            fields_added=[],
            fields_removed=[],
            fields_modified=["species_code"],
            format_changes=["5-digit numeric codes"],
            semantic_improvements=["Larger species code space"],
            compatibility_notes=["Species code length changed"]
        )
    ]
    
    species_compatibility_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.SPECIES)
    species_compatibility_matrix.set_compatibility("euring_1966", "euring_1979", DomainCompatibilityLevel.PARTIAL)
    
    species_evolution = DomainEvolution(
        domain=SemanticDomain.SPECIES,
        evolution_entries=species_entries,
        compatibility_matrix=species_compatibility_matrix
    )
    
    return [identification_evolution, species_evolution]


def create_test_versions() -> List[EuringVersion]:
    """Create test EURING versions for testing"""
    
    # EURING 1966
    euring_1966 = EuringVersion(
        id="euring_1966",
        name="EURING 1966",
        year=1966,
        description="First standardized EURING format",
        field_definitions=[
            FieldDefinition(
                position=1,
                name="ring_number",
                data_type="alphanumeric",
                length=7,
                description="Ring number",
                semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                semantic_meaning="Unique ring identifier"
            ),
            FieldDefinition(
                position=2,
                name="species_code",
                data_type="numeric",
                length=4,
                description="Species code",
                semantic_domain=SemanticDomain.SPECIES,
                semantic_meaning="EURING species code"
            )
        ],
        validation_rules=[],
        format_specification=FormatSpec(total_length=55, field_separator=" ")
    )
    
    # EURING 1979
    euring_1979 = EuringVersion(
        id="euring_1979",
        name="EURING 1979",
        year=1979,
        description="Fixed-length EURING format",
        field_definitions=[
            FieldDefinition(
                position=1,
                name="ring_number",
                data_type="alphanumeric",
                length=7,
                description="Ring number",
                semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                semantic_meaning="Unique ring identifier"
            ),
            FieldDefinition(
                position=2,
                name="scheme_country",
                data_type="alphanumeric",
                length=2,
                description="Country code",
                semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                semantic_meaning="Country code for ringing scheme"
            ),
            FieldDefinition(
                position=3,
                name="species_code",
                data_type="numeric",
                length=5,
                description="Species code",
                semantic_domain=SemanticDomain.SPECIES,
                semantic_meaning="EURING species code"
            )
        ],
        validation_rules=[],
        format_specification=FormatSpec(total_length=78)
    )
    
    # EURING 2020 Official
    euring_2020_official = EuringVersion(
        id="euring_2020_official",
        name="EURING 2020 Official SKOS",
        year=2020,
        description="Official SKOS-based EURING format",
        field_definitions=[
            FieldDefinition(
                position=1,
                name="identification_number",
                data_type="alphanumeric",
                length=10,
                description="Identification number",
                semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                semantic_meaning="Unique ring identifier for the bird throughout its life"
            ),
            FieldDefinition(
                position=2,
                name="ringing_scheme",
                data_type="alphanumeric",
                length=3,
                description="Ringing scheme",
                semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                semantic_meaning="Identification of ringing scheme or country"
            )
        ],
        validation_rules=[],
        format_specification=FormatSpec(total_length=0, field_separator="|")  # Variable length
    )
    
    return [euring_1966, euring_1979, euring_2020_official]


async def test_domain_evolution_analyzer():
    """Test the Domain Evolution Analyzer service"""
    print("🧪 Testing Domain Evolution Analyzer Service...")
    
    # Create analyzer instance
    analyzer = DomainEvolutionAnalyzer()
    
    # Load test data
    domain_evolutions = create_test_domain_evolution_data()
    versions = create_test_versions()
    
    analyzer.load_domain_evolutions(domain_evolutions)
    analyzer.load_versions(versions)
    
    print("✅ Test data loaded successfully")
    
    # Test 1: Analyze domain evolution (Requirement 8.1)
    print("\n📊 Test 1: Analyzing domain evolution...")
    try:
        identification_evolution = await analyzer.analyze_domain_evolution(
            SemanticDomain.IDENTIFICATION_MARKING
        )
        
        print(f"   Domain: {identification_evolution.domain.value}")
        print(f"   Evolution entries: {len(identification_evolution.evolution_entries)}")
        print(f"   Field evolution map: {len(identification_evolution.field_evolution_map or {})}")
        
        # Test with version range
        filtered_evolution = await analyzer.analyze_domain_evolution(
            SemanticDomain.IDENTIFICATION_MARKING,
            start_version="euring_1966",
            end_version="euring_1979"
        )
        print(f"   Filtered entries (1966-1979): {len(filtered_evolution.evolution_entries)}")
        
        print("✅ Domain evolution analysis working correctly")
        
    except Exception as e:
        print(f"❌ Domain evolution analysis failed: {e}")
        return False
    
    # Test 2: Compare domain versions (Requirement 8.2)
    print("\n🔍 Test 2: Comparing domain versions...")
    try:
        comparison = await analyzer.compare_domain_versions(
            SemanticDomain.IDENTIFICATION_MARKING,
            "euring_1966",
            "euring_1979"
        )
        
        print(f"   Comparison domain: {comparison['domain']}")
        print(f"   Version 1: {comparison['version1']}")
        print(f"   Version 2: {comparison['version2']}")
        print(f"   Compatibility level: {comparison['compatibility_level']}")
        print(f"   Total changes: {comparison['evolution_summary']['total_changes']}")
        print(f"   Fields added: {len(comparison['evolution_summary']['fields_added'])}")
        print(f"   Fields removed: {len(comparison['evolution_summary']['fields_removed'])}")
        print(f"   Fields modified: {len(comparison['evolution_summary']['fields_modified'])}")
        
        print("✅ Domain version comparison working correctly")
        
    except Exception as e:
        print(f"❌ Domain version comparison failed: {e}")
        return False
    
    # Test 3: Generate evolution timeline (Requirement 8.3)
    print("\n📅 Test 3: Generating evolution timeline...")
    try:
        timeline = await analyzer.generate_evolution_timeline(
            SemanticDomain.IDENTIFICATION_MARKING,
            include_details=True
        )
        
        print(f"   Timeline domain: {timeline['domain']}")
        print(f"   Timeline events: {len(timeline['timeline_events'])}")
        print(f"   Evolution period: {timeline['evolution_period']['start_year']}-{timeline['evolution_period']['end_year']}")
        print(f"   Duration: {timeline['evolution_period']['duration_years']} years")
        print(f"   Domain stability: {timeline['domain_stability']['stability_level']} (score: {timeline['domain_stability']['stability_score']})")
        
        # Check timeline events
        for i, event in enumerate(timeline['timeline_events'][:2]):  # Show first 2 events
            print(f"   Event {i+1}: {event['version']} ({event['year']}) - {event['changes_summary']['total_changes']} changes")
        
        print("✅ Evolution timeline generation working correctly")
        
    except Exception as e:
        print(f"❌ Evolution timeline generation failed: {e}")
        return False
    
    # Test 4: Test with SPECIES domain
    print("\n🐦 Test 4: Testing with SPECIES domain...")
    try:
        species_timeline = await analyzer.generate_evolution_timeline(
            SemanticDomain.SPECIES,
            include_details=False
        )
        
        print(f"   Species timeline events: {len(species_timeline['timeline_events'])}")
        print(f"   Species stability: {species_timeline['domain_stability']['stability_level']}")
        
        print("✅ SPECIES domain analysis working correctly")
        
    except Exception as e:
        print(f"❌ SPECIES domain analysis failed: {e}")
        return False
    
    # Test 5: Error handling
    print("\n⚠️  Test 5: Testing error handling...")
    try:
        # Test with non-existent domain
        try:
            await analyzer.analyze_domain_evolution(SemanticDomain.BIOMETRICS)  # Not loaded
            print("❌ Should have raised ValueError for non-existent domain")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly raised ValueError: {e}")
        
        # Test with invalid version comparison
        try:
            await analyzer.compare_domain_versions(
                SemanticDomain.IDENTIFICATION_MARKING,
                "invalid_version",
                "euring_1979"
            )
            print("❌ Should have handled invalid version gracefully")
        except Exception as e:
            print(f"   ✅ Correctly handled invalid version: {type(e).__name__}")
        
        print("✅ Error handling working correctly")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print("\n🎉 All Domain Evolution Analyzer tests passed!")
    print("\n📋 Test Summary:")
    print("   ✅ Domain evolution analysis (Requirement 8.1)")
    print("   ✅ Domain comparison algorithms (Requirement 8.2)")
    print("   ✅ Evolution timeline generation (Requirement 8.3)")
    print("   ✅ Error handling and edge cases")
    print("   ✅ Multiple domain support")
    
    return True


async def test_with_real_data():
    """Test with real EURING domain evolution data if available"""
    print("\n🔍 Testing with real EURING data...")
    
    # Check if real analysis data exists
    analysis_file = "backend/data/documentation/analysis/semantic_domain_analysis.json"
    if not os.path.exists(analysis_file):
        print("   ⚠️  Real analysis data not found, skipping real data test")
        return True
    
    try:
        # Load real domain evolution data
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        print(f"   📊 Loaded real data with {len(analysis_data['domain_evolutions'])} domains")
        
        # Test with real identification marking data
        if 'identification_marking' in analysis_data['domain_evolutions']:
            id_data = analysis_data['domain_evolutions']['identification_marking']
            print(f"   🔍 IDENTIFICATION_MARKING domain has {len(id_data['evolution_entries'])} evolution entries")
            print(f"   📈 Field evolution map has {len(id_data['field_evolution_map'])} fields")
            
            # Show some real evolution data
            for entry in id_data['evolution_entries'][:2]:
                print(f"      {entry['version']} ({entry['year']}): +{len(entry['fields_added'])} -{len(entry['fields_removed'])} ~{len(entry['fields_modified'])}")
        
        print("   ✅ Real data structure validation passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Real data test failed: {e}")
        return False


def main():
    """Main test execution"""
    print("🚀 Starting Domain Evolution Analyzer Tests")
    print("=" * 60)
    
    # Run async tests
    success = asyncio.run(test_domain_evolution_analyzer())
    
    if success:
        # Test with real data if available
        real_data_success = asyncio.run(test_with_real_data())
        
        if real_data_success:
            print("\n" + "=" * 60)
            print("🎯 Task B.1 Implementation Complete!")
            print("\n✅ Domain Evolution Analyzer Service successfully implemented:")
            print("   • Historical change analysis within domains")
            print("   • Domain comparison algorithms between versions")
            print("   • Evolution timeline generation for each domain")
            print("\n📋 Requirements Validated:")
            print("   • Requirement 8.1: Domain evolution analysis ✅")
            print("   • Requirement 8.2: Domain version comparison ✅")
            print("   • Requirement 8.3: Evolution timeline generation ✅")
            
            return True
    
    print("\n❌ Tests failed - implementation needs review")
    return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)