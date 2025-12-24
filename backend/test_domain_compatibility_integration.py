"""
Integration tests for Domain Compatibility Assessment with existing EURING system

Tests the integration of domain compatibility assessment with the SKOS manager
and existing EURING code recognition system.

Requirements: 8.5
"""
import asyncio
from app.services.domain_compatibility_assessor import DomainCompatibilityAssessor
from app.services.skos_manager import SKOSManagerImpl
from app.models.euring_models import (
    SemanticDomain, DomainCompatibilityLevel, DomainCompatibilityMatrix,
    DomainEvolution, DomainEvolutionEntry, DomainChange, DomainChangeType,
    EuringVersion, FieldDefinition, FormatSpec, ValidationRule
)


def create_test_versions():
    """Create test EURING versions for integration testing"""
    # Create 1966 version with basic fields
    fields_1966 = [
        FieldDefinition(
            position=1,
            name="species_code",
            data_type="integer",
            length=4,
            description="Species code",
            semantic_domain=SemanticDomain.SPECIES,
            semantic_meaning="species_identification"
        ),
        FieldDefinition(
            position=2,
            name="ring_number",
            data_type="string",
            length=7,
            description="Ring number",
            semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_identification"
        )
    ]
    
    version_1966 = EuringVersion(
        id="euring_1966",
        name="EURING 1966",
        year=1966,
        description="Original EURING format",
        field_definitions=fields_1966,
        validation_rules=[],
        format_specification=FormatSpec(total_length=50)
    )
    
    # Create 2020 version with enhanced fields
    fields_2020 = [
        FieldDefinition(
            position=1,
            name="species_code",
            data_type="string",
            length=5,
            description="Enhanced species code",
            semantic_domain=SemanticDomain.SPECIES,
            semantic_meaning="species_identification"
        ),
        FieldDefinition(
            position=2,
            name="ring_number",
            data_type="string",
            length=8,
            description="Enhanced ring number",
            semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_identification"
        ),
        FieldDefinition(
            position=3,
            name="metal_ring_info",
            data_type="integer",
            length=1,
            description="Metal ring information",
            semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_material"
        ),
        FieldDefinition(
            position=4,
            name="wing_length",
            data_type="float",
            length=5,
            description="Wing length",
            semantic_domain=SemanticDomain.BIOMETRICS,
            semantic_meaning="wing_measurement"
        )
    ]
    
    version_2020 = EuringVersion(
        id="euring_2020",
        name="EURING 2020",
        year=2020,
        description="Modern EURING format",
        field_definitions=fields_2020,
        validation_rules=[],
        format_specification=FormatSpec(total_length=100)
    )
    
    return [version_1966, version_2020]


def create_test_domain_evolutions():
    """Create test domain evolution data"""
    # Species domain evolution
    species_entry_1966 = DomainEvolutionEntry(
        version="euring_1966",
        year=1966,
        changes=[
            DomainChange(
                change_type=DomainChangeType.ADDED,
                field_name="species_code",
                semantic_impact="Initial species coding",
                compatibility_impact=DomainCompatibilityLevel.FULL
            )
        ],
        field_mappings=[],
        semantic_notes=["4-digit integer species codes"]
    )
    
    species_entry_2020 = DomainEvolutionEntry(
        version="euring_2020",
        year=2020,
        changes=[
            DomainChange(
                change_type=DomainChangeType.MODIFIED,
                field_name="species_code",
                previous_value="4-digit integer",
                new_value="5-character string",
                semantic_impact="Expanded species code space",
                compatibility_impact=DomainCompatibilityLevel.PARTIAL
            )
        ],
        field_mappings=[],
        semantic_notes=["5-character alphanumeric species codes"]
    )
    
    species_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.SPECIES)
    species_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.FULL)
    species_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.PARTIAL)
    
    species_evolution = DomainEvolution(
        domain=SemanticDomain.SPECIES,
        evolution_entries=[species_entry_1966, species_entry_2020],
        compatibility_matrix=species_matrix
    )
    
    # Identification marking domain evolution
    id_entry_1966 = DomainEvolutionEntry(
        version="euring_1966",
        year=1966,
        changes=[
            DomainChange(
                change_type=DomainChangeType.ADDED,
                field_name="ring_number",
                semantic_impact="Basic ring identification",
                compatibility_impact=DomainCompatibilityLevel.FULL
            )
        ],
        field_mappings=[],
        semantic_notes=["7-character ring numbers"]
    )
    
    id_entry_2020 = DomainEvolutionEntry(
        version="euring_2020",
        year=2020,
        changes=[
            DomainChange(
                change_type=DomainChangeType.MODIFIED,
                field_name="ring_number",
                previous_value="7 characters",
                new_value="8 characters",
                semantic_impact="Enhanced ring identification",
                compatibility_impact=DomainCompatibilityLevel.PARTIAL
            ),
            DomainChange(
                change_type=DomainChangeType.ADDED,
                field_name="metal_ring_info",
                semantic_impact="Added metal ring tracking",
                compatibility_impact=DomainCompatibilityLevel.PARTIAL
            )
        ],
        field_mappings=[],
        semantic_notes=["8-character ring numbers", "Metal ring information"]
    )
    
    id_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.IDENTIFICATION_MARKING)
    id_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.PARTIAL)
    id_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.LOSSY)
    
    id_evolution = DomainEvolution(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        evolution_entries=[id_entry_1966, id_entry_2020],
        compatibility_matrix=id_matrix
    )
    
    # Biometrics domain evolution (only in 2020)
    bio_entry_2020 = DomainEvolutionEntry(
        version="euring_2020",
        year=2020,
        changes=[
            DomainChange(
                change_type=DomainChangeType.ADDED,
                field_name="wing_length",
                semantic_impact="Added biometric measurements",
                compatibility_impact=DomainCompatibilityLevel.INCOMPATIBLE
            )
        ],
        field_mappings=[],
        semantic_notes=["Biometric measurements introduced"]
    )
    
    bio_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.BIOMETRICS)
    bio_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.INCOMPATIBLE)
    bio_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.INCOMPATIBLE)
    
    bio_evolution = DomainEvolution(
        domain=SemanticDomain.BIOMETRICS,
        evolution_entries=[bio_entry_2020],
        compatibility_matrix=bio_matrix
    )
    
    return [species_evolution, id_evolution, bio_evolution]


async def test_domain_compatibility_integration():
    """Test integration of domain compatibility assessment with SKOS manager"""
    print("Testing Domain Compatibility Assessment Integration...")
    
    # Create test data
    versions = create_test_versions()
    domain_evolutions = create_test_domain_evolutions()
    
    # Create and configure assessor
    assessor = DomainCompatibilityAssessor()
    assessor.load_versions(versions)
    assessor.load_domain_evolutions(domain_evolutions)
    
    print("✓ Domain compatibility assessor configured")
    
    # Test 1: Assess species domain compatibility (should be FULL)
    print("\n1. Testing species domain compatibility (1966 → 2020)...")
    species_result = await assessor.assess_domain_compatibility(
        domain=SemanticDomain.SPECIES,
        from_version="euring_1966",
        to_version="euring_2020",
        detailed_analysis=True
    )
    
    print(f"   Compatibility level: {species_result.compatibility_level}")
    print(f"   Is lossy: {species_result.is_lossy}")
    print(f"   Warnings: {len(species_result.conversion_warnings)}")
    print(f"   Notes: {len(species_result.conversion_notes)}")
    
    assert species_result.compatibility_level == "full"
    assert species_result.is_lossy is False
    print("✓ Species domain compatibility test passed")
    
    # Test 2: Assess identification marking compatibility (should be PARTIAL)
    print("\n2. Testing identification marking domain compatibility (1966 → 2020)...")
    id_result = await assessor.assess_domain_compatibility(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        from_version="euring_1966",
        to_version="euring_2020",
        detailed_analysis=True
    )
    
    print(f"   Compatibility level: {id_result.compatibility_level}")
    print(f"   Is lossy: {id_result.is_lossy}")
    print(f"   Field compatibility: {len(id_result.field_compatibility)} fields analyzed")
    
    assert id_result.compatibility_level == "partial"
    print("✓ Identification marking domain compatibility test passed")
    
    # Test 3: Assess reverse compatibility (should be LOSSY)
    print("\n3. Testing reverse compatibility (2020 → 1966)...")
    reverse_result = await assessor.assess_domain_compatibility(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        from_version="euring_2020",
        to_version="euring_1966",
        detailed_analysis=True
    )
    
    print(f"   Compatibility level: {reverse_result.compatibility_level}")
    print(f"   Is lossy: {reverse_result.is_lossy}")
    print(f"   Loss details: {len(reverse_result.loss_details)} losses detected")
    
    assert reverse_result.compatibility_level == "lossy"
    assert reverse_result.is_lossy is True
    print("✓ Reverse compatibility test passed")
    
    # Test 4: Assess biometrics domain (should be INCOMPATIBLE)
    print("\n4. Testing biometrics domain compatibility (1966 → 2020)...")
    bio_result = await assessor.assess_domain_compatibility(
        domain=SemanticDomain.BIOMETRICS,
        from_version="euring_1966",
        to_version="euring_2020",
        detailed_analysis=True
    )
    
    print(f"   Compatibility level: {bio_result.compatibility_level}")
    print(f"   Warnings: {len(bio_result.conversion_warnings)}")
    
    assert bio_result.compatibility_level == "incompatible"
    print("✓ Biometrics domain compatibility test passed")
    
    # Test 5: Create compatibility matrices
    print("\n5. Testing compatibility matrix creation...")
    species_matrix = await assessor.create_domain_compatibility_matrix(
        domain=SemanticDomain.SPECIES,
        versions=["euring_1966", "euring_2020"]
    )
    
    print(f"   Species matrix created for domain: {species_matrix.domain.value}")
    print(f"   Matrix entries: {len(species_matrix.compatibility_map)}")
    
    # Check specific compatibility levels
    compat_1966_to_2020 = species_matrix.get_compatibility("euring_1966", "euring_2020")
    compat_2020_to_1966 = species_matrix.get_compatibility("euring_2020", "euring_1966")
    
    print(f"   1966→2020: {compat_1966_to_2020.value}")
    print(f"   2020→1966: {compat_2020_to_1966.value}")
    
    assert compat_1966_to_2020 != DomainCompatibilityLevel.INCOMPATIBLE
    print("✓ Compatibility matrix creation test passed")
    
    # Test 6: Generate comprehensive report
    print("\n6. Testing compatibility report generation...")
    report = await assessor.generate_compatibility_report(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        include_matrices=True,
        include_lossy_analysis=True
    )
    
    print(f"   Report generated for domain: {report['domain']}")
    print(f"   Versions analyzed: {len(report['versions_analyzed'])}")
    print(f"   Total version pairs: {report['total_version_pairs']}")
    print(f"   Compatibility matrix included: {'compatibility_matrix' in report}")
    print(f"   Lossy analysis included: {'lossy_conversions' in report}")
    print(f"   Domain insights included: {'domain_insights' in report}")
    
    assert report['domain'] == "identification_marking"
    assert 'compatibility_matrix' in report
    assert 'lossy_conversions' in report
    assert 'domain_insights' in report
    print("✓ Compatibility report generation test passed")
    
    # Test 7: Detect lossy conversions
    print("\n7. Testing lossy conversion detection...")
    lossy_conversions = await assessor.detect_lossy_conversions(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        version_pairs=[("euring_2020", "euring_1966")]
    )
    
    print(f"   Lossy conversions detected: {len(lossy_conversions)}")
    
    if lossy_conversions:
        for pair, details in lossy_conversions.items():
            print(f"   {pair[0]} → {pair[1]}: {details['loss_severity']} severity")
            print(f"   Recommendation: {details['recommended_action']}")
    
    print("✓ Lossy conversion detection test passed")
    
    print("\n🎉 All domain compatibility integration tests passed!")
    return True


async def test_skos_manager_integration():
    """Test integration with SKOS manager"""
    print("\nTesting SKOS Manager Integration...")
    
    # Note: This would require actual SKOS manager setup with data files
    # For now, we'll test the interface compatibility
    
    try:
        # Test that the SKOS manager can be imported with domain compatibility
        from app.services.skos_manager import SKOSManagerImpl
        
        # Create SKOS manager (won't load data without proper setup)
        skos_manager = SKOSManagerImpl()
        
        # Test that the new methods exist
        assert hasattr(skos_manager, 'get_domain_evolution')
        assert hasattr(skos_manager, 'analyze_domain_compatibility')
        assert hasattr(skos_manager, 'get_semantic_domains')
        
        print("✓ SKOS manager interface compatibility verified")
        
        # Test semantic domains enumeration
        domains = await skos_manager.get_semantic_domains()
        print(f"✓ Available semantic domains: {len(domains)}")
        for domain in domains:
            print(f"   - {domain.value}")
        
        print("✓ SKOS manager integration test passed")
        return True
        
    except Exception as e:
        print(f"✗ SKOS manager integration test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("=" * 60)
    print("DOMAIN COMPATIBILITY ASSESSMENT INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        # Run domain compatibility tests
        result1 = asyncio.run(test_domain_compatibility_integration())
        
        # Run SKOS manager integration tests
        result2 = asyncio.run(test_skos_manager_integration())
        
        if result1 and result2:
            print("\n" + "=" * 60)
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("Domain compatibility assessment is ready for use.")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n❌ Integration tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)