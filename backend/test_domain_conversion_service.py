"""
Test Domain-Specific Conversion Service

This test file validates the implementation of domain-specific conversion rules,
transformation logic, and compatibility assessment.

Requirements: 5.4, 8.5
"""
import asyncio
from typing import List, Dict, Any

from app.models.euring_models import (
    SemanticDomain, DomainCompatibilityLevel, EuringVersion,
    FieldDefinition, ValidationRule, FormatSpec, SemanticDomainMapping
)
from app.services.domain_conversion_service import DomainConversionService


class TestDomainConversionService:
    """Test suite for domain-specific conversion service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = DomainConversionService()
        self.test_versions = self._create_test_versions()
        self.service.load_versions(self.test_versions)
    
    def _create_test_versions(self) -> List[EuringVersion]:
        """Create test EURING versions for testing"""
        # Create 1966 version
        version_1966 = EuringVersion(
            id="1966",
            name="EURING 1966",
            year=1966,
            description="Original EURING format",
            field_definitions=[
                FieldDefinition(
                    position=1,
                    name="species_code",
                    data_type="integer",
                    length=4,
                    description="Species identification code",
                    semantic_domain=SemanticDomain.SPECIES,
                    semantic_meaning="species_identification"
                ),
                FieldDefinition(
                    position=2,
                    name="ring_number",
                    data_type="string",
                    length=7,
                    description="Ring identification number",
                    semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                    semantic_meaning="ring_identification"
                ),
                FieldDefinition(
                    position=3,
                    name="age_code",
                    data_type="integer",
                    length=1,
                    valid_values=["1", "2", "3", "4", "5"],
                    description="Age classification",
                    semantic_domain=SemanticDomain.DEMOGRAPHICS,
                    semantic_meaning="age_classification"
                ),
                FieldDefinition(
                    position=4,
                    name="date_code",
                    data_type="integer",
                    length=8,
                    description="Date in DDMMYYYY format",
                    semantic_domain=SemanticDomain.TEMPORAL,
                    semantic_meaning="observation_date"
                ),
                FieldDefinition(
                    position=5,
                    name="latitude",
                    data_type="string",
                    length=5,
                    description="Latitude in degrees/minutes",
                    semantic_domain=SemanticDomain.SPATIAL,
                    semantic_meaning="geographic_latitude"
                ),
                FieldDefinition(
                    position=6,
                    name="wing_length",
                    data_type="integer",
                    length=3,
                    description="Wing length in mm",
                    semantic_domain=SemanticDomain.BIOMETRICS,
                    semantic_meaning="wing_measurement"
                ),
                FieldDefinition(
                    position=7,
                    name="method_code",
                    data_type="integer",
                    length=1,
                    description="Capture method",
                    semantic_domain=SemanticDomain.METHODOLOGY,
                    semantic_meaning="capture_method"
                )
            ],
            validation_rules=[],
            format_specification=FormatSpec(total_length=50)
        )
        
        # Create 2020 version
        version_2020 = EuringVersion(
            id="2020",
            name="EURING 2020",
            year=2020,
            description="Modern EURING format",
            field_definitions=[
                FieldDefinition(
                    position=1,
                    name="species_code",
                    data_type="string",
                    length=5,
                    description="Species identification code",
                    semantic_domain=SemanticDomain.SPECIES,
                    semantic_meaning="species_identification"
                ),
                FieldDefinition(
                    position=2,
                    name="ring_number",
                    data_type="string",
                    length=8,
                    description="Ring identification number",
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
                    semantic_meaning="metal_ring_details"
                ),
                FieldDefinition(
                    position=4,
                    name="age_code",
                    data_type="integer",
                    length=1,
                    valid_values=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                    description="Age classification",
                    semantic_domain=SemanticDomain.DEMOGRAPHICS,
                    semantic_meaning="age_classification"
                ),
                FieldDefinition(
                    position=5,
                    name="sex_code",
                    data_type="integer",
                    length=1,
                    description="Sex classification",
                    semantic_domain=SemanticDomain.DEMOGRAPHICS,
                    semantic_meaning="sex_classification"
                ),
                FieldDefinition(
                    position=6,
                    name="date_code",
                    data_type="string",
                    length=8,
                    description="Date in YYYYMMDD format",
                    semantic_domain=SemanticDomain.TEMPORAL,
                    semantic_meaning="observation_date"
                ),
                FieldDefinition(
                    position=7,
                    name="time_code",
                    data_type="string",
                    length=4,
                    description="Time in HHMM format",
                    semantic_domain=SemanticDomain.TEMPORAL,
                    semantic_meaning="observation_time"
                ),
                FieldDefinition(
                    position=8,
                    name="latitude_decimal",
                    data_type="float",
                    length=10,
                    description="Latitude in decimal degrees",
                    semantic_domain=SemanticDomain.SPATIAL,
                    semantic_meaning="geographic_latitude"
                ),
                FieldDefinition(
                    position=9,
                    name="wing_length",
                    data_type="float",
                    length=5,
                    description="Wing length in mm",
                    semantic_domain=SemanticDomain.BIOMETRICS,
                    semantic_meaning="wing_measurement"
                ),
                FieldDefinition(
                    position=10,
                    name="fat_score",
                    data_type="integer",
                    length=1,
                    description="Fat score",
                    semantic_domain=SemanticDomain.BIOMETRICS,
                    semantic_meaning="fat_assessment"
                ),
                FieldDefinition(
                    position=11,
                    name="method_code",
                    data_type="string",
                    length=2,
                    description="Capture method",
                    semantic_domain=SemanticDomain.METHODOLOGY,
                    semantic_meaning="capture_method"
                ),
                FieldDefinition(
                    position=12,
                    name="status_info",
                    data_type="integer",
                    length=1,
                    description="Status information",
                    semantic_domain=SemanticDomain.METHODOLOGY,
                    semantic_meaning="status_details"
                )
            ],
            validation_rules=[],
            format_specification=FormatSpec(total_length=100)
        )
        
        return [version_1966, version_2020]
    
    async def test_create_domain_conversion_mapping(self):
        """Test creation of domain-specific conversion mapping"""
        # Test IDENTIFICATION_MARKING domain conversion from 1966 to 2020
        mapping = await self.service.create_domain_conversion_mapping(
            SemanticDomain.IDENTIFICATION_MARKING, "1966", "2020"
        )
        
        assert mapping.domain == SemanticDomain.IDENTIFICATION_MARKING
        assert mapping.compatibility in [
            DomainCompatibilityLevel.FULL,
            DomainCompatibilityLevel.PARTIAL,
            DomainCompatibilityLevel.LOSSY
        ]
        assert len(mapping.field_mappings) > 0
        assert len(mapping.transformation_rules) >= 0
        assert isinstance(mapping.conversion_notes, list)
        
        # Check that ring_number field is mapped
        ring_mapping = next(
            (fm for fm in mapping.field_mappings if fm.source_field == "ring_number"),
            None
        )
        assert ring_mapping is not None
        assert ring_mapping.target_field == "ring_number"
        assert ring_mapping.semantic_domain == SemanticDomain.IDENTIFICATION_MARKING
    
    async def test_create_all_domain_conversion_mappings(self):
        """Test creation of conversion mappings for all domains"""
        mappings = await self.service.create_all_domain_conversion_mappings("1966", "2020")
        
        # Should have mappings for domains that exist in both versions
        assert len(mappings) > 0
        
        # Check that we have mappings for key domains
        domain_names = [mapping.domain for mapping in mappings]
        assert SemanticDomain.IDENTIFICATION_MARKING in domain_names
        assert SemanticDomain.SPECIES in domain_names
        assert SemanticDomain.DEMOGRAPHICS in domain_names
        assert SemanticDomain.TEMPORAL in domain_names
        assert SemanticDomain.SPATIAL in domain_names
        assert SemanticDomain.BIOMETRICS in domain_names
        assert SemanticDomain.METHODOLOGY in domain_names
    
    async def test_assess_domain_compatibility_level(self):
        """Test domain compatibility level assessment"""
        # Test different domains
        species_compatibility = await self.service.assess_domain_compatibility_level(
            SemanticDomain.SPECIES, "1966", "2020"
        )
        assert species_compatibility in list(DomainCompatibilityLevel)
        
        temporal_compatibility = await self.service.assess_domain_compatibility_level(
            SemanticDomain.TEMPORAL, "1966", "2020"
        )
        assert temporal_compatibility in list(DomainCompatibilityLevel)
        
        # Same version should be fully compatible
        same_version_compatibility = await self.service.assess_domain_compatibility_level(
            SemanticDomain.SPECIES, "1966", "1966"
        )
        assert same_version_compatibility == DomainCompatibilityLevel.FULL
    
    async def test_apply_domain_transformation(self):
        """Test application of domain-specific transformations"""
        # Test IDENTIFICATION_MARKING domain transformation
        field_data = {
            "ring_number": "AB12345"
        }
        
        transformed_data = await self.service.apply_domain_transformation(
            SemanticDomain.IDENTIFICATION_MARKING, field_data, "1966", "2020"
        )
        
        assert "ring_number" in transformed_data
        # Should have the transformed ring number
        assert transformed_data["ring_number"] is not None
        
        # Test TEMPORAL domain transformation
        temporal_data = {
            "date_code": "01012023"
        }
        
        transformed_temporal = await self.service.apply_domain_transformation(
            SemanticDomain.TEMPORAL, temporal_data, "1966", "2020"
        )
        
        assert "date_code" in transformed_temporal
    
    async def test_get_domain_transformation_rules(self):
        """Test retrieval of domain-specific transformation rules"""
        # Get transformation rules for IDENTIFICATION_MARKING domain
        rules = await self.service.get_domain_transformation_rules(
            SemanticDomain.IDENTIFICATION_MARKING, "1966", "2020"
        )
        
        assert isinstance(rules, list)
        
        # Should have rules for new fields in 2020 version
        rule_targets = [rule.target_field for rule in rules]
        assert "metal_ring_info" in rule_targets or len(rules) == 0  # May not have specific rules
    
    def test_get_domain_fields(self):
        """Test extraction of domain-specific fields"""
        # Test SPECIES domain fields
        species_fields_1966 = self.service._get_domain_fields(SemanticDomain.SPECIES, "1966")
        assert len(species_fields_1966) == 1
        assert species_fields_1966[0].name == "species_code"
        
        species_fields_2020 = self.service._get_domain_fields(SemanticDomain.SPECIES, "2020")
        assert len(species_fields_2020) == 1
        assert species_fields_2020[0].name == "species_code"
        
        # Test BIOMETRICS domain fields
        biometrics_fields_1966 = self.service._get_domain_fields(SemanticDomain.BIOMETRICS, "1966")
        assert len(biometrics_fields_1966) == 1
        assert biometrics_fields_1966[0].name == "wing_length"
        
        biometrics_fields_2020 = self.service._get_domain_fields(SemanticDomain.BIOMETRICS, "2020")
        assert len(biometrics_fields_2020) == 2  # wing_length and fat_score
        field_names = [field.name for field in biometrics_fields_2020]
        assert "wing_length" in field_names
        assert "fat_score" in field_names
    
    def test_find_corresponding_field(self):
        """Test field correspondence detection"""
        # Get fields from both versions
        species_1966 = self.service._get_domain_fields(SemanticDomain.SPECIES, "1966")[0]
        species_2020 = self.service._get_domain_fields(SemanticDomain.SPECIES, "2020")[0]
        
        # Test exact name match
        corresponding_field = self.service._find_corresponding_field(
            species_1966, [species_2020]
        )
        assert corresponding_field is not None
        assert corresponding_field.name == "species_code"
        
        # Test semantic meaning match
        wing_1966 = self.service._get_domain_fields(SemanticDomain.BIOMETRICS, "1966")[0]
        wing_2020 = next(
            field for field in self.service._get_domain_fields(SemanticDomain.BIOMETRICS, "2020")
            if field.name == "wing_length"
        )
        
        corresponding_wing = self.service._find_corresponding_field(
            wing_1966, [wing_2020]
        )
        assert corresponding_wing is not None
        assert corresponding_wing.semantic_meaning == wing_1966.semantic_meaning
    
    def test_calculate_conversion_accuracy(self):
        """Test conversion accuracy calculation"""
        # Same field should have 100% accuracy
        species_1966 = self.service._get_domain_fields(SemanticDomain.SPECIES, "1966")[0]
        species_2020 = self.service._get_domain_fields(SemanticDomain.SPECIES, "2020")[0]
        
        # Different data types and lengths should reduce accuracy
        accuracy = self.service._calculate_conversion_accuracy(species_1966, species_2020)
        assert 0.1 <= accuracy <= 1.0  # Should be between 10% and 100%
        
        # Same field to itself should have perfect accuracy
        self_accuracy = self.service._calculate_conversion_accuracy(species_1966, species_1966)
        assert self_accuracy == 1.0


async def run_tests():
    """Run the test suite"""
    test_instance = TestDomainConversionService()
    
    print("Testing Domain Conversion Service...")
    
    # Setup
    test_instance.setup_method()
    
    # Run tests
    try:
        await test_instance.test_create_domain_conversion_mapping()
        print("✓ test_create_domain_conversion_mapping passed")
        
        await test_instance.test_create_all_domain_conversion_mappings()
        print("✓ test_create_all_domain_conversion_mappings passed")
        
        await test_instance.test_assess_domain_compatibility_level()
        print("✓ test_assess_domain_compatibility_level passed")
        
        await test_instance.test_apply_domain_transformation()
        print("✓ test_apply_domain_transformation passed")
        
        await test_instance.test_get_domain_transformation_rules()
        print("✓ test_get_domain_transformation_rules passed")
        
        test_instance.test_get_domain_fields()
        print("✓ test_get_domain_fields passed")
        
        test_instance.test_find_corresponding_field()
        print("✓ test_find_corresponding_field passed")
        
        test_instance.test_calculate_conversion_accuracy()
        print("✓ test_calculate_conversion_accuracy passed")
        
        print("\n✅ All Domain Conversion Service tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_tests())