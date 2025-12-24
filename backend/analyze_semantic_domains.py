#!/usr/bin/env python3
"""
Semantic Domain Analysis for EURING Code Versions

This script analyzes and documents the 7 semantic domains across all EURING versions:
1. IDENTIFICATION_MARKING - Ring numbers, schemes, metal rings, other marks, verification
2. SPECIES - Species codes, taxonomy, finder vs scheme identification  
3. DEMOGRAPHICS - Age, sex classification systems
4. TEMPORAL - Date/time formats and their evolution
5. SPATIAL - Coordinates, location accuracy, geographic encoding
6. BIOMETRICS - Wing, weight, bill, tarsus, fat, muscle, moult measurements
7. METHODOLOGY - Capture methods, conditions, manipulation, lures

Creates detailed analysis of field evolution and domain evolution matrices.
"""

import json
import os
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

class SemanticDomain(Enum):
    IDENTIFICATION_MARKING = 'identification_marking'
    SPECIES = 'species'
    DEMOGRAPHICS = 'demographics'
    TEMPORAL = 'temporal'
    SPATIAL = 'spatial'
    BIOMETRICS = 'biometrics'
    METHODOLOGY = 'methodology'

@dataclass
class FieldEvolution:
    """Tracks evolution of a specific field across versions"""
    field_name: str
    semantic_domain: SemanticDomain
    versions_present: List[str]
    format_changes: Dict[str, str]  # version -> format description
    semantic_changes: Dict[str, str]  # version -> semantic meaning changes
    data_type_changes: Dict[str, str]  # version -> data type
    length_changes: Dict[str, int]  # version -> field length
    validation_changes: Dict[str, List[str]]  # version -> validation rules

@dataclass
class DomainEvolutionEntry:
    """Evolution entry for a specific domain in a specific version"""
    version: str
    year: int
    fields_added: List[str]
    fields_removed: List[str]
    fields_modified: List[str]
    format_changes: List[str]
    semantic_improvements: List[str]
    compatibility_notes: List[str]

@dataclass
class DomainEvolution:
    """Complete evolution history of a semantic domain"""
    domain: SemanticDomain
    description: str
    evolution_entries: List[DomainEvolutionEntry]
    field_evolution_map: Dict[str, FieldEvolution]
    compatibility_matrix: Dict[Tuple[str, str], str]  # (from_version, to_version) -> compatibility level

class SemanticDomainAnalyzer:
    """Analyzes semantic domains across EURING versions"""
    
    def __init__(self, data_dir: str = "data/euring_versions/versions"):
        self.data_dir = data_dir
        self.versions = {}
        self.domain_field_mappings = self._initialize_domain_mappings()
        
    def _initialize_domain_mappings(self) -> Dict[SemanticDomain, List[str]]:
        """Initialize semantic domain field mappings based on field names and meanings"""
        return {
            SemanticDomain.IDENTIFICATION_MARKING: [
                'ring_number', 'identification_number', 'ring_prefix', 'ring_suffix',
                'scheme_code', 'scheme_country', 'ringing_scheme', 'metal_ring_info',
                'metal_ring_information', 'other_marks_info', 'other_marks_information',
                'primary_identification_method', 'verification_code', 
                'verification_of_the_metal_ring'
            ],
            SemanticDomain.SPECIES: [
                'species_code', 'species_as_mentioned_by_finder', 
                'species_as_mentioned_by_scheme'
            ],
            SemanticDomain.DEMOGRAPHICS: [
                'age_code', 'age_mentioned_by_the_person', 'sex_code', 
                'sex_mentioned_by_the_person', 'sex_concluded_by_the_scheme'
            ],
            SemanticDomain.TEMPORAL: [
                'date_code', 'date_first', 'date_current', 'time_code'
            ],
            SemanticDomain.SPATIAL: [
                'latitude', 'longitude', 'latitude_encoded', 'longitude_encoded',
                'latitude_decimal', 'longitude_decimal', 'latitude_sign', 
                'latitude_value', 'longitude_sign', 'longitude_value',
                'location_code', 'region_code', 'accuracy_code'
            ],
            SemanticDomain.BIOMETRICS: [
                'wing_length', 'weight', 'bill_length', 'tarsus_length',
                'fat_score', 'muscle_score', 'moult_code', 'measurement_1',
                'measurement_2', 'measurement_3', 'measurement_4'
            ],
            SemanticDomain.METHODOLOGY: [
                'condition_code', 'method_code', 'status_code', 'status_info',
                'manipulated', 'moved_before', 'catching_method', 'catching_lures'
            ]
        }
    
    def load_versions(self):
        """Load all EURING version data"""
        version_files = [
            'euring_1966.json',
            'euring_1979.json', 
            'euring_2000.json',
            'euring_2020.json',
            'euring_2020_official.json'
        ]
        
        for filename in version_files:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    self.versions[version_data['id']] = version_data
                    print(f"Loaded {version_data['name']} ({version_data['year']})")
    
    def classify_field_to_domain(self, field_name: str, field_def: Dict) -> SemanticDomain:
        """Classify a field to its semantic domain based on name and semantic meaning"""
        field_name_lower = field_name.lower()
        semantic_meaning = field_def.get('semantic_meaning', '').lower()
        
        # Check direct field name matches first
        for domain, field_patterns in self.domain_field_mappings.items():
            if field_name in field_patterns:
                return domain
        
        # Check semantic meaning patterns
        if any(keyword in semantic_meaning for keyword in ['ring', 'identification', 'scheme', 'mark', 'verification']):
            return SemanticDomain.IDENTIFICATION_MARKING
        elif any(keyword in semantic_meaning for keyword in ['species', 'taxonomy']):
            return SemanticDomain.SPECIES
        elif any(keyword in semantic_meaning for keyword in ['age', 'sex']):
            return SemanticDomain.DEMOGRAPHICS
        elif any(keyword in semantic_meaning for keyword in ['date', 'time']):
            return SemanticDomain.TEMPORAL
        elif any(keyword in semantic_meaning for keyword in ['latitude', 'longitude', 'coordinate', 'location', 'geographic']):
            return SemanticDomain.SPATIAL
        elif any(keyword in semantic_meaning for keyword in ['wing', 'weight', 'bill', 'tarsus', 'fat', 'muscle', 'moult', 'biometric', 'measurement']):
            return SemanticDomain.BIOMETRICS
        elif any(keyword in semantic_meaning for keyword in ['method', 'condition', 'capture', 'manipulation', 'lure', 'status']):
            return SemanticDomain.METHODOLOGY
        
        # Default classification based on field name patterns
        if any(pattern in field_name_lower for pattern in ['empty', 'padding', 'separator']):
            return SemanticDomain.METHODOLOGY  # Structural fields
        
        # If still unclassified, make best guess based on field name
        print(f"Warning: Could not classify field '{field_name}' with meaning '{semantic_meaning}'. Defaulting to METHODOLOGY.")
        return SemanticDomain.METHODOLOGY
    
    def analyze_field_evolution(self) -> Dict[str, FieldEvolution]:
        """Analyze how individual fields evolve across versions"""
        field_evolution_map = {}
        
        # Collect all unique field names across versions
        all_fields = set()
        for version_data in self.versions.values():
            for field_def in version_data['field_definitions']:
                all_fields.add(field_def['name'])
        
        # Analyze evolution for each field
        for field_name in all_fields:
            versions_present = []
            format_changes = {}
            semantic_changes = {}
            data_type_changes = {}
            length_changes = {}
            validation_changes = {}
            domain = None
            
            for version_id, version_data in self.versions.items():
                field_def = next((f for f in version_data['field_definitions'] if f['name'] == field_name), None)
                
                if field_def:
                    versions_present.append(version_id)
                    
                    # Track domain (should be consistent)
                    if domain is None:
                        domain = self.classify_field_to_domain(field_name, field_def)
                    
                    # Track format changes
                    format_info = f"Length: {field_def.get('length', 'variable')}, Type: {field_def.get('data_type', 'unknown')}"
                    if field_def.get('format_pattern'):
                        format_info += f", Pattern: {field_def['format_pattern']}"
                    format_changes[version_id] = format_info
                    
                    # Track semantic changes
                    semantic_changes[version_id] = field_def.get('semantic_meaning', 'No semantic meaning defined')
                    
                    # Track data type changes
                    data_type_changes[version_id] = field_def.get('data_type', 'unknown')
                    
                    # Track length changes
                    length_changes[version_id] = field_def.get('length', 0)
                    
                    # Track validation changes
                    field_validations = []
                    for rule in version_data.get('validation_rules', []):
                        if rule.get('field_name') == field_name:
                            field_validations.append(f"{rule.get('rule_type', 'unknown')}: {rule.get('rule_expression', 'no expression')}")
                    validation_changes[version_id] = field_validations
            
            if domain:
                field_evolution_map[field_name] = FieldEvolution(
                    field_name=field_name,
                    semantic_domain=domain,
                    versions_present=versions_present,
                    format_changes=format_changes,
                    semantic_changes=semantic_changes,
                    data_type_changes=data_type_changes,
                    length_changes=length_changes,
                    validation_changes=validation_changes
                )
        
        return field_evolution_map
    
    def analyze_domain_evolution(self, field_evolution_map: Dict[str, FieldEvolution]) -> Dict[SemanticDomain, DomainEvolution]:
        """Analyze evolution of each semantic domain"""
        domain_evolutions = {}
        
        # Sort versions by year for chronological analysis
        sorted_versions = sorted(self.versions.items(), key=lambda x: x[1]['year'])
        
        for domain in SemanticDomain:
            evolution_entries = []
            compatibility_matrix = {}
            
            # Get all fields for this domain
            domain_fields = {name: evolution for name, evolution in field_evolution_map.items() 
                           if evolution.semantic_domain == domain}
            
            # Analyze evolution for each version
            previous_version_fields = set()
            
            for i, (version_id, version_data) in enumerate(sorted_versions):
                current_version_fields = set()
                
                # Find fields present in this version for this domain
                for field_def in version_data['field_definitions']:
                    field_name = field_def['name']
                    if field_name in domain_fields:
                        current_version_fields.add(field_name)
                
                # Calculate changes from previous version
                if i == 0:
                    fields_added = list(current_version_fields)
                    fields_removed = []
                    fields_modified = []
                else:
                    fields_added = list(current_version_fields - previous_version_fields)
                    fields_removed = list(previous_version_fields - current_version_fields)
                    
                    # Check for modifications in common fields
                    common_fields = current_version_fields & previous_version_fields
                    fields_modified = []
                    for field_name in common_fields:
                        field_evolution = domain_fields[field_name]
                        prev_version_id = sorted_versions[i-1][0]
                        
                        # Check if format, type, or validation changed
                        if (field_evolution.format_changes.get(version_id) != field_evolution.format_changes.get(prev_version_id) or
                            field_evolution.data_type_changes.get(version_id) != field_evolution.data_type_changes.get(prev_version_id) or
                            field_evolution.validation_changes.get(version_id) != field_evolution.validation_changes.get(prev_version_id)):
                            fields_modified.append(field_name)
                
                # Analyze format changes for this domain
                format_changes = []
                if version_data.get('format_specification'):
                    format_spec = version_data['format_specification']
                    if format_spec.get('field_separator'):
                        format_changes.append(f"Field separator: {format_spec['field_separator']}")
                    else:
                        format_changes.append("Fixed-length format")
                    
                    if format_spec.get('total_length'):
                        format_changes.append(f"Total length: {format_spec['total_length']}")
                
                # Identify semantic improvements
                semantic_improvements = []
                if version_id == 'euring_2020_official':
                    semantic_improvements.append("Official SKOS thesaurus integration")
                    semantic_improvements.append("Precise field definitions with editorial notes")
                    semantic_improvements.append("Priority-based manipulation codes")
                elif version_id == 'euring_2020':
                    semantic_improvements.append("Decimal coordinate format")
                    semantic_improvements.append("Pipe-delimited structure")
                    semantic_improvements.append("Enhanced biometric measurements")
                elif version_id == 'euring_2000':
                    semantic_improvements.append("Complex alphanumeric encoding")
                    semantic_improvements.append("Enhanced location accuracy")
                elif version_id == 'euring_1979':
                    semantic_improvements.append("Fixed-length format standardization")
                    semantic_improvements.append("Encoded coordinate system")
                    semantic_improvements.append("Additional measurement fields")
                
                # Compatibility notes
                compatibility_notes = []
                if i > 0:
                    if fields_removed:
                        compatibility_notes.append(f"Fields removed: {', '.join(fields_removed)}")
                    if fields_added:
                        compatibility_notes.append(f"Fields added: {', '.join(fields_added)}")
                    if fields_modified:
                        compatibility_notes.append(f"Fields modified: {', '.join(fields_modified)}")
                
                evolution_entry = DomainEvolutionEntry(
                    version=version_id,
                    year=version_data['year'],
                    fields_added=fields_added,
                    fields_removed=fields_removed,
                    fields_modified=fields_modified,
                    format_changes=format_changes,
                    semantic_improvements=semantic_improvements,
                    compatibility_notes=compatibility_notes
                )
                
                evolution_entries.append(evolution_entry)
                previous_version_fields = current_version_fields
            
            # Build compatibility matrix for this domain
            for i, (version_id1, _) in enumerate(sorted_versions):
                for j, (version_id2, _) in enumerate(sorted_versions):
                    if i != j:
                        # Determine compatibility level
                        domain_fields_v1 = {name for name, evolution in domain_fields.items() 
                                          if version_id1 in evolution.versions_present}
                        domain_fields_v2 = {name for name, evolution in domain_fields.items() 
                                          if version_id2 in evolution.versions_present}
                        
                        common_fields = domain_fields_v1 & domain_fields_v2
                        total_fields = domain_fields_v1 | domain_fields_v2
                        
                        if len(common_fields) == len(total_fields):
                            compatibility_level = "FULL"
                        elif len(common_fields) >= len(total_fields) * 0.8:
                            compatibility_level = "PARTIAL"
                        elif len(common_fields) >= len(total_fields) * 0.5:
                            compatibility_level = "LOSSY"
                        else:
                            compatibility_level = "INCOMPATIBLE"
                        
                        compatibility_matrix[(version_id1, version_id2)] = compatibility_level
            
            # Create domain evolution
            domain_description = self._get_domain_description(domain)
            domain_evolutions[domain] = DomainEvolution(
                domain=domain,
                description=domain_description,
                evolution_entries=evolution_entries,
                field_evolution_map=domain_fields,
                compatibility_matrix=compatibility_matrix
            )
        
        return domain_evolutions
    
    def _get_domain_description(self, domain: SemanticDomain) -> str:
        """Get description for each semantic domain"""
        descriptions = {
            SemanticDomain.IDENTIFICATION_MARKING: "Ring numbers, schemes, metal rings, other marks, and verification systems for unique bird identification throughout its life",
            SemanticDomain.SPECIES: "Species codes, taxonomy systems, and identification verification by both finders and ringing schemes",
            SemanticDomain.DEMOGRAPHICS: "Age and sex classification systems based on plumage characteristics and morphological features",
            SemanticDomain.TEMPORAL: "Date and time formats for recording capture, observation, and handling events",
            SemanticDomain.SPATIAL: "Geographic coordinates, location accuracy, and spatial encoding systems for recording bird locations",
            SemanticDomain.BIOMETRICS: "Physical measurements including wing length, weight, bill dimensions, tarsus, fat scores, muscle condition, and moult status",
            SemanticDomain.METHODOLOGY: "Capture methods, handling conditions, manipulation status, lures used, and procedural information"
        }
        return descriptions[domain]
    
    def generate_analysis_report(self, output_dir: str = "data/documentation/analysis"):
        """Generate comprehensive analysis report"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Load versions and analyze
        self.load_versions()
        field_evolution_map = self.analyze_field_evolution()
        domain_evolutions = self.analyze_domain_evolution(field_evolution_map)
        
        # Generate main analysis report
        report_path = os.path.join(output_dir, "semantic_domain_analysis.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# EURING Semantic Domain Analysis\n\n")
            f.write("This document provides a comprehensive analysis of the 7 semantic domains across all EURING code versions (1966-2020).\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Versions Analyzed**: {len(self.versions)}\n")
            f.write(f"- **Total Fields Analyzed**: {len(field_evolution_map)}\n")
            f.write(f"- **Semantic Domains**: {len(SemanticDomain)}\n")
            f.write(f"- **Analysis Period**: 1966-2020 (54 years of evolution)\n\n")
            
            # Domain overview
            f.write("## Semantic Domains Overview\n\n")
            for domain in SemanticDomain:
                domain_evolution = domain_evolutions[domain]
                domain_fields = len(domain_evolution.field_evolution_map)
                f.write(f"### {domain.value.replace('_', ' ').title()}\n")
                f.write(f"**Description**: {domain_evolution.description}\n\n")
                f.write(f"**Total Fields**: {domain_fields}\n\n")
                
                # List fields in this domain
                f.write("**Fields in this domain**:\n")
                for field_name in sorted(domain_evolution.field_evolution_map.keys()):
                    field_evolution = domain_evolution.field_evolution_map[field_name]
                    versions_str = ", ".join(field_evolution.versions_present)
                    f.write(f"- `{field_name}` (present in: {versions_str})\n")
                f.write("\n")
            
            # Evolution timeline
            f.write("## Evolution Timeline\n\n")
            sorted_versions = sorted(self.versions.items(), key=lambda x: x[1]['year'])
            
            for version_id, version_data in sorted_versions:
                f.write(f"### {version_data['name']} ({version_data['year']})\n\n")
                f.write(f"**Description**: {version_data['description']}\n\n")
                
                # Show changes for each domain
                for domain in SemanticDomain:
                    domain_evolution = domain_evolutions[domain]
                    evolution_entry = next((e for e in domain_evolution.evolution_entries if e.version == version_id), None)
                    
                    if evolution_entry and (evolution_entry.fields_added or evolution_entry.fields_removed or evolution_entry.fields_modified):
                        f.write(f"**{domain.value.replace('_', ' ').title()} Changes**:\n")
                        
                        if evolution_entry.fields_added:
                            f.write(f"- Added: {', '.join(evolution_entry.fields_added)}\n")
                        if evolution_entry.fields_removed:
                            f.write(f"- Removed: {', '.join(evolution_entry.fields_removed)}\n")
                        if evolution_entry.fields_modified:
                            f.write(f"- Modified: {', '.join(evolution_entry.fields_modified)}\n")
                        
                        if evolution_entry.semantic_improvements:
                            f.write(f"- Improvements: {', '.join(evolution_entry.semantic_improvements)}\n")
                        f.write("\n")
                
                f.write("\n")
        
        # Generate domain-specific reports
        for domain, domain_evolution in domain_evolutions.items():
            domain_report_path = os.path.join(output_dir, f"domain_{domain.value}_evolution.md")
            with open(domain_report_path, 'w', encoding='utf-8') as f:
                f.write(f"# {domain.value.replace('_', ' ').title()} Domain Evolution\n\n")
                f.write(f"**Description**: {domain_evolution.description}\n\n")
                
                # Field evolution details
                f.write("## Field Evolution Details\n\n")
                for field_name, field_evolution in sorted(domain_evolution.field_evolution_map.items()):
                    f.write(f"### {field_name}\n\n")
                    f.write(f"**Versions Present**: {', '.join(field_evolution.versions_present)}\n\n")
                    
                    # Format changes
                    f.write("**Format Evolution**:\n")
                    for version_id in field_evolution.versions_present:
                        format_info = field_evolution.format_changes.get(version_id, 'No format info')
                        f.write(f"- {version_id}: {format_info}\n")
                    f.write("\n")
                    
                    # Semantic changes
                    f.write("**Semantic Evolution**:\n")
                    for version_id in field_evolution.versions_present:
                        semantic_info = field_evolution.semantic_changes.get(version_id, 'No semantic info')
                        f.write(f"- {version_id}: {semantic_info}\n")
                    f.write("\n")
                
                # Compatibility matrix
                f.write("## Compatibility Matrix\n\n")
                f.write("| From \\ To | ")
                version_ids = sorted(self.versions.keys(), key=lambda x: self.versions[x]['year'])
                for version_id in version_ids:
                    f.write(f"{version_id} | ")
                f.write("\n")
                
                f.write("|-----------|")
                for _ in version_ids:
                    f.write("----------|")
                f.write("\n")
                
                for from_version in version_ids:
                    f.write(f"| {from_version} | ")
                    for to_version in version_ids:
                        if from_version == to_version:
                            f.write("SAME | ")
                        else:
                            compatibility = domain_evolution.compatibility_matrix.get((from_version, to_version), "UNKNOWN")
                            f.write(f"{compatibility} | ")
                    f.write("\n")
                f.write("\n")
        
        # Generate JSON data for programmatic access
        json_data = {
            'analysis_metadata': {
                'generated_date': '2024-12-22',
                'versions_analyzed': list(self.versions.keys()),
                'total_fields': len(field_evolution_map),
                'semantic_domains': [domain.value for domain in SemanticDomain]
            },
            'domain_evolutions': {}
        }
        
        for domain, domain_evolution in domain_evolutions.items():
            json_data['domain_evolutions'][domain.value] = {
                'description': domain_evolution.description,
                'evolution_entries': [asdict(entry) for entry in domain_evolution.evolution_entries],
                'field_evolution_map': {
                    name: {
                        'field_name': evolution.field_name,
                        'semantic_domain': evolution.semantic_domain.value,
                        'versions_present': evolution.versions_present,
                        'format_changes': evolution.format_changes,
                        'semantic_changes': evolution.semantic_changes,
                        'data_type_changes': evolution.data_type_changes,
                        'length_changes': evolution.length_changes,
                        'validation_changes': evolution.validation_changes
                    }
                    for name, evolution in domain_evolution.field_evolution_map.items()
                },
                'compatibility_matrix': {
                    f"{from_v}_{to_v}": compatibility
                    for (from_v, to_v), compatibility in domain_evolution.compatibility_matrix.items()
                }
            }
        
        json_path = os.path.join(output_dir, "semantic_domain_analysis.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Analysis complete!")
        print(f"📄 Main report: {report_path}")
        print(f"📊 JSON data: {json_path}")
        print(f"📁 Domain reports: {output_dir}/domain_*_evolution.md")
        
        return json_data

def main():
    """Main execution function"""
    print("🔍 Starting EURING Semantic Domain Analysis...")
    
    analyzer = SemanticDomainAnalyzer()
    analysis_data = analyzer.generate_analysis_report()
    
    print(f"\n📈 Analysis Summary:")
    print(f"   - Versions analyzed: {len(analysis_data['analysis_metadata']['versions_analyzed'])}")
    print(f"   - Total fields: {analysis_data['analysis_metadata']['total_fields']}")
    print(f"   - Semantic domains: {len(analysis_data['analysis_metadata']['semantic_domains'])}")
    
    for domain_name, domain_data in analysis_data['domain_evolutions'].items():
        field_count = len(domain_data['field_evolution_map'])
        print(f"   - {domain_name.replace('_', ' ').title()}: {field_count} fields")

if __name__ == "__main__":
    main()