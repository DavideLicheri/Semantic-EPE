"""
Domain Evolution Analyzer Service for EURING Code Recognition System

This service analyzes historical changes within semantic domains, implements domain 
comparison algorithms, and generates evolution timelines for each domain.

Requirements: 8.1, 8.2, 8.3
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from ..models.euring_models import (
    SemanticDomain, DomainEvolution, DomainEvolutionEntry, DomainChange,
    DomainChangeType, DomainCompatibilityLevel, EuringVersion, FieldDefinition
)
from .semantic_field_grouper import SemanticFieldGrouper


class DomainEvolutionAnalyzer:
    """
    Service for analyzing historical changes within semantic domains.
    
    This analyzer provides:
    - Historical change analysis within domains
    - Domain comparison algorithms between versions
    - Evolution timeline generation for each domain
    """
    
    def __init__(self):
        self._domain_evolutions: Dict[SemanticDomain, DomainEvolution] = {}
        self._version_cache: Dict[str, EuringVersion] = {}
        self._semantic_grouper = SemanticFieldGrouper()
    
    def load_domain_evolutions(self, domain_evolutions: List[DomainEvolution]) -> None:
        """Load domain evolution data for analysis"""
        self._domain_evolutions = {
            evolution.domain: evolution for evolution in domain_evolutions
        }
    
    def load_versions(self, versions: List[EuringVersion]) -> None:
        """Load version data for analysis"""
        self._version_cache = {version.id: version for version in versions}
    
    async def analyze_domain_evolution(
        self, 
        domain: SemanticDomain,
        start_version: Optional[str] = None,
        end_version: Optional[str] = None
    ) -> DomainEvolution:
        """
        Analyze historical changes within a specific domain.
        
        Args:
            domain: The semantic domain to analyze
            start_version: Optional starting version for analysis
            end_version: Optional ending version for analysis
            
        Returns:
            DomainEvolution object with complete evolution history
            
        Validates: Requirements 8.1
        """
        if domain not in self._domain_evolutions:
            raise ValueError(f"Domain {domain.value} not found in evolution data")
        
        domain_evolution = self._domain_evolutions[domain]
        
        # Filter evolution entries by version range if specified
        filtered_entries = domain_evolution.evolution_entries
        if start_version or end_version:
            filtered_entries = self._filter_evolution_entries(
                domain_evolution.evolution_entries,
                start_version,
                end_version
            )
        
        # Analyze changes within the filtered entries
        analyzed_changes = self._analyze_domain_changes(filtered_entries)
        
        # Create filtered domain evolution
        return DomainEvolution(
            domain=domain,
            evolution_entries=filtered_entries,
            compatibility_matrix=domain_evolution.compatibility_matrix,
            field_evolution_map=analyzed_changes
        )
    
    async def compare_domain_versions(
        self,
        domain: SemanticDomain,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """
        Compare two versions within a specific domain using comparison algorithms.
        
        Args:
            domain: The semantic domain to compare
            version1: First version to compare
            version2: Second version to compare
            
        Returns:
            Dictionary containing detailed comparison results
            
        Validates: Requirements 8.2
        """
        if domain not in self._domain_evolutions:
            raise ValueError(f"Domain {domain.value} not found in evolution data")
        
        # Get domain fields for both versions
        fields1 = self._get_domain_fields(domain, version1)
        fields2 = self._get_domain_fields(domain, version2)
        
        # Perform field-level comparison
        field_comparison = self._compare_domain_fields(fields1, fields2)
        
        # Get evolution entries for both versions
        entry1 = self._get_evolution_entry(domain, version1)
        entry2 = self._get_evolution_entry(domain, version2)
        
        # Calculate compatibility level
        compatibility = self._calculate_domain_compatibility(entry1, entry2)
        
        # Analyze semantic changes
        semantic_changes = self._analyze_semantic_changes(entry1, entry2)
        
        return {
            "domain": domain.value,
            "version1": version1,
            "version2": version2,
            "field_comparison": field_comparison,
            "compatibility_level": compatibility.value,
            "semantic_changes": semantic_changes,
            "evolution_summary": {
                "fields_added": field_comparison["added"],
                "fields_removed": field_comparison["removed"],
                "fields_modified": field_comparison["modified"],
                "total_changes": len(field_comparison["added"]) + 
                               len(field_comparison["removed"]) + 
                               len(field_comparison["modified"])
            }
        }
    
    async def generate_evolution_timeline(
        self,
        domain: SemanticDomain,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate evolution timeline for a specific domain.
        
        Args:
            domain: The semantic domain to generate timeline for
            include_details: Whether to include detailed change information
            
        Returns:
            Dictionary containing timeline data with chronological evolution
            
        Validates: Requirements 8.3
        """
        if domain not in self._domain_evolutions:
            raise ValueError(f"Domain {domain.value} not found in evolution data")
        
        domain_evolution = self._domain_evolutions[domain]
        
        # Sort evolution entries chronologically
        sorted_entries = sorted(
            domain_evolution.evolution_entries,
            key=lambda entry: entry.year
        )
        
        # Generate timeline events
        timeline_events = []
        for i, entry in enumerate(sorted_entries):
            event = {
                "version": entry.version,
                "year": entry.year,
                "position": i + 1,
                "total_versions": len(sorted_entries)
            }
            
            if include_details:
                event.update({
                    "changes_summary": {
                        "total_changes": len(entry.changes),
                        "fields_added": len(entry.fields_added or []),
                        "fields_removed": len(entry.fields_removed or []),
                        "fields_modified": len(entry.fields_modified or [])
                    },
                    "major_changes": [
                        {
                            "type": change.change_type.value,
                            "field": change.field_name,
                            "impact": change.semantic_impact,
                            "compatibility_impact": change.compatibility_impact.value
                        }
                        for change in entry.changes[:5]  # Top 5 changes
                    ],
                    "semantic_notes": entry.semantic_notes[:3],  # Top 3 notes
                    "format_changes": entry.format_changes or []
                })
            
            timeline_events.append(event)
        
        # Calculate evolution statistics
        evolution_stats = self._calculate_evolution_statistics(sorted_entries)
        
        return {
            "domain": domain.value,
            "timeline_events": timeline_events,
            "evolution_period": {
                "start_year": sorted_entries[0].year if sorted_entries else None,
                "end_year": sorted_entries[-1].year if sorted_entries else None,
                "duration_years": (sorted_entries[-1].year - sorted_entries[0].year) if len(sorted_entries) > 1 else 0
            },
            "evolution_statistics": evolution_stats,
            "domain_stability": self._calculate_domain_stability(sorted_entries)
        }
    
    async def analyze_semantic_field_grouping(
        self,
        domain: SemanticDomain,
        versions: Optional[List[EuringVersion]] = None
    ) -> Dict[str, Any]:
        """
        Analyze semantic field grouping within a domain using the semantic field grouper.
        
        Args:
            domain: The semantic domain to analyze
            versions: Optional list of versions to analyze (uses cached versions if None)
            
        Returns:
            Dictionary containing semantic field grouping analysis
            
        Validates: Requirements 8.4
        """
        # Use cached versions if none provided
        if versions is None:
            versions = list(self._version_cache.values())
        
        if not versions:
            raise ValueError("No versions available for semantic field grouping analysis")
        
        # Perform domain-specific field analysis
        domain_analysis = self._semantic_grouper.analyze_domain_specific_fields(domain, versions)
        
        # Get all fields for the domain across versions
        all_domain_fields = []
        for version in versions:
            domain_fields = [f for f in version.field_definitions if f.semantic_domain == domain]
            all_domain_fields.extend(domain_fields)
        
        # Group fields by semantic relationships
        field_groups = self._semantic_grouper.group_fields_by_semantics(all_domain_fields, domain)
        
        # Categorize fields semantically
        field_categories = self._semantic_grouper.categorize_semantic_fields(all_domain_fields, domain)
        
        # Extract semantic meanings for all fields
        semantic_meanings = []
        for field in all_domain_fields:
            meaning = self._semantic_grouper.extract_semantic_meaning(field)
            semantic_meanings.append({
                "field_name": meaning.field_name,
                "primary_concept": meaning.primary_concept,
                "secondary_concepts": meaning.secondary_concepts,
                "semantic_category": meaning.semantic_category,
                "confidence": meaning.confidence,
                "linguistic_patterns": meaning.linguistic_patterns
            })
        
        # Format field groups for output
        formatted_groups = []
        for group in field_groups:
            formatted_groups.append({
                "group_id": group.group_id,
                "group_name": group.group_name,
                "fields": group.fields,
                "semantic_theme": group.semantic_theme,
                "cohesion_score": group.cohesion_score,
                "relationships": [
                    {
                        "field1": rel.field1,
                        "field2": rel.field2,
                        "relationship_type": rel.relationship_type,
                        "strength": rel.strength,
                        "semantic_basis": rel.semantic_basis
                    }
                    for rel in group.relationships
                ]
            })
        
        return {
            "domain": domain.value,
            "total_fields_analyzed": len(all_domain_fields),
            "versions_analyzed": len(versions),
            "domain_analysis": domain_analysis,
            "field_groups": formatted_groups,
            "field_categories": field_categories,
            "semantic_meanings": semantic_meanings,
            "grouping_summary": {
                "total_groups": len(field_groups),
                "average_group_size": sum(len(g.fields) for g in field_groups) / len(field_groups) if field_groups else 0,
                "average_cohesion": sum(g.cohesion_score for g in field_groups) / len(field_groups) if field_groups else 0,
                "most_cohesive_group": max(field_groups, key=lambda g: g.cohesion_score).group_name if field_groups else None
            }
        }
    
    def _filter_evolution_entries(
        self,
        entries: List[DomainEvolutionEntry],
        start_version: Optional[str],
        end_version: Optional[str]
    ) -> List[DomainEvolutionEntry]:
        """Filter evolution entries by version range"""
        filtered = entries
        
        if start_version:
            start_year = self._get_version_year(start_version)
            filtered = [entry for entry in filtered if entry.year >= start_year]
        
        if end_version:
            end_year = self._get_version_year(end_version)
            filtered = [entry for entry in filtered if entry.year <= end_year]
        
        return filtered
    
    def _analyze_domain_changes(
        self,
        entries: List[DomainEvolutionEntry]
    ) -> Dict[str, Any]:
        """Analyze changes across domain evolution entries"""
        all_changes = []
        field_evolution = {}
        
        for entry in entries:
            all_changes.extend(entry.changes)
            
            # Track field evolution
            for change in entry.changes:
                field_name = change.field_name
                if field_name not in field_evolution:
                    field_evolution[field_name] = []
                
                field_evolution[field_name].append({
                    "version": entry.version,
                    "year": entry.year,
                    "change_type": change.change_type.value,
                    "semantic_impact": change.semantic_impact
                })
        
        # Categorize changes by type
        change_categories = {
            "added": [c for c in all_changes if c.change_type == DomainChangeType.ADDED],
            "removed": [c for c in all_changes if c.change_type == DomainChangeType.REMOVED],
            "modified": [c for c in all_changes if c.change_type == DomainChangeType.MODIFIED],
            "renamed": [c for c in all_changes if c.change_type == DomainChangeType.RENAMED]
        }
        
        return {
            "field_evolution": field_evolution,
            "change_categories": change_categories,
            "total_changes": len(all_changes)
        }
    
    def _get_domain_fields(
        self,
        domain: SemanticDomain,
        version: str
    ) -> List[FieldDefinition]:
        """Get fields belonging to a domain in a specific version"""
        if version not in self._version_cache:
            return []
        
        version_obj = self._version_cache[version]
        return [
            field for field in version_obj.field_definitions
            if field.semantic_domain == domain
        ]
    
    def _compare_domain_fields(
        self,
        fields1: List[FieldDefinition],
        fields2: List[FieldDefinition]
    ) -> Dict[str, List[str]]:
        """Compare fields between two versions of a domain"""
        field_names1 = {field.name for field in fields1}
        field_names2 = {field.name for field in fields2}
        
        added = list(field_names2 - field_names1)
        removed = list(field_names1 - field_names2)
        common = field_names1 & field_names2
        
        # Check for modifications in common fields
        modified = []
        fields1_dict = {field.name: field for field in fields1}
        fields2_dict = {field.name: field for field in fields2}
        
        for field_name in common:
            field1 = fields1_dict[field_name]
            field2 = fields2_dict[field_name]
            
            if (field1.data_type != field2.data_type or
                field1.length != field2.length or
                field1.valid_values != field2.valid_values):
                modified.append(field_name)
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": list(common - set(modified))
        }
    
    def _get_evolution_entry(
        self,
        domain: SemanticDomain,
        version: str
    ) -> Optional[DomainEvolutionEntry]:
        """Get evolution entry for a specific domain and version"""
        if domain not in self._domain_evolutions:
            return None
        
        domain_evolution = self._domain_evolutions[domain]
        for entry in domain_evolution.evolution_entries:
            if entry.version == version:
                return entry
        
        return None
    
    def _calculate_domain_compatibility(
        self,
        entry1: Optional[DomainEvolutionEntry],
        entry2: Optional[DomainEvolutionEntry]
    ) -> DomainCompatibilityLevel:
        """Calculate compatibility level between two domain evolution entries"""
        if not entry1 or not entry2:
            return DomainCompatibilityLevel.INCOMPATIBLE
        
        # Count breaking changes
        breaking_changes = 0
        total_changes = len(entry1.changes) + len(entry2.changes)
        
        for change in entry1.changes + entry2.changes:
            if change.compatibility_impact in [
                DomainCompatibilityLevel.LOSSY,
                DomainCompatibilityLevel.INCOMPATIBLE
            ]:
                breaking_changes += 1
        
        if total_changes == 0:
            return DomainCompatibilityLevel.FULL
        
        breaking_ratio = breaking_changes / total_changes
        
        if breaking_ratio == 0:
            return DomainCompatibilityLevel.FULL
        elif breaking_ratio < 0.3:
            return DomainCompatibilityLevel.PARTIAL
        elif breaking_ratio < 0.7:
            return DomainCompatibilityLevel.LOSSY
        else:
            return DomainCompatibilityLevel.INCOMPATIBLE
    
    def _analyze_semantic_changes(
        self,
        entry1: Optional[DomainEvolutionEntry],
        entry2: Optional[DomainEvolutionEntry]
    ) -> List[Dict[str, Any]]:
        """Analyze semantic changes between two evolution entries"""
        if not entry1 or not entry2:
            return []
        
        semantic_changes = []
        
        # Compare semantic notes
        notes1 = set(entry1.semantic_notes)
        notes2 = set(entry2.semantic_notes)
        
        new_concepts = notes2 - notes1
        removed_concepts = notes1 - notes2
        
        for concept in new_concepts:
            semantic_changes.append({
                "type": "concept_added",
                "description": concept,
                "impact": "enhancement"
            })
        
        for concept in removed_concepts:
            semantic_changes.append({
                "type": "concept_removed", 
                "description": concept,
                "impact": "reduction"
            })
        
        # Analyze field semantic meanings
        if entry1.field_mappings and entry2.field_mappings:
            semantic_changes.extend(
                self._compare_field_semantics(entry1.field_mappings, entry2.field_mappings)
            )
        
        return semantic_changes
    
    def _compare_field_semantics(self, mappings1, mappings2) -> List[Dict[str, Any]]:
        """Compare semantic meanings of field mappings"""
        changes = []
        
        # This would compare semantic domains and meanings of field mappings
        # Implementation depends on the specific structure of field mappings
        # For now, return empty list as placeholder
        
        return changes
    
    def _calculate_evolution_statistics(
        self,
        entries: List[DomainEvolutionEntry]
    ) -> Dict[str, Any]:
        """Calculate statistics about domain evolution"""
        if not entries:
            return {}
        
        total_changes = sum(len(entry.changes) for entry in entries)
        total_fields_added = sum(len(entry.fields_added or []) for entry in entries)
        total_fields_removed = sum(len(entry.fields_removed or []) for entry in entries)
        total_fields_modified = sum(len(entry.fields_modified or []) for entry in entries)
        
        # Calculate change types distribution
        change_types = {}
        for entry in entries:
            for change in entry.changes:
                change_type = change.change_type.value
                change_types[change_type] = change_types.get(change_type, 0) + 1
        
        return {
            "total_versions": len(entries),
            "total_changes": total_changes,
            "average_changes_per_version": total_changes / len(entries) if entries else 0,
            "fields_added": total_fields_added,
            "fields_removed": total_fields_removed,
            "fields_modified": total_fields_modified,
            "change_types_distribution": change_types,
            "most_active_version": max(entries, key=lambda e: len(e.changes)).version if entries else None
        }
    
    def _calculate_domain_stability(
        self,
        entries: List[DomainEvolutionEntry]
    ) -> Dict[str, Any]:
        """Calculate stability metrics for a domain"""
        if not entries:
            return {"stability_score": 0, "stability_level": "unknown"}
        
        # Calculate stability based on change frequency and impact
        total_changes = sum(len(entry.changes) for entry in entries)
        total_versions = len(entries)
        
        # Stability score (0-10, where 10 is most stable)
        if total_versions == 0:
            stability_score = 0
        else:
            changes_per_version = total_changes / total_versions
            # Inverse relationship: fewer changes = higher stability
            stability_score = max(0, 10 - (changes_per_version * 2))
        
        # Determine stability level
        if stability_score >= 8:
            stability_level = "very_high"
        elif stability_score >= 6:
            stability_level = "high"
        elif stability_score >= 4:
            stability_level = "medium"
        elif stability_score >= 2:
            stability_level = "low"
        else:
            stability_level = "very_low"
        
        return {
            "stability_score": round(stability_score, 1),
            "stability_level": stability_level,
            "changes_per_version": round(total_changes / total_versions, 1) if total_versions > 0 else 0,
            "most_stable_period": self._find_most_stable_period(entries),
            "most_volatile_period": self._find_most_volatile_period(entries)
        }
    
    def _find_most_stable_period(
        self,
        entries: List[DomainEvolutionEntry]
    ) -> Optional[Dict[str, Any]]:
        """Find the most stable period in domain evolution"""
        if len(entries) < 2:
            return None
        
        min_changes = float('inf')
        stable_period = None
        
        for i in range(len(entries) - 1):
            changes = len(entries[i].changes) + len(entries[i + 1].changes)
            if changes < min_changes:
                min_changes = changes
                stable_period = {
                    "start_version": entries[i].version,
                    "end_version": entries[i + 1].version,
                    "start_year": entries[i].year,
                    "end_year": entries[i + 1].year,
                    "total_changes": changes
                }
        
        return stable_period
    
    def _find_most_volatile_period(
        self,
        entries: List[DomainEvolutionEntry]
    ) -> Optional[Dict[str, Any]]:
        """Find the most volatile period in domain evolution"""
        if len(entries) < 2:
            return None
        
        max_changes = 0
        volatile_period = None
        
        for i in range(len(entries) - 1):
            changes = len(entries[i].changes) + len(entries[i + 1].changes)
            if changes > max_changes:
                max_changes = changes
                volatile_period = {
                    "start_version": entries[i].version,
                    "end_version": entries[i + 1].version,
                    "start_year": entries[i].year,
                    "end_year": entries[i + 1].year,
                    "total_changes": changes
                }
        
        return volatile_period
    
    def _get_version_year(self, version: str) -> int:
        """Get the year for a version"""
        if version in self._version_cache:
            return self._version_cache[version].year
        
        # Fallback: try to extract year from version string
        try:
            if "1966" in version:
                return 1966
            elif "1979" in version:
                return 1979
            elif "2000" in version:
                return 2000
            elif "2020" in version:
                return 2020
            else:
                return 2020  # Default to latest
        except:
            return 2020