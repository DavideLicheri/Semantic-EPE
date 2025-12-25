"""
SKOS Manager implementation for EURING Code Recognition System
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from ..models.euring_models import (
    EuringVersionModel, EuringVersion, VersionRelationship, 
    ConversionMapping, FieldDefinition, ValidationRule, FormatSpec,
    SemanticDomain, DomainEvolution, DomainCompatibilityMatrix
)
from .interfaces import SKOSManager, VersionCharacteristics, ConversionRules
from ..repositories.skos_repository import SKOSRepository
from .domain_compatibility_assessor import DomainCompatibilityAssessor
from .domain_conversion_service import DomainConversionService


class SKOSManagerImpl(SKOSManager):
    """Concrete implementation of SKOS Manager for EURING versions"""
    
    def __init__(self, data_directory: str = "data/euring_versions"):
        self.repository = SKOSRepository(data_directory)
        self._version_model: Optional[EuringVersionModel] = None
        self._version_cache: Dict[str, EuringVersion] = {}
        self._domain_compatibility_assessor = DomainCompatibilityAssessor()
        self._domain_conversion_service = DomainConversionService()
    async def load_version_model(self) -> EuringVersionModel:
        """Load the complete EURING version model from data files"""
        if self._version_model is not None:
            return self._version_model
            
        # Load versions from repository
        versions = await self.repository.load_all_versions()
        relationships = await self.repository.load_relationships()
        conversion_mappings = await self.repository.load_conversion_mappings()
        
        # Load domain evolutions if available
        domain_evolutions = []
        for domain in SemanticDomain:
            try:
                domain_evolution = await self.repository.load_domain_evolution(domain)
                if domain_evolution:
                    domain_evolutions.append(domain_evolution)
            except Exception:
                # Domain evolution not available, skip
                pass
        
        self._version_model = EuringVersionModel(
            versions=versions,
            relationships=relationships,
            conversion_mappings=conversion_mappings,
            domain_evolutions=domain_evolutions
        )
        
        # Cache versions for quick access
        self._version_cache = {v.id: v for v in versions}
        
        # Initialize domain compatibility assessor
        self._domain_compatibility_assessor.load_versions(versions)
        if domain_evolutions:
            self._domain_compatibility_assessor.load_domain_evolutions(domain_evolutions)
        
        # Initialize domain conversion service
        self._domain_conversion_service.load_versions(versions)
        
        return self._version_model
    
    async def get_version_characteristics(self, version: str) -> VersionCharacteristics:
        """Get characteristics for a specific version"""
        if not self._version_model:
            await self.load_version_model()
            
        if version not in self._version_cache:
            raise ValueError(f"Version {version} not found")
            
        euring_version = self._version_cache[version]
        
        # Extract unique patterns from field definitions
        unique_patterns = []
        for field in euring_version.field_definitions:
            if field.valid_values:
                unique_patterns.extend(field.valid_values[:3])  # Take first 3 as examples
        
        # Extract validation rule expressions
        validation_rules = [rule.rule_expression for rule in euring_version.validation_rules]
        
        return VersionCharacteristics(
            version_id=version,
            field_count=len(euring_version.field_definitions),
            total_length=euring_version.format_specification.total_length,
            unique_patterns=unique_patterns,
            validation_rules=validation_rules
        )
    
    async def get_conversion_rules(self, from_version: str, to_version: str) -> ConversionRules:
        """Get conversion rules between two versions"""
        if not self._version_model:
            await self.load_version_model()
            
        # Find conversion mapping
        conversion_mapping = None
        for mapping in self._version_model.conversion_mappings:
            if mapping.from_version == from_version and mapping.to_version == to_version:
                conversion_mapping = mapping
                break
                
        if not conversion_mapping:
            raise ValueError(f"No conversion mapping found from {from_version} to {to_version}")
        
        # Extract field mappings as dictionaries
        field_mappings = []
        for field_mapping in conversion_mapping.field_mappings:
            field_mappings.append({
                "source_field": field_mapping.source_field,
                "target_field": field_mapping.target_field,
                "transformation_type": field_mapping.transformation_type.value,
                "transformation_function": field_mapping.transformation_function
            })
        
        # Extract transformation functions
        transformation_functions = [
            rule.transformation_expression 
            for rule in conversion_mapping.transformation_rules
        ]
        
        # Calculate compatibility score based on compatibility level
        compatibility_scores = {
            "full": 1.0,
            "partial": 0.7,
            "limited": 0.4,
            "none": 0.0
        }
        compatibility_score = compatibility_scores.get(
            conversion_mapping.compatibility_level.value, 0.0
        )
        
        return ConversionRules(
            from_version=from_version,
            to_version=to_version,
            field_mappings=field_mappings,
            transformation_functions=transformation_functions,
            compatibility_score=compatibility_score
        )
    
    async def validate_version_compatibility(self, from_version: str, to_version: str) -> bool:
        """Check if conversion between versions is possible"""
        if not self._version_model:
            await self.load_version_model()
            
        # Check if both versions exist
        if from_version not in self._version_cache or to_version not in self._version_cache:
            return False
            
        # Check if conversion mapping exists
        for mapping in self._version_model.conversion_mappings:
            if (mapping.from_version == from_version and 
                mapping.to_version == to_version and
                mapping.compatibility_level.value != "none"):
                return True
                
        return False
    
    async def add_version(self, version: EuringVersion) -> None:
        """Add a new version to the model"""
        if not self._version_model:
            await self.load_version_model()
            
        # Check if version already exists
        if version.id in self._version_cache:
            raise ValueError(f"Version {version.id} already exists")
            
        # Add to model and cache
        self._version_model.versions.append(version)
        self._version_cache[version.id] = version
        
        # Persist to repository
        await self.repository.save_version(version)
    
    async def update_version(self, version: EuringVersion) -> None:
        """Update an existing version in the model"""
        if not self._version_model:
            await self.load_version_model()
            
        # Update cache
        self._version_cache[version.id] = version
        
        # Update in model list
        for i, v in enumerate(self._version_model.versions):
            if v.id == version.id:
                self._version_model.versions[i] = version
                break
        
        # Persist to repository
        await self.repository.save_version(version)
    
    async def reload_version_model(self) -> None:
        """Force reload the version model from storage"""
        self._version_model = None
        self._version_cache.clear()
        await self.load_version_model()
    
    async def get_all_versions(self) -> List[EuringVersion]:
        """Get all available EURING versions"""
        if not self._version_model:
            await self.load_version_model()
            
        return self._version_model.versions
    
    async def get_version_by_id(self, version_id: str) -> Optional[EuringVersion]:
        """Get a specific version by ID"""
        if not self._version_model:
            await self.load_version_model()
            
        return self._version_cache.get(version_id)
    
    async def add_relationship(self, relationship: VersionRelationship) -> None:
        """Add a new version relationship"""
        if not self._version_model:
            await self.load_version_model()
            
        self._version_model.relationships.append(relationship)
        await self.repository.save_relationships(self._version_model.relationships)
    
    async def add_conversion_mapping(self, mapping: ConversionMapping) -> None:
        """Add a new conversion mapping"""
        if not self._version_model:
            await self.load_version_model()
            
        self._version_model.conversion_mappings.append(mapping)
        await self.repository.save_conversion_mappings(self._version_model.conversion_mappings)
    
    async def create_domain_conversion_mapping(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Create domain-specific conversion mapping between two versions.
        
        Args:
            domain: The semantic domain to create mapping for
            from_version: Source version for conversion
            to_version: Target version for conversion
            
        Returns:
            Dictionary containing domain conversion mapping information
            
        Validates: Requirements 5.4, 8.5
        """
        if not self._version_model:
            await self.load_version_model()
        
        # Create domain conversion mapping using the domain conversion service
        domain_mapping = await self._domain_conversion_service.create_domain_conversion_mapping(
            domain, from_version, to_version
        )
        
        return {
            'domain': domain.value,
            'from_version': from_version,
            'to_version': to_version,
            'compatibility': domain_mapping.compatibility.value,
            'lossy_conversion': domain_mapping.lossy_conversion,
            'field_mappings': [
                {
                    'source_field': fm.source_field,
                    'target_field': fm.target_field,
                    'transformation_type': fm.transformation_type.value,
                    'transformation_function': fm.transformation_function,
                    'conversion_accuracy': fm.conversion_accuracy
                }
                for fm in domain_mapping.field_mappings
            ],
            'transformation_rules': [
                {
                    'rule_id': tr.rule_id,
                    'source_field': tr.source_field,
                    'target_field': tr.target_field,
                    'transformation_type': tr.transformation_type.value,
                    'transformation_expression': tr.transformation_expression
                }
                for tr in domain_mapping.transformation_rules
            ],
            'conversion_notes': domain_mapping.conversion_notes
        }
    
    async def update_conversion_mapping_with_domain_rules(
        self,
        from_version: str,
        to_version: str
    ) -> ConversionMapping:
        """
        Update existing conversion mapping with domain-specific rules.
        
        Args:
            from_version: Source version for conversion
            to_version: Target version for conversion
            
        Returns:
            Updated ConversionMapping with domain-specific mappings
            
        Validates: Requirements 5.4, 8.5
        """
        if not self._version_model:
            await self.load_version_model()
        
        # Find existing conversion mapping
        conversion_mapping = None
        for mapping in self._version_model.conversion_mappings:
            if mapping.from_version == from_version and mapping.to_version == to_version:
                conversion_mapping = mapping
                break
        
        if not conversion_mapping:
            raise ValueError(f"No conversion mapping found from {from_version} to {to_version}")
        
        # Update with domain-specific mappings
        updated_mapping = await self._domain_conversion_service.update_conversion_mapping_with_domains(
            conversion_mapping
        )
        
        # Save updated mapping
        await self.repository.save_conversion_mappings(self._version_model.conversion_mappings)
        
        return updated_mapping
    
    async def get_domain_conversion_rules(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Get conversion rules specific to a domain between two versions.
        
        Args:
            domain: The semantic domain to get rules for
            from_version: Source version for conversion
            to_version: Target version for conversion
            
        Returns:
            Dictionary containing domain-specific conversion rules
            
        Validates: Requirements 5.4, 8.5
        """
        if not self._version_model:
            await self.load_version_model()
        
        # Get domain conversion mapping
        domain_mapping = await self._domain_conversion_service.get_domain_conversion_mapping(
            domain, from_version, to_version
        )
        
        if not domain_mapping:
            return {
                'domain': domain.value,
                'from_version': from_version,
                'to_version': to_version,
                'available': False,
                'message': 'Domain conversion mapping not available'
            }
        
        # Get transformation rules for this domain
        transformation_rules = await self._domain_conversion_service.get_domain_transformation_rules(
            domain, from_version, to_version
        )
        
        # Get compatibility assessment (handle case where evolution data is not available)
        try:
            compatibility_assessment = await self.analyze_domain_compatibility(
                domain, from_version, to_version
            )
        except ValueError:
            # Domain evolution data not available, create basic assessment
            compatibility_assessment = {
                'domain': domain.value,
                'from_version': from_version,
                'to_version': to_version,
                'compatibility_level': domain_mapping.compatibility.value,
                'is_lossy': domain_mapping.lossy_conversion,
                'assessment_method': 'basic'
            }
        
        return {
            'domain': domain.value,
            'from_version': from_version,
            'to_version': to_version,
            'available': True,
            'compatibility_level': domain_mapping.compatibility.value,
            'lossy_conversion': domain_mapping.lossy_conversion,
            'field_mappings': [
                {
                    'source_field': fm.source_field,
                    'target_field': fm.target_field,
                    'transformation_type': fm.transformation_type.value,
                    'transformation_function': fm.transformation_function,
                    'conversion_accuracy': fm.conversion_accuracy,
                    'semantic_domain': fm.semantic_domain.value if fm.semantic_domain else None
                }
                for fm in domain_mapping.field_mappings
            ],
            'transformation_rules': [
                {
                    'rule_id': tr.rule_id,
                    'source_field': tr.source_field,
                    'target_field': tr.target_field,
                    'transformation_type': tr.transformation_type.value,
                    'transformation_expression': tr.transformation_expression,
                    'conditions': tr.conditions
                }
                for tr in transformation_rules
            ],
            'conversion_notes': domain_mapping.conversion_notes,
            'compatibility_assessment': compatibility_assessment
        }
    
    async def assess_all_domain_compatibility_levels(
        self,
        from_version: str,
        to_version: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Assess compatibility levels for all domains between two versions.
        
        Args:
            from_version: Source version for conversion
            to_version: Target version for conversion
            
        Returns:
            Dictionary mapping domain names to their compatibility assessments
            
        Validates: Requirements 8.5
        """
        if not self._version_model:
            await self.load_version_model()
        
        domain_assessments = {}
        
        for domain in SemanticDomain:
            try:
                compatibility_level = await self._domain_conversion_service.assess_domain_compatibility_level(
                    domain, from_version, to_version
                )
                
                domain_assessment = await self.analyze_domain_compatibility(
                    domain, from_version, to_version
                )
                
                domain_assessments[domain.value] = {
                    'compatibility_level': compatibility_level.value,
                    'detailed_assessment': domain_assessment
                }
                
            except Exception as e:
                domain_assessments[domain.value] = {
                    'compatibility_level': 'error',
                    'error': str(e),
                    'detailed_assessment': None
                }
        
        return domain_assessments
    
    async def get_domain_evolution(self, domain: SemanticDomain) -> DomainEvolution:
        """Get evolution data for a specific domain"""
        if not self._version_model:
            await self.load_version_model()
        
        # Try to get from loaded model first
        if self._version_model.domain_evolutions:
            for evolution in self._version_model.domain_evolutions:
                if evolution.domain == domain:
                    return evolution
        
        # If not found, try to load from repository
        domain_evolution = await self.repository.load_domain_evolution(domain)
        if domain_evolution:
            return domain_evolution
        
        raise ValueError(f"Domain evolution not found for {domain.value}")
    
    async def analyze_domain_compatibility(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Analyze compatibility between versions for a specific domain"""
        if not self._version_model:
            await self.load_version_model()
        
        # Use the domain compatibility assessor
        result = await self._domain_compatibility_assessor.assess_domain_compatibility(
            domain=domain,
            from_version=from_version,
            to_version=to_version,
            detailed_analysis=True
        )
        
        return dict(result)
    
    async def get_semantic_domains(self) -> List[SemanticDomain]:
        """Get list of available semantic domains"""
        return list(SemanticDomain)
    
    async def get_domain_specific_version_characteristics(
        self, 
        version: str, 
        domain: SemanticDomain
    ) -> Dict[str, Any]:
        """Get version characteristics specific to a semantic domain"""
        if not self._version_model:
            await self.load_version_model()
            
        if version not in self._version_cache:
            raise ValueError(f"Version {version} not found")
            
        euring_version = self._version_cache[version]
        
        # Filter fields by domain
        domain_fields = [
            field for field in euring_version.field_definitions
            if field.semantic_domain == domain
        ]
        
        # Extract domain-specific patterns
        domain_patterns = []
        for field in domain_fields:
            if field.valid_values:
                domain_patterns.extend(field.valid_values[:3])  # Take first 3 as examples
        
        # Extract domain-specific validation rules
        domain_validation_rules = [
            rule.rule_expression for rule in euring_version.validation_rules
            if any(field.name in rule.rule_expression for field in domain_fields)
        ]
        
        # Get semantic domain mapping if available
        domain_mapping = None
        if euring_version.semantic_domains:
            for mapping in euring_version.semantic_domains:
                if mapping.domain == domain:
                    domain_mapping = mapping
                    break
        
        return {
            "version_id": version,
            "domain": domain.value,
            "field_count": len(domain_fields),
            "fields": [
                {
                    "name": field.name,
                    "position": field.position,
                    "data_type": field.data_type,
                    "length": field.length,
                    "description": field.description,
                    "semantic_meaning": field.semantic_meaning,
                    "valid_values": field.valid_values[:5] if field.valid_values else None  # First 5 examples
                }
                for field in domain_fields
            ],
            "unique_patterns": domain_patterns,
            "validation_rules": domain_validation_rules,
            "domain_specific_rules": [
                rule.rule_expression for rule in domain_mapping.domain_specific_rules
            ] if domain_mapping else [],
            "evolution_notes": [
                note for field in domain_fields 
                for note in (field.evolution_notes or [])
            ]
        }
    
    async def get_all_domain_characteristics(self, version: str) -> Dict[SemanticDomain, Dict[str, Any]]:
        """Get characteristics for all domains in a specific version"""
        if not self._version_model:
            await self.load_version_model()
            
        domain_characteristics = {}
        
        for domain in SemanticDomain:
            try:
                characteristics = await self.get_domain_specific_version_characteristics(version, domain)
                if characteristics["field_count"] > 0:  # Only include domains with fields
                    domain_characteristics[domain] = characteristics
            except Exception:
                # Domain not present in this version, skip
                continue
                
        return domain_characteristics
    
    async def get_domain_field_mappings(
        self, 
        domain: SemanticDomain, 
        from_version: str, 
        to_version: str
    ) -> List[Dict[str, Any]]:
        """Get field mappings for a specific domain between two versions"""
        if not self._version_model:
            await self.load_version_model()
        
        # Find conversion mapping
        conversion_mapping = None
        for mapping in self._version_model.conversion_mappings:
            if mapping.from_version == from_version and mapping.to_version == to_version:
                conversion_mapping = mapping
                break
                
        if not conversion_mapping:
            raise ValueError(f"No conversion mapping found from {from_version} to {to_version}")
        
        # Filter field mappings by domain
        domain_field_mappings = []
        for field_mapping in conversion_mapping.field_mappings:
            if field_mapping.semantic_domain == domain:
                domain_field_mappings.append({
                    "source_field": field_mapping.source_field,
                    "target_field": field_mapping.target_field,
                    "transformation_type": field_mapping.transformation_type.value,
                    "transformation_function": field_mapping.transformation_function,
                    "conversion_accuracy": field_mapping.conversion_accuracy,
                    "semantic_domain": domain.value
                })
        
        # Also check domain-specific mappings if available
        if conversion_mapping.domain_mappings:
            for domain_mapping in conversion_mapping.domain_mappings:
                if domain_mapping.domain == domain:
                    for field_mapping in domain_mapping.field_mappings:
                        domain_field_mappings.append({
                            "source_field": field_mapping.source_field,
                            "target_field": field_mapping.target_field,
                            "transformation_type": field_mapping.transformation_type.value,
                            "transformation_function": field_mapping.transformation_function,
                            "conversion_accuracy": field_mapping.conversion_accuracy,
                            "semantic_domain": domain.value,
                            "domain_specific": True,
                            "lossy_conversion": domain_mapping.lossy_conversion,
                            "conversion_notes": domain_mapping.conversion_notes
                        })
                    break
        
        return domain_field_mappings
    
    async def get_domain_evolution_summary(self, domain: SemanticDomain) -> Dict[str, Any]:
        """Get a summary of domain evolution across all versions"""
        if not self._version_model:
            await self.load_version_model()
        
        try:
            domain_evolution = await self.get_domain_evolution(domain)
        except ValueError:
            # Domain evolution not available
            return {
                "domain": domain.value,
                "evolution_available": False,
                "message": "Domain evolution data not available"
            }
        
        # Calculate summary statistics
        total_changes = sum(len(entry.changes) for entry in domain_evolution.evolution_entries)
        versions_with_changes = len(domain_evolution.evolution_entries)
        
        # Categorize changes by type
        change_types = {}
        for entry in domain_evolution.evolution_entries:
            for change in entry.changes:
                change_type = change.change_type.value
                if change_type not in change_types:
                    change_types[change_type] = 0
                change_types[change_type] += 1
        
        # Get compatibility overview
        compatibility_overview = {}
        if domain_evolution.compatibility_matrix:
            for (from_ver, to_ver), level in domain_evolution.compatibility_matrix.compatibility_map.items():
                level_str = level.value if hasattr(level, 'value') else str(level)
                if level_str not in compatibility_overview:
                    compatibility_overview[level_str] = 0
                compatibility_overview[level_str] += 1
        
        return {
            "domain": domain.value,
            "evolution_available": True,
            "total_changes": total_changes,
            "versions_with_changes": versions_with_changes,
            "change_types": change_types,
            "compatibility_overview": compatibility_overview,
            "evolution_entries": [
                {
                    "version": entry.version,
                    "year": entry.year,
                    "changes_count": len(entry.changes),
                    "fields_added": entry.fields_added or [],
                    "fields_removed": entry.fields_removed or [],
                    "fields_modified": entry.fields_modified or [],
                    "semantic_notes": entry.semantic_notes[:3] if entry.semantic_notes else []  # First 3 notes
                }
                for entry in sorted(domain_evolution.evolution_entries, key=lambda e: e.year)
            ]
        }
    
    async def compare_domain_between_versions(
        self, 
        domain: SemanticDomain, 
        version1: str, 
        version2: str
    ) -> Dict[str, Any]:
        """Compare a specific domain between two versions"""
        if not self._version_model:
            await self.load_version_model()
        
        # Get domain characteristics for both versions
        try:
            v1_characteristics = await self.get_domain_specific_version_characteristics(version1, domain)
        except ValueError:
            v1_characteristics = {"field_count": 0, "fields": []}
        
        try:
            v2_characteristics = await self.get_domain_specific_version_characteristics(version2, domain)
        except ValueError:
            v2_characteristics = {"field_count": 0, "fields": []}
        
        # Compare field counts
        field_count_diff = v2_characteristics["field_count"] - v1_characteristics["field_count"]
        
        # Compare fields
        v1_field_names = {field["name"] for field in v1_characteristics["fields"]}
        v2_field_names = {field["name"] for field in v2_characteristics["fields"]}
        
        added_fields = v2_field_names - v1_field_names
        removed_fields = v1_field_names - v2_field_names
        common_fields = v1_field_names & v2_field_names
        
        # Check for field modifications in common fields
        modified_fields = []
        for field_name in common_fields:
            v1_field = next(f for f in v1_characteristics["fields"] if f["name"] == field_name)
            v2_field = next(f for f in v2_characteristics["fields"] if f["name"] == field_name)
            
            modifications = []
            if v1_field["data_type"] != v2_field["data_type"]:
                modifications.append(f"data_type: {v1_field['data_type']} -> {v2_field['data_type']}")
            if v1_field["length"] != v2_field["length"]:
                modifications.append(f"length: {v1_field['length']} -> {v2_field['length']}")
            if v1_field["description"] != v2_field["description"]:
                modifications.append("description changed")
            
            if modifications:
                modified_fields.append({
                    "field_name": field_name,
                    "modifications": modifications
                })
        
        # Get compatibility assessment if available
        compatibility_info = None
        try:
            compatibility_info = await self.analyze_domain_compatibility(domain, version1, version2)
        except Exception:
            # Compatibility analysis not available
            pass
        
        return {
            "domain": domain.value,
            "version1": version1,
            "version2": version2,
            "field_count_difference": field_count_diff,
            "added_fields": list(added_fields),
            "removed_fields": list(removed_fields),
            "modified_fields": modified_fields,
            "common_fields_count": len(common_fields),
            "compatibility_info": compatibility_info,
            "summary": {
                "has_changes": field_count_diff != 0 or len(added_fields) > 0 or len(removed_fields) > 0 or len(modified_fields) > 0,
                "change_type": "expansion" if field_count_diff > 0 else "reduction" if field_count_diff < 0 else "modification" if len(modified_fields) > 0 else "no_change"
            }
        }