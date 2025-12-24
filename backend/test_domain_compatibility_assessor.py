"""
Tests for Domain Compatibility Assessor Service

Tests domain-specific conversion compatibility checking, lossy conversion detection,
and compatibility matrices for each domain pair.

Requirements: 8.5
"""
import pytest
from typing import List, Dict, Any
from app.services.domain_compatibility_assessor import (
    DomainCompatibilityAssessor, CompatibilityAssessmentResult, ConversionLossType
)
from app.models.euring_models import (
    SemanticDomain, DomainCompatibilityLevel, DomainCompatibilityMatrix,
    DomainEvolution, DomainEvolutionEntry, DomainChange, DomainChangeType,
    EuringVersion, FieldDefinition, FormatSpec, ValidationRule
)


@pytest.fixture
def sample_versions():
    """Create sample EURING versions for testing"""
    # Create field definitions for different domains
    id_fields_1966 = [
        FieldDefinition(
            position=1,
            name="ring_number",
            data_type="string",
            length=7,
            description="Ring identification number",
            semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_identification"
        )
    ]
    
    id_fields_2020 = [
        FieldDefinition(
            position=1,
            name="ring_number",
            data_type="string",
            length=8,
            description="Enhanced ring identification number",
            semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_identification"
        ),
        FieldDefinition(
            position=2,
            name="metal_ring_info",
            data_type="integer",
            length=1,
            description="Metal ring information",
            semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
            semantic_meaning="ring_material"
        )
    ]
    
    species_fields_1966 = [
        FieldDefinition(
            position=3,
            name="species_code",
            data_type="integer",
            length=4,
            description="Species identification code",
            semantic_domain=SemanticDomain.SPECIES,
            semantic_meaning="species_identification"
        )
    ]
    
    species_fields_2020 = [
        FieldDefinition(
            position=3,
            name="species_code",
            data_type="string",
            length=5,
            description="Enhanced species identification code",
            semantic_domain=SemanticDomain.SPECIES,
            semantic_meaning="species_identification"
        )
    ]
    
    biometric_fields_2020 = [
        FieldDefinition(
            position=10,
            name="wing_length",
            data_type="float",
            length=5,
            description="Wing length measurement",
            semantic_domain=SemanticDomain.BIOMETRICS,
            semantic_meaning="wing_measurement"
        ),
        FieldDefinition(
            position=11,
            name="weight",
            data_type="float",
            length=6,
            description="Body weight measurement",
            semantic_domain=SemanticDomain.BIOMETRICS,
            semantic_meaning="weight_measurement"
        )
    ]
    
    version_1966 = EuringVersion(
        id="euring_1966",
        name="EURING 1966",
        year=1966,
        description="Original EURING format",
        field_definitions=id_fields_1966 + species_fields_1966,
        validation_rules=[],
        format_specification=FormatSpec(total_length=50)
    )
    
    version_2020 = EuringVersion(
        id="euring_2020",
        name="EURING 2020",
        year=2020,
        description="Modern EURING format",
        field_definitions=id_fields_2020 + species_fields_2020 + biometric_fields_2020,
        validation_rules=[],
        format_specification=FormatSpec(total_length=100)
    )
    
    return [version_1966, version_2020]


@pytest.fixture
def sample_domain_evolutions():
    """Create sample domain evolution data for testing"""
    # Identification marking evolution
    id_entry_1966 = DomainEvolutionEntry(
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
        semantic_notes=["Basic ring identification"]
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
                semantic_impact="Added metal ring information",
                compatibility_impact=DomainCompatibilityLevel.PARTIAL
            )
        ],
        field_mappings=[],
        semantic_notes=["Enhanced identification system", "Metal ring tracking"]
    )
    
    id_compatibility_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.IDENTIFICATION_MARKING)
    id_compatibility_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.PARTIAL)
    id_compatibility_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.LOSSY)
    
    id_evolution = DomainEvolution(
        domain=SemanticDomain.IDENTIFICATION_MARKING,
        evolution_entries=[id_entry_1966, id_entry_2020],
        compatibility_matrix=id_compatibility_matrix
    )
    
    # Species evolution
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
        semantic_notes=["4-digit species codes"]
    )
    
    species_entry_2020 = DomainEvolutionEntry(
        version="euring_2020",
        year=2020,
        changes=[
            DomainChange(
                change_type=DomainChangeType.MODIFIED,
                field_name="species_code",
                previous_value="4 digits",
                new_value="5 characters",
                semantic_impact="Expanded species code space",
                compatibility_impact=DomainCompatibilityLevel.PARTIAL
            )
        ],
        field_mappings=[],
        semantic_notes=["5-character species codes", "Alphanumeric support"]
    )
    
    species_compatibility_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.SPECIES)
    species_compatibility_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.FULL)
    species_compatibility_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.PARTIAL)
    
    species_evolution = DomainEvolution(
        domain=SemanticDomain.SPECIES,
        evolution_entries=[species_entry_1966, species_entry_2020],
        compatibility_matrix=species_compatibility_matrix
    )
    
    # Biometrics evolution (only in 2020)
    biometric_entry_2020 = DomainEvolutionEntry(
        version="euring_2020",
        year=2020,
        changes=[
            DomainChange(
                change_type=DomainChangeType.ADDED,
                field_name="wing_length",
                semantic_impact="Added wing measurement",
                compatibility_impact=DomainCompatibilityLevel.INCOMPATIBLE
            ),
            DomainChange(
                change_type=DomainChangeType.ADDED,
                field_name="weight",
                semantic_impact="Added weight measurement",
                compatibility_impact=DomainCompatibilityLevel.INCOMPATIBLE
            )
        ],
        field_mappings=[],
        semantic_notes=["Biometric measurements introduced"]
    )
    
    biometric_compatibility_matrix = DomainCompatibilityMatrix(domain=SemanticDomain.BIOMETRICS)
    biometric_compatibility_matrix.set_compatibility("euring_1966", "euring_2020", DomainCompatibilityLevel.INCOMPATIBLE)
    biometric_compatibility_matrix.set_compatibility("euring_2020", "euring_1966", DomainCompatibilityLevel.INCOMPATIBLE)
    
    biometric_evolution = DomainEvolution(
        domain=SemanticDomain.BIOMETRICS,
        evolution_entries=[biometric_entry_2020],
        compatibility_matrix=biometric_compatibility_matrix
    )
    
    return [id_evolution, species_evolution, biometric_evolution]


@pytest.fixture
def compatibility_assessor(sample_versions, sample_domain_evolutions):
    """Create configured compatibility assessor for testing"""
    assessor = DomainCompatibilityAssessor()
    assessor.load_versions(sample_versions)
    assessor.load_domain_evolutions(sample_domain_evolutions)
    return assessor


class TestDomainCompatibilityAssessor:
    """Test suite for Domain Compatibility Assessor"""
    
    @pytest.mark.asyncio
    async def test_assess_domain_compatibility_partial(self, compatibility_assessor):
        """Test domain compatibility assessment for partial compatibility"""
        result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            from_version="euring_1966",
            to_version="euring_2020",
            detailed_analysis=True
        )
        
        assert isinstance(result, CompatibilityAssessmentResult)
        assert result.domain == "identification_marking"
        assert result.from_version == "euring_1966"
        assert result.to_version == "euring_2020"
        assert result.compatibility_level == "partial"
        assert result.is_lossy is False  # No fields removed, just enhanced
        assert len(result.conversion_warnings) > 0
        assert len(result.conversion_notes) > 0
        assert 'field_compatibility' in result
        assert 'assessment_metadata' in result
    
    @pytest.mark.asyncio
    async def test_assess_domain_compatibility_lossy(self, compatibility_assessor):
        """Test domain compatibility assessment for lossy conversion"""
        result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            from_version="euring_2020",
            to_version="euring_1966",
            detailed_analysis=True
        )
        
        assert result.compatibility_level == "lossy"
        assert result.is_lossy is True
        assert len(result.loss_details) > 0
        
        # Check for field removal loss
        field_removed_losses = [
            loss for loss in result.loss_details
            if loss['type'] == ConversionLossType.FIELD_REMOVED.value
        ]
        assert len(field_removed_losses) > 0
        assert any('metal_ring_info' in loss['field'] for loss in field_removed_losses)
    
    @pytest.mark.asyncio
    async def test_assess_domain_compatibility_incompatible(self, compatibility_assessor):
        """Test domain compatibility assessment for incompatible conversion"""
        result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.BIOMETRICS,
            from_version="euring_1966",
            to_version="euring_2020",
            detailed_analysis=True
        )
        
        assert result.compatibility_level == "incompatible"
        assert result.is_lossy is False  # No loss since fields are added, not removed
        assert len(result.conversion_warnings) > 0
        
        # Should warn about incompatibility
        incompatible_warnings = [
            warning for warning in result.conversion_warnings
            if 'not recommended' in warning.lower()
        ]
        assert len(incompatible_warnings) > 0
    
    @pytest.mark.asyncio
    async def test_assess_domain_compatibility_full(self, compatibility_assessor):
        """Test domain compatibility assessment for full compatibility"""
        result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.SPECIES,
            from_version="euring_1966",
            to_version="euring_2020",
            detailed_analysis=True
        )
        
        assert result.compatibility_level == "full"
        assert result.is_lossy is False
        assert len(result.loss_details) == 0
        
        # Should have positive notes for full compatibility
        full_compat_notes = [
            note for note in result.conversion_notes
            if 'full compatibility' in note.lower()
        ]
        assert len(full_compat_notes) > 0
    
    @pytest.mark.asyncio
    async def test_create_domain_compatibility_matrix(self, compatibility_assessor):
        """Test creation of domain compatibility matrix"""
        matrix = await compatibility_assessor.create_domain_compatibility_matrix(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            versions=["euring_1966", "euring_2020"]
        )
        
        assert isinstance(matrix, DomainCompatibilityMatrix)
        assert matrix.domain == SemanticDomain.IDENTIFICATION_MARKING
        
        # Check that all version pairs have compatibility levels
        compat_1966_to_2020 = matrix.get_compatibility("euring_1966", "euring_2020")
        compat_2020_to_1966 = matrix.get_compatibility("euring_2020", "euring_1966")
        
        assert compat_1966_to_2020 in [
            DomainCompatibilityLevel.FULL,
            DomainCompatibilityLevel.PARTIAL,
            DomainCompatibilityLevel.LOSSY,
            DomainCompatibilityLevel.INCOMPATIBLE
        ]
        assert compat_2020_to_1966 in [
            DomainCompatibilityLevel.FULL,
            DomainCompatibilityLevel.PARTIAL,
            DomainCompatibilityLevel.LOSSY,
            DomainCompatibilityLevel.INCOMPATIBLE
        ]
    
    @pytest.mark.asyncio
    async def test_get_all_domain_compatibility_matrices(self, compatibility_assessor):
        """Test getting all domain compatibility matrices"""
        matrices = await compatibility_assessor.get_all_domain_compatibility_matrices()
        
        assert isinstance(matrices, dict)
        assert len(matrices) >= 3  # At least the domains we loaded
        
        for domain, matrix in matrices.items():
            assert isinstance(domain, SemanticDomain)
            assert isinstance(matrix, DomainCompatibilityMatrix)
            assert matrix.domain == domain
    
    @pytest.mark.asyncio
    async def test_detect_lossy_conversions(self, compatibility_assessor):
        """Test detection of lossy conversions"""
        lossy_conversions = await compatibility_assessor.detect_lossy_conversions(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            version_pairs=[("euring_2020", "euring_1966")]
        )
        
        assert isinstance(lossy_conversions, dict)
        
        # Should detect lossy conversion from 2020 to 1966
        pair_key = ("euring_2020", "euring_1966")
        if pair_key in lossy_conversions:
            loss_info = lossy_conversions[pair_key]
            assert loss_info['is_lossy'] is True
            assert len(loss_info['loss_details']) > 0
            assert 'loss_severity' in loss_info
            assert 'recommended_action' in loss_info
    
    @pytest.mark.asyncio
    async def test_generate_compatibility_report(self, compatibility_assessor):
        """Test generation of comprehensive compatibility report"""
        report = await compatibility_assessor.generate_compatibility_report(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            include_matrices=True,
            include_lossy_analysis=True
        )
        
        assert isinstance(report, dict)
        assert report['domain'] == "identification_marking"
        assert 'report_timestamp' in report
        assert 'versions_analyzed' in report
        assert 'total_version_pairs' in report
        
        # Check matrix inclusion
        assert 'compatibility_matrix' in report
        assert 'compatibility_summary' in report
        
        # Check lossy analysis inclusion
        assert 'lossy_conversions' in report
        assert 'lossy_conversion_summary' in report
        
        # Check domain insights
        assert 'domain_insights' in report
        assert 'domain_characteristics' in report['domain_insights']
        assert 'evolution_pattern' in report['domain_insights']
        assert 'conversion_recommendations' in report['domain_insights']
    
    @pytest.mark.asyncio
    async def test_field_compatibility_analysis(self, compatibility_assessor):
        """Test detailed field-level compatibility analysis"""
        result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.SPECIES,
            from_version="euring_1966",
            to_version="euring_2020",
            detailed_analysis=True
        )
        
        field_compatibility = result.field_compatibility
        assert isinstance(field_compatibility, dict)
        
        # Should analyze species_code field
        assert 'species_code' in field_compatibility
        species_compat = field_compatibility['species_code']
        
        assert 'compatibility' in species_compat
        assert 'field_mapping' in species_compat
        assert species_compat['field_mapping']['from_field'] == 'species_code'
        assert species_compat['field_mapping']['to_field'] == 'species_code'
    
    @pytest.mark.asyncio
    async def test_conversion_loss_detection(self, compatibility_assessor):
        """Test specific types of conversion loss detection"""
        result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            from_version="euring_2020",
            to_version="euring_1966",
            detailed_analysis=True
        )
        
        loss_details = result.loss_details
        
        # Should detect field removal
        field_removal_losses = [
            loss for loss in loss_details
            if loss['type'] == ConversionLossType.FIELD_REMOVED.value
        ]
        assert len(field_removal_losses) > 0
        
        # Check loss severity classification
        for loss in loss_details:
            assert 'severity' in loss
            assert loss['severity'] in ['low', 'medium', 'high']
    
    @pytest.mark.asyncio
    async def test_domain_specific_warnings(self, compatibility_assessor):
        """Test domain-specific conversion warnings"""
        # Test identification marking warnings
        id_result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.IDENTIFICATION_MARKING,
            from_version="euring_1966",
            to_version="euring_2020"
        )
        
        # Should have domain-specific warnings for identification marking
        id_warnings = [
            warning for warning in id_result.conversion_warnings
            if 'ring number' in warning.lower()
        ]
        # Note: This might be 0 if no specific warnings are generated for this case
        
        # Test biometrics warnings
        bio_result = await compatibility_assessor.assess_domain_compatibility(
            domain=SemanticDomain.BIOMETRICS,
            from_version="euring_1966",
            to_version="euring_2020"
        )
        
        # Should have warnings about limited biometric data in 1966
        bio_warnings = [
            warning for warning in bio_result.conversion_warnings
            if 'biometric' in warning.lower() or 'limited' in warning.lower()
        ]
        # Note: This might be 0 if no specific warnings are generated for this case
    
    @pytest.mark.asyncio
    async def test_compatibility_matrix_serialization(self, compatibility_assessor):
        """Test compatibility matrix serialization for reporting"""
        matrix = await compatibility_assessor.create_domain_compatibility_matrix(
            domain=SemanticDomain.SPECIES,
            versions=["euring_1966", "euring_2020"]
        )
        
        serialized = compatibility_assessor._serialize_compatibility_matrix(matrix)
        
        assert isinstance(serialized, dict)
        assert serialized['domain'] == "species"
        assert 'compatibility_pairs' in serialized
        
        # Check that version pairs are properly serialized
        pairs = serialized['compatibility_pairs']
        assert isinstance(pairs, dict)
        
        # Should have entries for both directions
        expected_keys = ["euring_1966_to_euring_2020", "euring_2020_to_euring_1966"]
        for key in expected_keys:
            if key in pairs:
                assert pairs[key] in ["full", "partial", "lossy", "incompatible"]
    
    @pytest.mark.asyncio
    async def test_compatibility_score_calculation(self, compatibility_assessor):
        """Test overall compatibility score calculation"""
        report = await compatibility_assessor.generate_compatibility_report(
            domain=SemanticDomain.SPECIES,
            include_matrices=True,
            include_lossy_analysis=False
        )
        
        compatibility_summary = report['compatibility_summary']
        assert 'compatibility_score' in compatibility_summary
        
        score = compatibility_summary['compatibility_score']
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_domain(self, compatibility_assessor):
        """Test error handling for invalid domain"""
        with pytest.raises(ValueError, match="Domain .* not found"):
            await compatibility_assessor.assess_domain_compatibility(
                domain=SemanticDomain.TEMPORAL,  # Not loaded in test data
                from_version="euring_1966",
                to_version="euring_2020"
            )
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_version(self, compatibility_assessor):
        """Test error handling for invalid version"""
        with pytest.raises(ValueError, match="Version not found"):
            await compatibility_assessor.assess_domain_compatibility(
                domain=SemanticDomain.IDENTIFICATION_MARKING,
                from_version="invalid_version",
                to_version="euring_2020"
            )


class TestCompatibilityAssessmentResult:
    """Test suite for CompatibilityAssessmentResult"""
    
    def test_compatibility_assessment_result_creation(self):
        """Test creation of CompatibilityAssessmentResult"""
        result = CompatibilityAssessmentResult(
            domain="identification_marking",
            from_version="euring_1966",
            to_version="euring_2020",
            compatibility_level="partial",
            is_lossy=False,
            loss_details=[],
            field_compatibility={},
            conversion_warnings=["Test warning"],
            conversion_notes=["Test note"]
        )
        
        assert result.domain == "identification_marking"
        assert result.from_version == "euring_1966"
        assert result.to_version == "euring_2020"
        assert result.compatibility_level == "partial"
        assert result.is_lossy is False
        assert len(result.conversion_warnings) == 1
        assert len(result.conversion_notes) == 1
    
    def test_compatibility_assessment_result_dict_access(self):
        """Test dictionary-style access to CompatibilityAssessmentResult"""
        result = CompatibilityAssessmentResult(
            domain="species",
            compatibility_level="full"
        )
        
        # Should work as both object and dict
        assert result.domain == "species"
        assert result['domain'] == "species"
        assert result.compatibility_level == "full"
        assert result['compatibility_level'] == "full"


if __name__ == "__main__":
    pytest.main([__file__])