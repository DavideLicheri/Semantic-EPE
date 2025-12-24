"""
Tests for EURING version loading functionality with domain organization
"""
import pytest
import asyncio
from pathlib import Path
from backend.app.services.version_loader import VersionLoaderService
from backend.app.services.skos_manager import SKOSManagerImpl
from backend.app.models.euring_models import SemanticDomain


class TestVersionLoading:
    """Test version loading functionality"""
    
    @pytest.fixture
    def version_loader(self):
        """Create a version loader for testing"""
        return VersionLoaderService("data/euring_versions")
    
    @pytest.fixture
    def skos_manager(self):
        """Create a SKOS manager for testing"""
        return SKOSManagerImpl("data/euring_versions")
    
    @pytest.mark.asyncio
    async def test_load_historical_versions(self, version_loader):
        """Test loading of historical EURING versions with domain organization"""
        version_model = await version_loader.load_all_historical_versions()
        
        # Verify we have versions
        assert len(version_model.versions) > 0
        
        # Verify we have the expected historical versions
        version_ids = {v.id for v in version_model.versions}
        expected_versions = {"euring_1966", "euring_2000", "euring_2020"}
        assert expected_versions.issubset(version_ids)
        
        # Verify versions are sorted by year
        years = [v.year for v in version_model.versions]
        assert years == sorted(years)
        
        # Verify domain organization
        for version in version_model.versions:
            # Check that fields have semantic domains assigned
            fields_with_domains = [f for f in version.field_definitions if f.semantic_domain]
            assert len(fields_with_domains) > 0, f"Version {version.id} has no fields with semantic domains"
            
            # Check that semantic domain mappings exist
            if version.semantic_domains:
                domain_names = {mapping.domain for mapping in version.semantic_domains}
                assert len(domain_names) > 0, f"Version {version.id} has no semantic domain mappings"
        
        # Verify domain evolutions are tracked
        if version_model.domain_evolutions:
            assert len(version_model.domain_evolutions) > 0
            for evolution in version_model.domain_evolutions:
                assert evolution.domain in SemanticDomain
                assert len(evolution.evolution_entries) > 0
    
    @pytest.mark.asyncio
    async def test_version_by_year_range(self, version_loader):
        """Test getting versions by year range"""
        versions = await version_loader.get_versions_by_year_range(1960, 2000)
        
        # Should include 1963 and 2000 versions
        version_years = {v.year for v in versions}
        assert 1963 in version_years
        assert 2000 in version_years
        assert 2024 not in version_years  # Should be excluded
    
    @pytest.mark.asyncio
    async def test_version_by_specific_year(self, version_loader):
        """Test getting version active in a specific year"""
        # Test year 1980 should return 1963 version (latest before 1980)
        version = await version_loader.get_version_by_year(1980)
        assert version is not None
        assert version.year == 1963
        
        # Test year 2010 should return 2000 version
        version = await version_loader.get_version_by_year(2010)
        assert version is not None
        assert version.year == 2000
        
        # Test current year should return 2024 version
        version = await version_loader.get_version_by_year(2024)
        assert version is not None
        assert version.year == 2024
    
    @pytest.mark.asyncio
    async def test_version_statistics(self, version_loader):
        """Test version statistics generation"""
        stats = await version_loader.get_version_statistics()
        
        assert stats["total_versions"] >= 3
        assert stats["year_range"]["earliest"] == 1963
        assert stats["year_range"]["latest"] >= 2024
        assert stats["average_fields"] > 0
        assert "1960s" in stats["versions_by_decade"]
    
    @pytest.mark.asyncio
    async def test_skos_manager_integration(self, skos_manager):
        """Test SKOS manager integration"""
        # Test loading version model
        version_model = await skos_manager.load_version_model()
        assert len(version_model.versions) > 0
        
        # Test getting version characteristics
        characteristics = await skos_manager.get_version_characteristics("euring_1966")
        assert characteristics.version_id == "euring_1966"
        assert characteristics.field_count > 0
        assert characteristics.total_length > 0
        
        # Test version compatibility
        is_compatible = await skos_manager.validate_version_compatibility("euring_1966", "euring_2000")
        assert is_compatible is True
        
        # Test conversion rules
        conversion_rules = await skos_manager.get_conversion_rules("euring_1966", "euring_2000")
        assert conversion_rules.from_version == "euring_1966"
        assert conversion_rules.to_version == "euring_2000"
        assert len(conversion_rules.field_mappings) > 0
    
    @pytest.mark.asyncio
    async def test_domain_field_assignment(self, version_loader):
        """Test automatic field assignment to semantic domains"""
        version_model = await version_loader.load_all_historical_versions()
        
        # Find a version to test
        test_version = next(v for v in version_model.versions if v.id == "euring_2020")
        
        # Check that fields are assigned to appropriate domains
        species_fields = [f for f in test_version.field_definitions 
                         if f.semantic_domain == SemanticDomain.SPECIES]
        assert len(species_fields) > 0, "No species fields found"
        
        # Check that species fields have appropriate names
        species_field_names = [f.name for f in species_fields]
        assert any("species" in name.lower() for name in species_field_names)
        
        # Check identification marking fields
        id_fields = [f for f in test_version.field_definitions 
                    if f.semantic_domain == SemanticDomain.IDENTIFICATION_MARKING]
        assert len(id_fields) > 0, "No identification marking fields found"
        
        # Check that ring fields are in identification domain
        ring_field_names = [f.name for f in id_fields]
        assert any("ring" in name.lower() for name in ring_field_names)
    
    @pytest.mark.asyncio
    async def test_domain_mapping_validation(self, version_loader):
        """Test validation of domain mappings"""
        version_model = await version_loader.load_all_historical_versions()
        
        # Validation should pass without errors
        await version_loader._validate_domain_mappings(version_model.versions)
        
        # Check that all versions have consistent domain mappings
        for version in version_model.versions:
            if version.semantic_domains:
                for domain_mapping in version.semantic_domains:
                    # All mapped fields should exist in version
                    version_field_names = {f.name for f in version.field_definitions}
                    for field_name in domain_mapping.fields:
                        assert field_name in version_field_names, \
                            f"Mapped field {field_name} not found in version {version.id}"
                    
                    # All mapped fields should have correct domain assignment
                    for field_name in domain_mapping.fields:
                        field = next(f for f in version.field_definitions if f.name == field_name)
                        assert field.semantic_domain == domain_mapping.domain, \
                            f"Field {field_name} domain mismatch in version {version.id}"
    
    @pytest.mark.asyncio
    async def test_domain_evolution_tracking(self, version_loader):
        """Test tracking of domain evolution across versions"""
        version_model = await version_loader.load_all_historical_versions()
        
        # Should have domain evolutions
        assert version_model.domain_evolutions is not None
        assert len(version_model.domain_evolutions) > 0
        
        # Check evolution structure
        for evolution in version_model.domain_evolutions:
            assert evolution.domain in SemanticDomain
            assert len(evolution.evolution_entries) > 0
            
            # Check evolution entries are sorted by year
            years = [entry.year for entry in evolution.evolution_entries]
            assert years == sorted(years)
            
            # Check that changes are tracked
            for entry in evolution.evolution_entries:
                assert entry.version is not None
                assert entry.year > 0
                # Changes list can be empty for first version
                assert isinstance(entry.changes, list)
    
    @pytest.mark.asyncio
    async def test_domain_specific_rules_creation(self, version_loader):
        """Test creation of domain-specific validation rules"""
        version_model = await version_loader.load_all_historical_versions()
        
        # Find a version with domain mappings
        test_version = next(v for v in version_model.versions 
                           if v.semantic_domains and len(v.semantic_domains) > 0)
        
        # Check that domain-specific rules are created
        for domain_mapping in test_version.semantic_domains:
            if domain_mapping.domain in [SemanticDomain.IDENTIFICATION_MARKING, 
                                       SemanticDomain.SPATIAL, 
                                       SemanticDomain.TEMPORAL]:
                # These domains should have specific validation rules
                assert len(domain_mapping.domain_specific_rules) > 0, \
                    f"No domain-specific rules for {domain_mapping.domain.value}"
    
    @pytest.mark.asyncio
    async def test_domain_statistics(self, version_loader):
        """Test domain statistics generation"""
        version_model = await version_loader.load_all_historical_versions()
        
        # Test domain statistics for a specific version
        test_version_id = "euring_2020"
        stats = await version_loader.get_domain_statistics_for_version(test_version_id)
        
        assert stats["version_id"] == test_version_id
        assert stats["total_domains"] > 0
        assert stats["total_fields"] > 0
        assert stats["fields_with_domains"] > 0
        
        # Check domain statistics structure
        assert "domain_statistics" in stats
        for domain_name, domain_stats in stats["domain_statistics"].items():
            assert "field_count" in domain_stats
            assert "fields" in domain_stats
            assert "total_length" in domain_stats
            assert "data_types" in domain_stats
            assert domain_stats["field_count"] > 0
    
    @pytest.mark.asyncio
    async def test_reload_with_domain_organization(self, version_loader):
        """Test reloading versions with domain organization"""
        # First load
        version_model1 = await version_loader.load_all_historical_versions()
        
        # Reload
        version_model2 = await version_loader.reload_versions_with_domain_organization()
        
        # Should have same number of versions
        assert len(version_model1.versions) == len(version_model2.versions)
        
        # Should have domain organization in both
        for version in version_model2.versions:
            fields_with_domains = [f for f in version.field_definitions if f.semantic_domain]
            assert len(fields_with_domains) > 0


if __name__ == "__main__":
    # Run a simple test
    async def main():
        loader = VersionLoaderService("data/euring_versions")
        try:
            model = await loader.load_all_historical_versions()
            print(f"Successfully loaded {len(model.versions)} versions")
            
            stats = await loader.get_version_statistics()
            print(f"Statistics: {stats}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(main())