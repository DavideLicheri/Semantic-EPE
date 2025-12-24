"""
SKOS Repository for EURING Code Recognition System
Handles data persistence and retrieval for EURING versions and relationships
"""
import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from ..models.euring_models import (
    EuringVersion, VersionRelationship, ConversionMapping,
    FieldDefinition, ValidationRule, FormatSpec, TransformationRule,
    FieldMapping, TransformationType, CompatibilityLevel,
    SemanticDomain, SemanticDomainDefinition, DomainEvolution,
    DomainEvolutionEntry, DomainCompatibilityMatrix, DomainChange,
    DomainCompatibilityLevel, EuringVersionModel
)


class SKOSRepository:
    """Repository for SKOS data persistence and retrieval"""
    
    def __init__(self, data_directory: str = "data/euring_versions"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for domain organization
        self.domains_directory = self.data_directory / "domains"
        self.domains_directory.mkdir(exist_ok=True)
        
        self.domain_evolutions_directory = self.data_directory / "domain_evolutions"
        self.domain_evolutions_directory.mkdir(exist_ok=True)
        
    async def save_version(self, version: EuringVersion) -> None:
        """Save an EURING version to storage"""
        versions_dir = self.data_directory / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        version_file = versions_dir / f"{version.id}.json"
        version_data = version.model_dump()
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False, default=str)
    
    async def load_version(self, version_id: str) -> Optional[EuringVersion]:
        """Load a specific EURING version from storage"""
        version_file = self.data_directory / "versions" / f"{version_id}.json"
        
        if not version_file.exists():
            return None
            
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
                return EuringVersion(**version_data)
        except Exception as e:
            print(f"Error loading version {version_id}: {e}")
            return None
    
    async def load_all_versions(self) -> List[EuringVersion]:
        """Load all EURING versions from storage"""
        versions = []
        versions_dir = self.data_directory / "versions"
        
        if not versions_dir.exists():
            return []
            
        for version_file in versions_dir.glob("*.json"):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    version = EuringVersion(**version_data)
                    versions.append(version)
            except Exception as e:
                print(f"Error loading version from {version_file}: {e}")
                
        return sorted(versions, key=lambda v: v.year)
    
    async def delete_version(self, version_id: str) -> bool:
        """Delete an EURING version from storage"""
        version_file = self.data_directory / "versions" / f"{version_id}.json"
        
        if version_file.exists():
            version_file.unlink()
            return True
        return False
    
    async def save_relationships(self, relationships: List[VersionRelationship]) -> None:
        """Save version relationships to storage"""
        relationships_file = self.data_directory / "relationships.json"
        relationships_data = [rel.model_dump() for rel in relationships]
        
        with open(relationships_file, 'w', encoding='utf-8') as f:
            json.dump(relationships_data, f, indent=2, ensure_ascii=False)
    
    async def load_relationships(self) -> List[VersionRelationship]:
        """Load version relationships from storage"""
        relationships_file = self.data_directory / "relationships.json"
        
        if not relationships_file.exists():
            return []
            
        try:
            with open(relationships_file, 'r', encoding='utf-8') as f:
                relationships_data = json.load(f)
                return [VersionRelationship(**rel_data) for rel_data in relationships_data]
        except Exception as e:
            print(f"Error loading relationships: {e}")
            return []
    
    async def save_conversion_mappings(self, mappings: List[ConversionMapping]) -> None:
        """Save conversion mappings to storage"""
        mappings_file = self.data_directory / "conversion_mappings.json"
        mappings_data = [mapping.model_dump() for mapping in mappings]
        
        with open(mappings_file, 'w', encoding='utf-8') as f:
            json.dump(mappings_data, f, indent=2, ensure_ascii=False, default=str)
    
    async def load_conversion_mappings(self) -> List[ConversionMapping]:
        """Load conversion mappings from storage"""
        mappings_file = self.data_directory / "conversion_mappings.json"
        
        if not mappings_file.exists():
            return []
            
        try:
            with open(mappings_file, 'r', encoding='utf-8') as f:
                mappings_data = json.load(f)
                return [ConversionMapping(**mapping_data) for mapping_data in mappings_data]
        except Exception as e:
            print(f"Error loading conversion mappings: {e}")
            return []
    
    async def version_exists(self, version_id: str) -> bool:
        """Check if a version exists in storage"""
        version_file = self.data_directory / "versions" / f"{version_id}.json"
        return version_file.exists()
    
    async def get_versions_by_year_range(self, start_year: int, end_year: int) -> List[EuringVersion]:
        """Get versions within a specific year range"""
        all_versions = await self.load_all_versions()
        return [v for v in all_versions if start_year <= v.year <= end_year]
    
    async def backup_data(self, backup_path: str) -> None:
        """Create a backup of all SKOS data"""
        import shutil
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy entire data directory
        if self.data_directory.exists():
            shutil.copytree(
                self.data_directory, 
                backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
    
    async def restore_data(self, backup_path: str) -> None:
        """Restore SKOS data from backup"""
        import shutil
        backup_dir = Path(backup_path)
        
        if backup_dir.exists():
            # Remove current data
            if self.data_directory.exists():
                shutil.rmtree(self.data_directory)
            
            # Restore from backup
            shutil.copytree(backup_dir, self.data_directory)
    
    # ========================================
    # DOMAIN ORGANIZATION METHODS
    # ========================================
    
    async def save_semantic_domain_definition(self, domain_def: SemanticDomainDefinition) -> None:
        """Save a semantic domain definition to storage"""
        domain_file = self.domains_directory / f"{domain_def.id}.json"
        domain_data = domain_def.model_dump()
        
        with open(domain_file, 'w', encoding='utf-8') as f:
            json.dump(domain_data, f, indent=2, ensure_ascii=False, default=str)
    
    async def load_semantic_domain_definition(self, domain_id: str) -> Optional[SemanticDomainDefinition]:
        """Load a specific semantic domain definition from storage"""
        domain_file = self.domains_directory / f"{domain_id}.json"
        
        if not domain_file.exists():
            return None
            
        try:
            with open(domain_file, 'r', encoding='utf-8') as f:
                domain_data = json.load(f)
                return SemanticDomainDefinition(**domain_data)
        except Exception as e:
            print(f"Error loading domain definition {domain_id}: {e}")
            return None
    
    async def load_all_semantic_domain_definitions(self) -> List[SemanticDomainDefinition]:
        """Load all semantic domain definitions from storage"""
        domains = []
        
        if not self.domains_directory.exists():
            return []
            
        for domain_file in self.domains_directory.glob("*.json"):
            try:
                with open(domain_file, 'r', encoding='utf-8') as f:
                    domain_data = json.load(f)
                    domain = SemanticDomainDefinition(**domain_data)
                    domains.append(domain)
            except Exception as e:
                print(f"Error loading domain from {domain_file}: {e}")
                
        return sorted(domains, key=lambda d: d.name)
    
    async def save_domain_evolution(self, domain_evolution: DomainEvolution) -> None:
        """Save domain evolution data to storage"""
        evolution_file = self.domain_evolutions_directory / f"{domain_evolution.domain.value}.json"
        
        # Custom serialization for DomainCompatibilityMatrix
        evolution_data = domain_evolution.model_dump()
        
        # Handle compatibility matrix serialization
        if 'compatibility_matrix' in evolution_data:
            matrix = evolution_data['compatibility_matrix']
            if 'compatibility_map' in matrix:
                # Convert tuple keys to string format for JSON serialization
                serialized_map = {}
                for key, value in matrix['compatibility_map'].items():
                    if isinstance(key, tuple):
                        serialized_map[f"{key[0]}->{key[1]}"] = value
                    else:
                        serialized_map[key] = value
                matrix['compatibility_map'] = serialized_map
        
        with open(evolution_file, 'w', encoding='utf-8') as f:
            json.dump(evolution_data, f, indent=2, ensure_ascii=False, default=str)
    
    async def load_domain_evolution(self, domain: SemanticDomain) -> Optional[DomainEvolution]:
        """Load domain evolution data from storage"""
        evolution_file = self.domain_evolutions_directory / f"{domain.value}.json"
        
        if not evolution_file.exists():
            return None
            
        try:
            with open(evolution_file, 'r', encoding='utf-8') as f:
                evolution_data = json.load(f)
                
                # Handle compatibility matrix deserialization
                if 'compatibility_matrix' in evolution_data:
                    matrix_data = evolution_data['compatibility_matrix']
                    if 'compatibility_map' in matrix_data:
                        # Convert string keys back to tuple format
                        deserialized_map = {}
                        for key, value in matrix_data['compatibility_map'].items():
                            if '->' in key:
                                from_version, to_version = key.split('->')
                                deserialized_map[(from_version, to_version)] = value
                            else:
                                deserialized_map[key] = value
                        matrix_data['compatibility_map'] = deserialized_map
                
                return DomainEvolution(**evolution_data)
        except Exception as e:
            print(f"Error loading domain evolution for {domain.value}: {e}")
            return None
    
    async def load_all_domain_evolutions(self) -> List[DomainEvolution]:
        """Load all domain evolution data from storage"""
        evolutions = []
        
        if not self.domain_evolutions_directory.exists():
            return []
            
        for evolution_file in self.domain_evolutions_directory.glob("*.json"):
            try:
                with open(evolution_file, 'r', encoding='utf-8') as f:
                    evolution_data = json.load(f)
                    
                    # Handle compatibility matrix deserialization
                    if 'compatibility_matrix' in evolution_data:
                        matrix_data = evolution_data['compatibility_matrix']
                        if 'compatibility_map' in matrix_data:
                            # Convert string keys back to tuple format
                            deserialized_map = {}
                            for key, value in matrix_data['compatibility_map'].items():
                                if '->' in key:
                                    from_version, to_version = key.split('->')
                                    deserialized_map[(from_version, to_version)] = value
                                else:
                                    deserialized_map[key] = value
                            matrix_data['compatibility_map'] = deserialized_map
                    
                    evolution = DomainEvolution(**evolution_data)
                    evolutions.append(evolution)
            except Exception as e:
                print(f"Error loading domain evolution from {evolution_file}: {e}")
                
        return sorted(evolutions, key=lambda e: e.domain.value)
    
    # ========================================
    # DOMAIN-SPECIFIC QUERYING METHODS
    # ========================================
    
    async def get_versions_by_domain(self, domain: SemanticDomain) -> List[EuringVersion]:
        """Get all versions that contain fields for a specific domain"""
        all_versions = await self.load_all_versions()
        domain_versions = []
        
        for version in all_versions:
            # Check if version has fields in this domain
            has_domain_fields = False
            for field in version.field_definitions:
                if field.semantic_domain == domain:
                    has_domain_fields = True
                    break
            
            if has_domain_fields:
                domain_versions.append(version)
                
        return domain_versions
    
    async def get_fields_by_domain(self, version_id: str, domain: SemanticDomain) -> List[FieldDefinition]:
        """Get all fields for a specific domain in a given version"""
        version = await self.load_version(version_id)
        if not version:
            return []
            
        domain_fields = []
        for field in version.field_definitions:
            if field.semantic_domain == domain:
                domain_fields.append(field)
                
        return sorted(domain_fields, key=lambda f: f.position)
    
    async def get_domain_field_evolution(self, domain: SemanticDomain, field_name: str) -> Dict[str, FieldDefinition]:
        """Get the evolution of a specific field across all versions within a domain"""
        all_versions = await self.load_all_versions()
        field_evolution = {}
        
        for version in all_versions:
            for field in version.field_definitions:
                if field.semantic_domain == domain and field.name == field_name:
                    field_evolution[version.id] = field
                    break
                    
        return field_evolution
    
    async def get_domain_compatibility_matrix(self, domain: SemanticDomain) -> Optional[DomainCompatibilityMatrix]:
        """Get the compatibility matrix for a specific domain"""
        domain_evolution = await self.load_domain_evolution(domain)
        if domain_evolution:
            return domain_evolution.compatibility_matrix
        return None
    
    async def update_domain_compatibility(self, domain: SemanticDomain, 
                                        from_version: str, to_version: str, 
                                        compatibility: DomainCompatibilityLevel) -> None:
        """Update compatibility level between two versions for a specific domain"""
        domain_evolution = await self.load_domain_evolution(domain)
        
        if not domain_evolution:
            # Create new domain evolution if it doesn't exist
            compatibility_matrix = DomainCompatibilityMatrix(domain=domain)
            compatibility_matrix.set_compatibility(from_version, to_version, compatibility)
            
            domain_evolution = DomainEvolution(
                domain=domain,
                evolution_entries=[],
                compatibility_matrix=compatibility_matrix
            )
        else:
            domain_evolution.compatibility_matrix.set_compatibility(from_version, to_version, compatibility)
        
        await self.save_domain_evolution(domain_evolution)
    
    async def get_domain_changes_between_versions(self, domain: SemanticDomain, 
                                                from_version: str, to_version: str) -> List[DomainChange]:
        """Get all changes for a domain between two specific versions"""
        domain_evolution = await self.load_domain_evolution(domain)
        if not domain_evolution:
            return []
        
        changes = []
        for entry in domain_evolution.evolution_entries:
            if entry.version == to_version:
                changes.extend(entry.changes)
                
        return changes
    
    async def search_domains_by_field(self, field_name: str) -> List[SemanticDomain]:
        """Find all domains that contain a specific field across any version"""
        all_versions = await self.load_all_versions()
        domains_with_field = set()
        
        for version in all_versions:
            for field in version.field_definitions:
                if field.name == field_name and field.semantic_domain:
                    domains_with_field.add(field.semantic_domain)
                    
        return sorted(list(domains_with_field), key=lambda d: d.value)
    
    async def get_domain_statistics(self, domain: SemanticDomain) -> Dict[str, Any]:
        """Get statistics for a specific domain across all versions"""
        domain_versions = await self.get_versions_by_domain(domain)
        domain_evolution = await self.load_domain_evolution(domain)
        
        stats = {
            'domain': domain.value,
            'versions_with_domain': len(domain_versions),
            'version_ids': [v.id for v in domain_versions],
            'total_fields_across_versions': 0,
            'unique_fields': set(),
            'evolution_entries': 0,
            'total_changes': 0
        }
        
        # Count fields across versions
        for version in domain_versions:
            domain_fields = await self.get_fields_by_domain(version.id, domain)
            stats['total_fields_across_versions'] += len(domain_fields)
            for field in domain_fields:
                stats['unique_fields'].add(field.name)
        
        stats['unique_fields'] = len(stats['unique_fields'])
        
        # Count evolution data
        if domain_evolution:
            stats['evolution_entries'] = len(domain_evolution.evolution_entries)
            for entry in domain_evolution.evolution_entries:
                stats['total_changes'] += len(entry.changes)
        
        return stats
    
    # ========================================
    # COMPLETE MODEL OPERATIONS
    # ========================================
    
    async def save_complete_model(self, model: EuringVersionModel) -> None:
        """Save a complete EURING version model with all components"""
        # Save versions
        for version in model.versions:
            await self.save_version(version)
        
        # Save relationships
        if model.relationships:
            await self.save_relationships(model.relationships)
        
        # Save conversion mappings
        if model.conversion_mappings:
            await self.save_conversion_mappings(model.conversion_mappings)
        
        # Save semantic domain definitions
        if model.semantic_domains:
            for domain_def in model.semantic_domains:
                await self.save_semantic_domain_definition(domain_def)
        
        # Save domain evolutions
        if model.domain_evolutions:
            for domain_evolution in model.domain_evolutions:
                await self.save_domain_evolution(domain_evolution)
    
    async def load_complete_model(self) -> EuringVersionModel:
        """Load the complete EURING version model with all components"""
        versions = await self.load_all_versions()
        relationships = await self.load_relationships()
        conversion_mappings = await self.load_conversion_mappings()
        semantic_domains = await self.load_all_semantic_domain_definitions()
        domain_evolutions = await self.load_all_domain_evolutions()
        
        return EuringVersionModel(
            versions=versions,
            relationships=relationships,
            conversion_mappings=conversion_mappings,
            semantic_domains=semantic_domains,
            domain_evolutions=domain_evolutions
        )