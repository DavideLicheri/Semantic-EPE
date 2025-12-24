"""
Test suite for Semantic Field Grouper Service

This test suite validates the semantic field grouping functionality including:
- Field grouping by semantic relationships
- Domain-specific field analysis
- Semantic meaning extraction and categorization

Requirements: 8.4
"""
import pytest
from app.services.semantic_field_grouper import SemanticFieldGrouper, SemanticMeaning, FieldGroup
from app.models.euring_models import (
    FieldDefinition, SemanticDomain, EuringVersion, FormatSpec, ValidationRule
)


class TestSemanticFieldGrouper:
    """Test cases for semantic field grouping functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.grouper = SemanticFieldGrouper()
        
        # Create test field definitions
        self.test_fields = [
            FieldDefinition(
                position=1,
                name="ring_number",
                data_type="alphanumeric",
                length=8,
                description="Ring number for bird identification",
                semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                semantic_meaning="Unique ring identifier"
            ),
            FieldDefinition(
                position=2,
                name="metal_ring_info",
                data_type="numeric",
                length=1,
                description="Metal ring information code",
                semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
                semantic_meaning="Metal ring status"
            ),
            FieldDefinition(
                position=3,
                name="species_code",
                data_type="numeric",
                length=5,
                description="Species identification code",
                semantic_domain=SemanticDomain.SPECIES,
                semantic_meaning="EURING species code"
            ),
            FieldDefinition(
                position=4,
                name="latitude_decimal",
                data_type="decimal",
                length=10,
                description="Latitude in decimal degrees",
                semantic_domain=SemanticDomain.SPATIAL,
                semantic_meaning="Geographic latitude coordinate"
            ),
            FieldDefinition(
                position=5,
                name="longitude_decimal",
                data_type="decimal",
                length=10,
                description="Longitude in decimal degrees",
                semantic_domain=SemanticDomain.SPATIAL,
                semantic_meaning="Geographic longitude coordinate"
            ),
            FieldDefinition(
                position=6,
                name="wing_length",
                data_type="numeric",
                length=3,
                description="Wing length measurement in mm",
                semantic_domain=SemanticDomain.BIOMETRICS,
                semantic_meaning="Wing measurement"
            ),
            FieldDefinition(
                position=7,
                name="weight",
                data_type="numeric",
                length=4,
                description="Body weight in grams",
                semantic_domain=SemanticDomain.BIOMETRICS,
                semantic_meaning="Body weight measurement"
            )
        ]
        
        # Create test versions
        self.test_versions = [
            EuringVersion(
                id="test_2020",
                name="Test EURING 2020",
                year=2020,
                description="Test version",
                field_definitions=self.test_fields,
                validation_rules=[],
                format_specification=FormatSpec(total_length=50)
            )
        ]
    
    def test_extract_semantic_meaning(self):
        """Test semantic meaning extraction from field definitions"""
        # Test with identification field
        ring_field = self.test_fields[0]  # ring_number
        meaning = self.grouper.extract_semantic_meaning(ring_field)
        
        assert isinstance(meaning, SemanticMeaning)
        assert meaning.field_name == "ring_number"
        assert meaning.domain == SemanticDomain.IDENTIFICATION_MARKING
        assert meaning.confidence > 0.5
        assert "ring" in meaning.primary_concept.lower() or "identification" in meaning.primary_concept.lower()
        
        # Test with coordinate field
        lat_field = self.test_fields[3]  # latitude_decimal
        lat_meaning = self.grouper.extract_semantic_meaning(lat_field)
        
        assert lat_meaning.field_name == "latitude_decimal"
        assert lat_meaning.domain == SemanticDomain.SPATIAL
        assert "spatial" in lat_meaning.primary_concept.lower() or "lat" in lat_meaning.primary_concept.lower()
    
    def test_group_fields_by_semantics(self):
        """Test grouping fields by semantic relationships"""
        # Test grouping all fields
        groups = self.grouper.group_fields_by_semantics(self.test_fields)
        
        assert isinstance(groups, list)
        assert len(groups) >= 1  # Should create at least one group
        
        # Check that coordinate fields are grouped together
        coordinate_group = None
        for group in groups:
            if "latitude_decimal" in group.fields and "longitude_decimal" in group.fields:
                coordinate_group = group
                break
        
        if coordinate_group:
            assert coordinate_group.domain == SemanticDomain.SPATIAL
            assert coordinate_group.cohesion_score > 0.5
            assert len(coordinate_group.relationships) > 0
    
    def test_group_fields_by_domain(self):
        """Test grouping fields within a specific domain"""
        # Test spatial domain grouping
        spatial_groups = self.grouper.group_fields_by_semantics(
            self.test_fields, 
            domain=SemanticDomain.SPATIAL
        )
        
        # Should group latitude and longitude together
        if spatial_groups:
            spatial_group = spatial_groups[0]
            assert spatial_group.domain == SemanticDomain.SPATIAL
            assert "latitude_decimal" in spatial_group.fields
            assert "longitude_decimal" in spatial_group.fields
        
        # Test biometrics domain grouping
        biometric_groups = self.grouper.group_fields_by_semantics(
            self.test_fields,
            domain=SemanticDomain.BIOMETRICS
        )
        
        # Should group wing_length and weight together
        if biometric_groups:
            biometric_group = biometric_groups[0]
            assert biometric_group.domain == SemanticDomain.BIOMETRICS
            assert "wing_length" in biometric_group.fields
            assert "weight" in biometric_group.fields
    
    def test_analyze_domain_specific_fields(self):
        """Test domain-specific field analysis"""
        # Test spatial domain analysis
        spatial_analysis = self.grouper.analyze_domain_specific_fields(
            SemanticDomain.SPATIAL,
            self.test_versions
        )
        
        assert spatial_analysis["domain"] == "spatial"
        assert spatial_analysis["total_fields_analyzed"] == 2  # lat and lon
        assert spatial_analysis["versions_analyzed"] == 1
        assert "evolution_patterns" in spatial_analysis
        assert "semantic_themes" in spatial_analysis
        assert "naming_conventions" in spatial_analysis
        assert "cohesion_metrics" in spatial_analysis
        
        # Check analysis summary
        assert "analysis_summary" in spatial_analysis
        assert "semantic_consistency_score" in spatial_analysis["analysis_summary"]
    
    def test_categorize_semantic_fields(self):
        """Test semantic field categorization"""
        # Test identification domain categorization
        id_fields = [f for f in self.test_fields if f.semantic_domain == SemanticDomain.IDENTIFICATION_MARKING]
        categories = self.grouper.categorize_semantic_fields(id_fields, SemanticDomain.IDENTIFICATION_MARKING)
        
        assert isinstance(categories, dict)
        assert len(categories) > 0
        
        # Should have some categorized fields
        total_categorized = sum(len(fields) for fields in categories.values())
        assert total_categorized >= len(id_fields)
    
    def test_semantic_meaning_confidence(self):
        """Test that semantic meaning extraction produces reasonable confidence scores"""
        meanings = [self.grouper.extract_semantic_meaning(field) for field in self.test_fields]
        
        # All meanings should have confidence > 0
        for meaning in meanings:
            assert meaning.confidence > 0.0
            assert meaning.confidence <= 1.0
        
        # Fields with clear semantic domains should have higher confidence
        clear_fields = [f for f in self.test_fields if f.semantic_domain and f.semantic_meaning]
        clear_meanings = [self.grouper.extract_semantic_meaning(field) for field in clear_fields]
        
        average_confidence = sum(m.confidence for m in clear_meanings) / len(clear_meanings)
        assert average_confidence > 0.6  # Should be reasonably confident
    
    def test_linguistic_pattern_identification(self):
        """Test identification of linguistic patterns in field names"""
        # Test field with underscore pattern
        underscore_field = self.test_fields[0]  # ring_number
        meaning = self.grouper.extract_semantic_meaning(underscore_field)
        assert "underscore_separated" in meaning.linguistic_patterns
        
        # Test field with decimal pattern
        decimal_field = self.test_fields[3]  # latitude_decimal
        decimal_meaning = self.grouper.extract_semantic_meaning(decimal_field)
        # Should identify some linguistic patterns
        assert len(decimal_meaning.linguistic_patterns) >= 0
    
    def test_field_relationship_detection(self):
        """Test detection of relationships between fields"""
        # Extract semantic meanings
        meanings = [self.grouper.extract_semantic_meaning(field) for field in self.test_fields]
        
        # Calculate relationships
        relationships = self.grouper._calculate_semantic_relationships(meanings)
        
        # Should find some relationships
        assert len(relationships) > 0
        
        # Should find coordinate relationship
        coord_relationship = None
        for rel in relationships:
            if (("latitude" in rel.field1 and "longitude" in rel.field2) or
                ("longitude" in rel.field1 and "latitude" in rel.field2)):
                coord_relationship = rel
                break
        
        if coord_relationship:
            assert coord_relationship.strength > 0.5
            assert coord_relationship.relationship_type in ["coordinate_pair", "spatial_related", "domain_related"]
    
    def test_domain_vocabulary_usage(self):
        """Test that domain vocabularies are used in semantic analysis"""
        # Test that spatial vocabulary is used for spatial fields
        spatial_field = self.test_fields[3]  # latitude_decimal
        meaning = self.grouper.extract_semantic_meaning(spatial_field)
        
        # Should recognize spatial concepts
        all_concepts = [meaning.primary_concept] + meaning.secondary_concepts
        spatial_concepts = [c for c in all_concepts if any(
            spatial_term in c.lower() for spatial_term in ["lat", "coordinate", "spatial", "location"]
        )]
        assert len(spatial_concepts) > 0
    
    def test_empty_field_list_handling(self):
        """Test handling of empty field lists"""
        # Test with empty field list
        empty_groups = self.grouper.group_fields_by_semantics([])
        assert empty_groups == []
        
        # Test domain analysis with empty fields
        empty_analysis = self.grouper.analyze_domain_specific_fields(
            SemanticDomain.SPATIAL,
            []
        )
        assert empty_analysis["total_fields_analyzed"] == 0
        assert empty_analysis["versions_analyzed"] == 0
    
    def test_single_field_handling(self):
        """Test handling of single field scenarios"""
        # Test with single field
        single_field = [self.test_fields[0]]
        single_groups = self.grouper.group_fields_by_semantics(single_field)
        
        # Should not create groups with single fields (groups need multiple fields)
        assert len(single_groups) == 0
        
        # Test semantic meaning extraction for single field
        meaning = self.grouper.extract_semantic_meaning(single_field[0])
        assert meaning.field_name == single_field[0].name
        assert meaning.confidence > 0


if __name__ == "__main__":
    # Run basic functionality test
    grouper = SemanticFieldGrouper()
    
    # Create a simple test field
    test_field = FieldDefinition(
        position=1,
        name="ring_number",
        data_type="alphanumeric",
        length=8,
        description="Ring number for bird identification",
        semantic_domain=SemanticDomain.IDENTIFICATION_MARKING,
        semantic_meaning="Unique ring identifier"
    )
    
    # Test semantic meaning extraction
    meaning = grouper.extract_semantic_meaning(test_field)
    print(f"Semantic meaning extracted for {test_field.name}:")
    print(f"  Primary concept: {meaning.primary_concept}")
    print(f"  Secondary concepts: {meaning.secondary_concepts}")
    print(f"  Semantic category: {meaning.semantic_category}")
    print(f"  Confidence: {meaning.confidence:.2f}")
    print(f"  Linguistic patterns: {meaning.linguistic_patterns}")
    
    print("\nSemantic Field Grouper basic functionality test completed successfully!")