"""
Version Loader Service for EURING Code Recognition System
Handles loading and validation of historical EURING versions with domain organization
"""
import asyncio
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
from ..models.euring_models import (
    EuringVersion, EuringVersionModel, SemanticDomain, FieldDefinition,
    SemanticDomainMapping, ValidationRule, DomainEvolution, DomainEvolutionEntry,
    DomainChange, DomainChangeType, DomainCompatibilityLevel, DomainCompatibilityMatrix
)
from .skos_manager import SKOSManagerImpl
from ..repositories.skos_repository import SKOSRepository


class VersionLoaderService:
    """Service for loading and validating historical EURING versions with domain organization"""
    
    def __init__(self, data_directory: str = "data/euring_versions"):
        self.skos_manager = SKOSManagerImpl(data_directory)
        self.repository = SKOSRepository(data_directory)
        self._domain_field_patterns = self._initialize_domain_field_patterns()
        self._loaded_versions: Dict[str, EuringVersion] = {}
        
    def _initialize_domain_field_patterns(self) -> Dict[SemanticDomain, List[str]]:
        """Initialize patterns for automatic domain assignment"""
        return {
            SemanticDomain.IDENTIFICATION_MARKING: [
                r"ring", r"number", r"scheme", r"metal", r"mark", r"verify", r"other_marks"
            ],
            SemanticDomain.SPECIES: [
                r"species", r"code", r"finder", r"mentioned"
            ],
            SemanticDomain.DEMOGRAPHICS: [
                r"age", r"sex", r"adult", r"juvenile", r"male", r"female"
            ],
            SemanticDomain.TEMPORAL: [
                r"date", r"time", r"current", r"first"
            ],
            SemanticDomain.SPATIAL: [
                r"lat", r"lon", r"coordinate", r"accuracy", r"region", r"place"
            ],
            SemanticDomain.BIOMETRICS: [
                r"wing", r"weight", r"bill", r"tarsus", r"fat", r"muscle", r"moult"
            ],
            SemanticDomain.METHODOLOGY: [
                r"method", r"condition", r"status", r"catch", r"lure", r"manipulat", r"moved"
            ]
        }
        
    async def load_all_historical_versions(self) -> EuringVersionModel:
        """Load all historical EURING versions from 1963 to present with domain organization"""
        try:
            # Load the complete version model
            version_model = await self.skos_manager.load_version_model()
            
            # Assign fields to semantic domains for each version
            for version in version_model.versions:
                await self._assign_fields_to_domains(version)
                await self._create_domain_mappings(version)
                self._loaded_versions[version.id] = version
            
            # Validate domain mappings
            await self._validate_domain_mappings(version_model.versions)
            
            # Track domain evolution across versions
            domain_evolutions = await self._track_domain_evolution(version_model.versions)
            version_model.domain_evolutions = domain_evolutions
            
            # Validate that we have versions spanning the required period
            await self._validate_historical_coverage(version_model.versions)
            
            # Validate version integrity
            await self._validate_version_integrity(version_model.versions)
            
            return version_model
            
        except Exception as e:
            raise RuntimeError(f"Failed to load historical versions: {e}")
    
    async def get_versions_by_year_range(self, start_year: int, end_year: int) -> List[EuringVersion]:
        """Get EURING versions within a specific year range"""
        version_model = await self.skos_manager.load_version_model()
        
        return [
            version for version in version_model.versions
            if start_year <= version.year <= end_year
        ]
    
    async def get_version_by_year(self, year: int) -> Optional[EuringVersion]:
        """Get the EURING version that was active in a specific year"""
        version_model = await self.skos_manager.load_version_model()
        
        # Find the version that was active in the given year
        # This assumes versions are active from their year until the next version
        active_version = None
        for version in sorted(version_model.versions, key=lambda v: v.year):
            if version.year <= year:
                active_version = version
            else:
                break
                
        return active_version
    
    async def validate_version_data(self, version: EuringVersion) -> Dict[str, List[str]]:
        """Validate a single version's data integrity"""
        errors = []
        warnings = []
        
        # Validate basic structure
        if not version.id:
            errors.append("Version ID is required")
        if not version.name:
            errors.append("Version name is required")
        if version.year < 1963 or version.year > 2030:
            warnings.append(f"Version year {version.year} is outside expected range (1963-2030)")
        
        # Validate field definitions
        if not version.field_definitions:
            errors.append("Version must have at least one field definition")
        else:
            positions = [field.position for field in version.field_definitions]
            if len(positions) != len(set(positions)):
                errors.append("Field positions must be unique")
            
            total_calculated_length = sum(field.length for field in version.field_definitions)
            if total_calculated_length != version.format_specification.total_length:
                warnings.append(
                    f"Calculated total length ({total_calculated_length}) "
                    f"differs from specified total length ({version.format_specification.total_length})"
                )
        
        # Validate validation rules
        field_names = {field.name for field in version.field_definitions}
        for rule in version.validation_rules:
            if rule.field_name not in field_names:
                errors.append(f"Validation rule references unknown field: {rule.field_name}")
        
        return {
            "errors": errors,
            "warnings": warnings
        }
    
    async def get_version_statistics(self) -> Dict[str, any]:
        """Get statistics about loaded versions"""
        version_model = await self.skos_manager.load_version_model()
        
        if not version_model.versions:
            return {
                "total_versions": 0,
                "year_range": None,
                "average_fields": 0,
                "total_relationships": 0,
                "total_conversion_mappings": 0
            }
        
        years = [v.year for v in version_model.versions]
        field_counts = [len(v.field_definitions) for v in version_model.versions]
        
        return {
            "total_versions": len(version_model.versions),
            "year_range": {
                "earliest": min(years),
                "latest": max(years)
            },
            "average_fields": sum(field_counts) / len(field_counts),
            "total_relationships": len(version_model.relationships),
            "total_conversion_mappings": len(version_model.conversion_mappings),
            "versions_by_decade": self._group_versions_by_decade(version_model.versions)
        }
    
    async def reload_versions(self) -> EuringVersionModel:
        """Force reload of all version data from storage"""
        # Clear the cached model
        self.skos_manager._version_model = None
        self.skos_manager._version_cache = {}
        
        # Reload from storage
        return await self.load_all_historical_versions()
    
    # Private helper methods
    
    async def _validate_historical_coverage(self, versions: List[EuringVersion]) -> None:
        """Validate that we have adequate historical coverage"""
        if not versions:
            raise ValueError("No EURING versions found")
        
        years = [v.year for v in versions]
        earliest_year = min(years)
        latest_year = max(years)
        
        if earliest_year > 1966:
            raise ValueError(f"Missing early versions: earliest version is from {earliest_year}, expected 1966")
        
        # Check for reasonable coverage (at least one version per decade)
        decades_covered = set((year // 10) * 10 for year in years)
        expected_decades = set(range(1960, 2030, 10))
        
        missing_decades = expected_decades - decades_covered
        if missing_decades:
            print(f"Warning: Missing versions for decades: {sorted(missing_decades)}")
    
    async def _validate_version_integrity(self, versions: List[EuringVersion]) -> None:
        """Validate integrity of all versions"""
        validation_results = []
        
        for version in versions:
            result = await self.validate_version_data(version)
            if result["errors"]:
                validation_results.append(f"Version {version.id}: {', '.join(result['errors'])}")
        
        if validation_results:
            raise ValueError(f"Version validation failed: {'; '.join(validation_results)}")
    
    def _group_versions_by_decade(self, versions: List[EuringVersion]) -> Dict[str, int]:
        """Group versions by decade for statistics"""
        decades = {}
        for version in versions:
            decade = (version.year // 10) * 10
            decade_key = f"{decade}s"
            decades[decade_key] = decades.get(decade_key, 0) + 1
        
        return decades
    
    # ========================================
    # DOMAIN ORGANIZATION METHODS
    # ========================================
    
    async def _assign_fields_to_domains(self, version: EuringVersion) -> None:
        """Assign fields to semantic domains based on patterns and existing assignments"""
        import re
        
        for field in version.field_definitions:
            # Skip if already assigned
            if field.semantic_domain:
                continue
                
            # Try to assign based on field name and description patterns
            assigned_domain = self._determine_field_domain(field)
            if assigned_domain:
                field.semantic_domain = assigned_domain
                
        # Validate assignments
        await self._validate_field_domain_assignments(version)
    
    def _determine_field_domain(self, field: FieldDefinition) -> Optional[SemanticDomain]:
        """Determine semantic domain for a field based on patterns"""
        import re
        
        field_text = f"{field.name} {field.description}".lower()
        
        # Score each domain based on pattern matches
        domain_scores = {}
        for domain, patterns in self._domain_field_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, field_text):
                    score += 1
            if score > 0:
                domain_scores[domain] = score
        
        # Return domain with highest score, if any
        if domain_scores:
            return max(domain_scores.keys(), key=lambda d: domain_scores[d])
        
        # Fallback to methodology for unclassified fields
        return SemanticDomain.METHODOLOGY
    
    async def _create_domain_mappings(self, version: EuringVersion) -> None:
        """Create semantic domain mappings for a version"""
        domain_mappings = {}
        
        # Group fields by domain
        for field in version.field_definitions:
            if field.semantic_domain:
                domain = field.semantic_domain
                if domain not in domain_mappings:
                    domain_mappings[domain] = {
                        'fields': [],
                        'domain_specific_rules': []
                    }
                domain_mappings[domain]['fields'].append(field.name)
        
        # Create domain-specific validation rules
        for domain, mapping_data in domain_mappings.items():
            domain_rules = await self._create_domain_specific_rules(
                domain, mapping_data['fields'], version
            )
            mapping_data['domain_specific_rules'] = domain_rules
        
        # Convert to SemanticDomainMapping objects
        semantic_mappings = []
        for domain, mapping_data in domain_mappings.items():
            mapping = SemanticDomainMapping(
                domain=domain,
                fields=mapping_data['fields'],
                domain_specific_rules=mapping_data['domain_specific_rules']
            )
            semantic_mappings.append(mapping)
        
        version.semantic_domains = semantic_mappings
    
    async def _create_domain_specific_rules(
        self, 
        domain: SemanticDomain, 
        field_names: List[str], 
        version: EuringVersion
    ) -> List[ValidationRule]:
        """Create domain-specific validation rules"""
        domain_rules = []
        
        # Create rules based on domain type
        if domain == SemanticDomain.IDENTIFICATION_MARKING:
            # Ring number validation rules
            ring_fields = [f for f in field_names if 'ring' in f.lower()]
            for ring_field in ring_fields:
                domain_rules.append(ValidationRule(
                    field_name=ring_field,
                    rule_type="format",
                    rule_expression="^[A-Z]{2,3}[0-9]{4,5}$",
                    error_message=f"Invalid ring number format in {ring_field}"
                ))
        
        elif domain == SemanticDomain.SPATIAL:
            # Coordinate validation rules
            lat_fields = [f for f in field_names if 'lat' in f.lower()]
            lon_fields = [f for f in field_names if 'lon' in f.lower()]
            
            for lat_field in lat_fields:
                domain_rules.append(ValidationRule(
                    field_name=lat_field,
                    rule_type="range",
                    rule_expression="-90 <= value <= 90",
                    error_message=f"Latitude {lat_field} must be between -90 and 90"
                ))
            
            for lon_field in lon_fields:
                domain_rules.append(ValidationRule(
                    field_name=lon_field,
                    rule_type="range",
                    rule_expression="-180 <= value <= 180",
                    error_message=f"Longitude {lon_field} must be between -180 and 180"
                ))
        
        elif domain == SemanticDomain.TEMPORAL:
            # Date validation rules
            date_fields = [f for f in field_names if 'date' in f.lower()]
            for date_field in date_fields:
                domain_rules.append(ValidationRule(
                    field_name=date_field,
                    rule_type="format",
                    rule_expression="^[0-3][0-9][0-1][0-9][0-9]{4}$",
                    error_message=f"Invalid date format in {date_field}"
                ))
        
        return domain_rules
    
    async def _validate_domain_mappings(self, versions: List[EuringVersion]) -> None:
        """Validate domain mappings across all versions"""
        validation_errors = []
        
        for version in versions:
            # Check that all fields are assigned to domains
            unassigned_fields = [
                field.name for field in version.field_definitions 
                if not field.semantic_domain
            ]
            if unassigned_fields:
                validation_errors.append(
                    f"Version {version.id}: Unassigned fields to domains: {unassigned_fields}"
                )
            
            # Validate domain mappings consistency
            if version.semantic_domains:
                for domain_mapping in version.semantic_domains:
                    # Check that all mapped fields exist in version
                    version_field_names = {f.name for f in version.field_definitions}
                    missing_fields = set(domain_mapping.fields) - version_field_names
                    if missing_fields:
                        validation_errors.append(
                            f"Version {version.id}, Domain {domain_mapping.domain.value}: "
                            f"Mapped fields not found in version: {missing_fields}"
                        )
                    
                    # Check that mapped fields have correct domain assignment
                    for field_name in domain_mapping.fields:
                        field = next((f for f in version.field_definitions if f.name == field_name), None)
                        if field and field.semantic_domain != domain_mapping.domain:
                            validation_errors.append(
                                f"Version {version.id}: Field {field_name} domain mismatch - "
                                f"field has {field.semantic_domain}, mapping has {domain_mapping.domain}"
                            )
        
        if validation_errors:
            raise ValueError(f"Domain mapping validation failed: {'; '.join(validation_errors)}")
    
    async def _track_domain_evolution(self, versions: List[EuringVersion]) -> List[DomainEvolution]:
        """Track domain evolution across versions"""
        # Sort versions by year
        sorted_versions = sorted(versions, key=lambda v: v.year)
        
        # Track evolution for each domain
        domain_evolutions = []
        for domain in SemanticDomain:
            evolution = await self._analyze_domain_evolution_across_versions(domain, sorted_versions)
            if evolution.evolution_entries:  # Only include domains with evolution data
                domain_evolutions.append(evolution)
        
        return domain_evolutions
    
    async def _analyze_domain_evolution_across_versions(
        self, 
        domain: SemanticDomain, 
        sorted_versions: List[EuringVersion]
    ) -> DomainEvolution:
        """Analyze evolution of a specific domain across versions"""
        evolution_entries = []
        compatibility_matrix = DomainCompatibilityMatrix(domain=domain)
        
        # Track fields for this domain across versions
        previous_fields = set()
        
        for i, version in enumerate(sorted_versions):
            # Get fields for this domain in current version
            current_fields = {
                field.name for field in version.field_definitions 
                if field.semantic_domain == domain
            }
            
            if not current_fields:
                continue  # Skip versions without fields for this domain
            
            # Calculate changes from previous version
            changes = []
            fields_added = []
            fields_removed = []
            fields_modified = []
            
            if i > 0:  # Not the first version
                added = current_fields - previous_fields
                removed = previous_fields - current_fields
                common = current_fields & previous_fields
                
                fields_added = list(added)
                fields_removed = list(removed)
                
                # Create change objects
                for field_name in added:
                    changes.append(DomainChange(
                        change_type=DomainChangeType.ADDED,
                        field_name=field_name,
                        new_value=field_name,
                        semantic_impact=f"Added {field_name} to {domain.value}",
                        compatibility_impact=DomainCompatibilityLevel.PARTIAL
                    ))
                
                for field_name in removed:
                    changes.append(DomainChange(
                        change_type=DomainChangeType.REMOVED,
                        field_name=field_name,
                        previous_value=field_name,
                        semantic_impact=f"Removed {field_name} from {domain.value}",
                        compatibility_impact=DomainCompatibilityLevel.LOSSY
                    ))
                
                # Check for modifications in common fields
                for field_name in common:
                    current_field = next(f for f in version.field_definitions if f.name == field_name)
                    prev_version = sorted_versions[i-1]
                    prev_field = next((f for f in prev_version.field_definitions if f.name == field_name), None)
                    
                    if prev_field and self._field_has_changed(prev_field, current_field):
                        fields_modified.append(field_name)
                        changes.append(DomainChange(
                            change_type=DomainChangeType.MODIFIED,
                            field_name=field_name,
                            previous_value=f"{prev_field.data_type}({prev_field.length})",
                            new_value=f"{current_field.data_type}({current_field.length})",
                            semantic_impact=f"Modified {field_name} in {domain.value}",
                            compatibility_impact=DomainCompatibilityLevel.PARTIAL
                        ))
            
            # Create evolution entry
            entry = DomainEvolutionEntry(
                version=version.id,
                year=version.year,
                changes=changes,
                field_mappings=[],  # Will be populated later if needed
                semantic_notes=[
                    f"Domain {domain.value} has {len(current_fields)} fields in {version.id}",
                    f"Changes: +{len(fields_added)} -{len(fields_removed)} ~{len(fields_modified)}"
                ],
                fields_added=fields_added,
                fields_removed=fields_removed,
                fields_modified=fields_modified
            )
            evolution_entries.append(entry)
            
            # Update compatibility matrix
            if i > 0:
                prev_version = sorted_versions[i-1]
                compatibility_level = self._calculate_domain_compatibility_level(
                    len(fields_added), len(fields_removed), len(fields_modified)
                )
                compatibility_matrix.set_compatibility(
                    prev_version.id, version.id, compatibility_level
                )
            
            previous_fields = current_fields
        
        return DomainEvolution(
            domain=domain,
            evolution_entries=evolution_entries,
            compatibility_matrix=compatibility_matrix
        )
    
    def _field_has_changed(self, field1: FieldDefinition, field2: FieldDefinition) -> bool:
        """Check if a field has changed between versions"""
        return (
            field1.data_type != field2.data_type or
            field1.length != field2.length or
            field1.valid_values != field2.valid_values or
            field1.description != field2.description
        )
    
    def _calculate_domain_compatibility_level(
        self, 
        added_count: int, 
        removed_count: int, 
        modified_count: int
    ) -> DomainCompatibilityLevel:
        """Calculate compatibility level based on changes"""
        total_changes = added_count + removed_count + modified_count
        
        if total_changes == 0:
            return DomainCompatibilityLevel.FULL
        elif removed_count == 0 and modified_count == 0:
            return DomainCompatibilityLevel.PARTIAL  # Only additions
        elif removed_count > 0:
            return DomainCompatibilityLevel.LOSSY  # Data loss possible
        else:
            return DomainCompatibilityLevel.PARTIAL  # Modifications only
    
    async def _validate_field_domain_assignments(self, version: EuringVersion) -> None:
        """Validate that field domain assignments are reasonable"""
        validation_warnings = []
        
        # Check for potential misassignments
        for field in version.field_definitions:
            if field.semantic_domain:
                expected_domain = self._determine_field_domain(field)
                if expected_domain and expected_domain != field.semantic_domain:
                    validation_warnings.append(
                        f"Version {version.id}: Field {field.name} assigned to "
                        f"{field.semantic_domain.value} but patterns suggest {expected_domain.value}"
                    )
        
        # Log warnings but don't fail validation
        if validation_warnings:
            print(f"Domain assignment warnings: {'; '.join(validation_warnings)}")
    
    async def reload_versions_with_domain_organization(self) -> EuringVersionModel:
        """Force reload of all version data with domain organization"""
        # Clear caches
        self.skos_manager._version_model = None
        self.skos_manager._version_cache = {}
        self._loaded_versions = {}
        
        # Reload with domain organization
        return await self.load_all_historical_versions()
    
    async def update_version_domain_mappings(self, version_id: str) -> None:
        """Update domain mappings for a specific version"""
        if version_id not in self._loaded_versions:
            raise ValueError(f"Version {version_id} not loaded")
        
        version = self._loaded_versions[version_id]
        
        # Re-assign fields to domains
        await self._assign_fields_to_domains(version)
        
        # Re-create domain mappings
        await self._create_domain_mappings(version)
        
        # Save updated version
        await self.repository.save_version(version)
        
        print(f"Updated domain mappings for version {version_id}")
    
    async def get_domain_statistics_for_version(self, version_id: str) -> Dict[str, any]:
        """Get domain statistics for a specific version"""
        if version_id not in self._loaded_versions:
            raise ValueError(f"Version {version_id} not loaded")
        
        version = self._loaded_versions[version_id]
        domain_stats = {}
        
        # Count fields by domain
        for domain in SemanticDomain:
            domain_fields = [
                field for field in version.field_definitions 
                if field.semantic_domain == domain
            ]
            
            if domain_fields:
                domain_stats[domain.value] = {
                    "field_count": len(domain_fields),
                    "fields": [field.name for field in domain_fields],
                    "total_length": sum(field.length for field in domain_fields),
                    "data_types": list(set(field.data_type for field in domain_fields))
                }
        
        return {
            "version_id": version_id,
            "total_domains": len(domain_stats),
            "domain_statistics": domain_stats,
            "total_fields": len(version.field_definitions),
            "fields_with_domains": len([
                f for f in version.field_definitions if f.semantic_domain
            ])
        }