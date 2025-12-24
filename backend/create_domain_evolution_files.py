#!/usr/bin/env python3
"""
Create Domain Evolution Files for SKOS Repository

This script converts the semantic domain analysis data into the format
expected by the SKOS repository for domain evolution loading.
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path
from app.models.euring_models import SemanticDomain, DomainCompatibilityLevel

def load_analysis_data() -> Dict[str, Any]:
    """Load the semantic domain analysis data"""
    analysis_file = Path("data/documentation/analysis/semantic_domain_analysis.json")
    
    if not analysis_file.exists():
        raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_compatibility_level(level_str: str) -> str:
    """Convert compatibility level string to enum value"""
    level_mapping = {
        'FULL': 'full',
        'PARTIAL': 'partial', 
        'LOSSY': 'lossy',
        'INCOMPATIBLE': 'incompatible'
    }
    return level_mapping.get(level_str, 'incompatible')

def create_domain_evolution_file(domain_name: str, domain_data: Dict[str, Any], output_dir: Path):
    """Create a domain evolution file for the SKOS repository"""
    
    # Convert domain name to SemanticDomain enum value
    try:
        domain_enum = SemanticDomain(domain_name)
    except ValueError:
        print(f"Warning: Unknown domain {domain_name}, skipping")
        return
    
    # Create the domain evolution structure
    evolution_entries = []
    for entry_data in domain_data['evolution_entries']:
        # Convert domain changes to the expected format
        changes = []
        
        # Add field changes
        for field_name in entry_data.get('fields_added', []):
            changes.append({
                'change_type': 'added',
                'field_name': field_name,
                'semantic_impact': f'New field added to {domain_name} domain',
                'compatibility_impact': 'partial',
                'previous_value': None,
                'new_value': 'field_added'
            })
        
        for field_name in entry_data.get('fields_removed', []):
            changes.append({
                'change_type': 'removed',
                'field_name': field_name,
                'semantic_impact': f'Field removed from {domain_name} domain',
                'compatibility_impact': 'lossy',
                'previous_value': 'field_existed',
                'new_value': None
            })
        
        for field_name in entry_data.get('fields_modified', []):
            changes.append({
                'change_type': 'modified',
                'field_name': field_name,
                'semantic_impact': f'Field modified in {domain_name} domain',
                'compatibility_impact': 'partial',
                'previous_value': 'previous_format',
                'new_value': 'new_format'
            })
        
        evolution_entry = {
            'version': entry_data['version'],
            'year': entry_data['year'],
            'changes': changes,
            'fields_added': entry_data.get('fields_added', []),
            'fields_removed': entry_data.get('fields_removed', []),
            'fields_modified': entry_data.get('fields_modified', []),
            'semantic_notes': entry_data.get('semantic_improvements', []),
            'format_changes': entry_data.get('format_changes', []),
            'field_mappings': []  # Add empty field mappings
        }
        
        evolution_entries.append(evolution_entry)
    
    # Create compatibility matrix
    compatibility_matrix = {
        'domain': domain_name,
        'compatibility_map': {}
    }
    
    for key, level in domain_data.get('compatibility_matrix', {}).items():
        # Convert key format from "version1_version2" to tuple format
        if '_' in key:
            from_version, to_version = key.split('_', 1)
            matrix_key = f"{from_version}->{to_version}"
            compatibility_matrix['compatibility_map'][matrix_key] = convert_compatibility_level(level)
    
    # Create the complete domain evolution structure
    domain_evolution = {
        'domain': domain_name,
        'evolution_entries': evolution_entries,
        'compatibility_matrix': compatibility_matrix,
        'field_evolution_map': domain_data.get('field_evolution_map', {})
    }
    
    # Save to file
    output_file = output_dir / f"{domain_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(domain_evolution, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created domain evolution file: {output_file}")

def main():
    """Main execution function"""
    print("🔄 Creating domain evolution files for SKOS repository...")
    
    # Load analysis data
    try:
        analysis_data = load_analysis_data()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please run 'python3 analyze_semantic_domains.py' first to generate the analysis data.")
        return
    
    # Create output directory
    output_dir = Path("data/euring_versions/domain_evolutions")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create domain evolution files
    domain_evolutions = analysis_data.get('domain_evolutions', {})
    
    for domain_name, domain_data in domain_evolutions.items():
        create_domain_evolution_file(domain_name, domain_data, output_dir)
    
    print(f"\n✅ Created {len(domain_evolutions)} domain evolution files")
    print(f"📁 Output directory: {output_dir}")
    
    # List created files
    print("\n📄 Created files:")
    for file_path in sorted(output_dir.glob("*.json")):
        print(f"   - {file_path.name}")

if __name__ == "__main__":
    main()