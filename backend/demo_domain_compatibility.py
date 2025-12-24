"""
Demonstration of Domain Compatibility Assessment functionality

This script demonstrates the key features of the domain compatibility assessment
system for EURING code recognition.

Requirements: 8.5
"""
import asyncio
from app.services.domain_compatibility_assessor import DomainCompatibilityAssessor
from app.models.euring_models import (
    SemanticDomain, DomainCompatibilityLevel, DomainCompatibilityMatrix,
    DomainEvolution, DomainEvolutionEntry, DomainChange, DomainChangeType,
    EuringVersion, FieldDefinition, FormatSpec
)


def create_demo_versions():
    """Create demonstration EURING versions"""
    # 1966 version - basic fields
    fields_1966 = [
        FieldDefinition(
            position=1, name="species_code", data_type="integer", length=4,
            description="4-digit species code", semantic_domain=SemanticDomain.SPECIES,
            semantic_meaning="species_identification"
        ),
        FieldDefinition(
            position=2, name="ring_number", data_type="string", length=7,
            description="7-character ring number", semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_identification"
        ),
        FieldDefinition(
            position=3, name="age_code", data_type="integer", length=1,
            description="Age classification", semantic_domain=SemanticDomain.DEMOGRAPHICS,
            semantic_meaning="age_classification"
        )
    ]
    
    # 2020 version - enhanced fields
    fields_2020 = [
        FieldDefinition(
            position=1, name="species_code", data_type="string", length=5,
            description="5-character species code", semantic_domain=SemanticDomain.SPECIES,
            semantic_meaning="species_identification"
        ),
        FieldDefinition(
            position=2, name="ring_number", data_type="string", length=8,
            description="8-character ring number", semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_identification"
        ),
        FieldDefinition(
            position=3, name="metal_ring_info", data_type="integer", length=1,
            description="Metal ring information", semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_material"
        ),
        FieldDefinition(
            position=4, name="age_code", data_type="integer", length=1,
            description="Enhanced age classification", semantic_domain=SemanticDomain.DEMOGRAPHICS,
            semantic_meaning="age_classification"
        ),
        FieldDefinition(
            position=5, name="sex_code", data_type="integer", length=1,
            description="Sex classification", semantic_domain=SemanticDomain.DEMOGRAPHICS,
            semantic_meaning="sex_classification"
        ),
        FieldDefinition(
            position=6, name="wing_length", data_type="float", length=5,
            description="Wing length measurement", semantic_domain=SemanticDomain.BIOMETRICS,
            semantic_meaning="wing_measurement"
        ),
        FieldDefinition(
            position=7, name="weight", data_type="float", length=6,
            description="Body weight", semantic_domain=SemanticDomain.BIOMETRICS,
            semantic_meaning="weight_measurement"
        )
    ]
    
    version_1966 = EuringVersion(
        id="euring_1966", name="EURING 1966", year=1966,
        description="Original EURING format", field_definitions=fields_1966,
        validation_rules=[], format_specification=FormatSpec(total_length=50)
    )
    
    version_2020 = EuringVersion(
        id="euring_2020", name="EURING 2020", year=2020,
        description="Modern EURING format", field_definitions=fields_2020,
        validation_rules=[], format_specification=FormatSpec(total_length=100)
    )
    
    return [version_1966, version_2020]


def create_demo_domain_evolutions():
    """Create demonstration domain evolution data"""
    evolutions = []
    
    # Species domain evolution
    species_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.SPECIES)
    species_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.FULL)
    species_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.PARTIAL)
    
    species_evolution = DomainEvolution(
        domain=SemanticDomain.SPECIES,
        evolution_entries=[
            DomainEvolutionEntry(
                version="euring_1966", year=1966,
                changes=[DomainChange(
                    change_type=DomainChangeType.ADDED, field_name="species_code",
                    semantic_impact="Initial species coding system",
                    compatibility_impact=DomainCompatibilityLevel.FULL
                )],
                field_mappings=[], semantic_notes=["4-digit integer codes"]
            ),
            DomainEvolutionEntry(
                version="euring_2020", year=2020,
                changes=[DomainChange(
                    change_type=DomainChangeType.MODIFIED, field_name="species_code",
                    previous_value="4-digit integer", new_value="5-character string",
                    semantic_impact="Expanded species code space",
                    compatibility_impact=DomainCompatibilityLevel.PARTIAL
                )],
                field_mappings=[], semantic_notes=["5-character alphanumeric codes"]
            )
        ],
        compatibility_matrix=species_matrix
    )
    evolutions.append(species_evolution)
    
    # Identification marking domain evolution
    id_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.IDENTIFICATION_MARKING)
    id_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.PARTIAL)
    id_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.LOSSY)
    
    id_evolution = DomainEvolution(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        evolution_entries=[
            DomainEvolutionEntry(
                version="euring_1966", year=1966,
                changes=[DomainChange(
                    change_type=DomainChangeType.ADDED, field_name="ring_number",
                    semantic_impact="Basic ring identification",
                    compatibility_impact=DomainCompatibilityLevel.FULL
                )],
                field_mappings=[], semantic_notes=["7-character ring numbers"]
            ),
            DomainEvolutionEntry(
                version="euring_2020", year=2020,
                changes=[
                    DomainChange(
                        change_type=DomainChangeType.MODIFIED, field_name="ring_number",
                        previous_value="7 characters", new_value="8 characters",
                        semantic_impact="Enhanced ring identification",
                        compatibility_impact=DomainCompatibilityLevel.PARTIAL
                    ),
                    DomainChange(
                        change_type=DomainChangeType.ADDED, field_name="metal_ring_info",
                        semantic_impact="Added metal ring tracking",
                        compatibility_impact=DomainCompatibilityLevel.PARTIAL
                    )
                ],
                field_mappings=[], semantic_notes=["8-character ring numbers", "Metal ring information"]
            )
        ],
        compatibility_matrix=id_matrix
    )
    evolutions.append(id_evolution)
    
    # Demographics domain evolution
    demo_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.DEMOGRAPHICS)
    demo_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.PARTIAL)
    demo_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.LOSSY)
    
    demo_evolution = DomainEvolution(
        domain=SemanticDomain.DEMOGRAPHICS,
        evolution_entries=[
            DomainEvolutionEntry(
                version="euring_1966", year=1966,
                changes=[DomainChange(
                    change_type=DomainChangeType.ADDED, field_name="age_code",
                    semantic_impact="Basic age classification",
                    compatibility_impact=DomainCompatibilityLevel.FULL
                )],
                field_mappings=[], semantic_notes=["Age classification only"]
            ),
            DomainEvolutionEntry(
                version="euring_2020", year=2020,
                changes=[DomainChange(
                    change_type=DomainChangeType.ADDED, field_name="sex_code",
                    semantic_impact="Added sex classification",
                    compatibility_impact=DomainCompatibilityLevel.PARTIAL
                )],
                field_mappings=[], semantic_notes=["Age and sex classification"]
            )
        ],
        compatibility_matrix=demo_matrix
    )
    evolutions.append(demo_evolution)
    
    # Biometrics domain evolution (only in 2020)
    bio_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.BIOMETRICS)
    bio_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.INCOMPATIBLE)
    bio_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.INCOMPATIBLE)
    
    bio_evolution = DomainEvolution(
        domain=SemanticDomain.BIOMETRICS,
        evolution_entries=[
            DomainEvolutionEntry(
                version="euring_2020", year=2020,
                changes=[
                    DomainChange(
                        change_type=DomainChangeType.ADDED, field_name="wing_length",
                        semantic_impact="Added wing measurements",
                        compatibility_impact=DomainCompatibilityLevel.INCOMPATIBLE
                    ),
                    DomainChange(
                        change_type=DomainChangeType.ADDED, field_name="weight",
                        semantic_impact="Added weight measurements",
                        compatibility_impact=DomainCompatibilityLevel.INCOMPATIBLE
                    )
                ],
                field_mappings=[], semantic_notes=["Biometric measurements introduced"]
            )
        ],
        compatibility_matrix=bio_matrix
    )
    evolutions.append(bio_evolution)
    
    return evolutions


async def demonstrate_domain_compatibility():
    """Demonstrate domain compatibility assessment features"""
    print("🔍 DOMAIN COMPATIBILITY ASSESSMENT DEMONSTRATION")
    print("=" * 60)
    
    # Setup
    versions = create_demo_versions()
    domain_evolutions = create_demo_domain_evolutions()
    
    assessor = DomainCompatibilityAssessor()
    assessor.load_versions(versions)
    assessor.load_domain_evolutions(domain_evolutions)
    
    print(f"📊 Loaded {len(versions)} EURING versions and {len(domain_evolutions)} domain evolutions")
    print()
    
    # Demonstrate compatibility assessment for each domain
    domains_to_test = [
        (SemanticDomain.SPECIES, "Species identification codes"),
        (SemanticDomain.IDENTIFICATION_MARKING, "Ring identification and marking"),
        (SemanticDomain.DEMOGRAPHICS, "Age and sex classification"),
        (SemanticDomain.BIOMETRICS, "Biometric measurements")
    ]
    
    for domain, description in domains_to_test:
        print(f"🔬 ANALYZING {domain.value.upper()} DOMAIN")
        print(f"   {description}")
        print("-" * 50)
        
        # Test forward compatibility (1966 → 2020)
        try:
            forward_result = await assessor.assess_domain_compatibility(
                domain=domain,
                from_version="euring_1966",
                to_version="euring_2020",
                detailed_analysis=True
            )
            
            print(f"   📈 Forward (1966 → 2020):")
            print(f"      Compatibility: {forward_result.compatibility_level.upper()}")
            print(f"      Lossy conversion: {'Yes' if forward_result.is_lossy else 'No'}")
            print(f"      Warnings: {len(forward_result.conversion_warnings)}")
            print(f"      Loss details: {len(forward_result.loss_details)}")
            
            if forward_result.conversion_warnings:
                for warning in forward_result.conversion_warnings[:2]:  # Show first 2
                    print(f"         ⚠️  {warning}")
            
            if forward_result.loss_details:
                for loss in forward_result.loss_details[:2]:  # Show first 2
                    print(f"         💥 {loss['type']}: {loss['description']}")
        
        except Exception as e:
            print(f"   ❌ Forward compatibility analysis failed: {e}")
        
        # Test reverse compatibility (2020 → 1966)
        try:
            reverse_result = await assessor.assess_domain_compatibility(
                domain=domain,
                from_version="euring_2020",
                to_version="euring_1966",
                detailed_analysis=True
            )
            
            print(f"   📉 Reverse (2020 → 1966):")
            print(f"      Compatibility: {reverse_result.compatibility_level.upper()}")
            print(f"      Lossy conversion: {'Yes' if reverse_result.is_lossy else 'No'}")
            print(f"      Loss details: {len(reverse_result.loss_details)}")
            
            if reverse_result.loss_details:
                for loss in reverse_result.loss_details[:2]:  # Show first 2
                    print(f"         💥 {loss['type']}: {loss['description']}")
        
        except Exception as e:
            print(f"   ❌ Reverse compatibility analysis failed: {e}")
        
        print()
    
    # Demonstrate compatibility matrices
    print("📋 COMPATIBILITY MATRICES")
    print("-" * 50)
    
    for domain, description in domains_to_test[:3]:  # First 3 domains
        try:
            matrix = await assessor.create_domain_compatibility_matrix(
                domain=domain,
                versions=["euring_1966", "euring_2020"]
            )
            
            print(f"   {domain.value}:")
            compat_forward = matrix.get_compatibility("euring_1966", "euring_2020")
            compat_reverse = matrix.get_compatibility("euring_2020", "euring_1966")
            print(f"      1966 → 2020: {compat_forward.value.upper()}")
            print(f"      2020 → 1966: {compat_reverse.value.upper()}")
            
        except Exception as e:
            print(f"   ❌ Matrix creation failed for {domain.value}: {e}")
    
    print()
    
    # Demonstrate lossy conversion detection
    print("🔍 LOSSY CONVERSION DETECTION")
    print("-" * 50)
    
    try:
        lossy_conversions = await assessor.detect_lossy_conversions(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            version_pairs=[("euring_2020", "euring_1966")]
        )
        
        print(f"   Found {len(lossy_conversions)} lossy conversions for identification marking:")
        
        for (from_v, to_v), details in lossy_conversions.items():
            print(f"      {from_v} → {to_v}:")
            print(f"         Severity: {details['loss_severity']}")
            print(f"         Recommendation: {details['recommended_action']}")
            print(f"         Loss types: {len(details['loss_details'])}")
            
            for loss in details['loss_details'][:2]:  # Show first 2
                print(f"            - {loss['type']}: {loss['description']}")
    
    except Exception as e:
        print(f"   ❌ Lossy conversion detection failed: {e}")
    
    print()
    
    # Demonstrate comprehensive report
    print("📊 COMPREHENSIVE COMPATIBILITY REPORT")
    print("-" * 50)
    
    try:
        report = await assessor.generate_compatibility_report(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            include_matrices=True,
            include_lossy_analysis=True
        )
        
        print(f"   Domain: {report['domain']}")
        print(f"   Versions analyzed: {len(report['versions_analyzed'])}")
        print(f"   Total version pairs: {report['total_version_pairs']}")
        
        if 'compatibility_summary' in report:
            summary = report['compatibility_summary']
            print(f"   Overall compatibility score: {summary.get('compatibility_score', 'N/A'):.2f}")
            print(f"   Most common compatibility level: {summary.get('most_common_level', 'N/A')}")
        
        if 'lossy_conversion_summary' in report:
            lossy_summary = report['lossy_conversion_summary']
            print(f"   Lossy conversions found: {lossy_summary.get('total_lossy_conversions', 0)}")
        
        if 'domain_insights' in report:
            insights = report['domain_insights']
            characteristics = insights.get('domain_characteristics', {})
            print(f"   Domain stability: {characteristics.get('stability', 'unknown')}")
            print(f"   Domain complexity: {characteristics.get('complexity', 'unknown')}")
            print(f"   Critical for conversion: {characteristics.get('critical_for_conversion', False)}")
    
    except Exception as e:
        print(f"   ❌ Report generation failed: {e}")
    
    print()
    print("✅ Domain compatibility assessment demonstration completed!")
    print("=" * 60)


def main():
    """Run the demonstration"""
    try:
        asyncio.run(demonstrate_domain_compatibility())
        print("\n🎉 Demonstration completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)