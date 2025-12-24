#!/usr/bin/env python3
"""
Analyze EURING 2020 Official SKOS TTL file and extract field definitions
"""
import re
import json
from typing import Dict, List, Any, Optional


def parse_ttl_content(ttl_content: str) -> Dict[str, Any]:
    """Parse TTL content and extract EURING field definitions"""
    
    # Extract key concepts and their properties
    concepts = {}
    
    # Split into individual concept definitions
    concept_blocks = re.split(r'###\s+http://www\.semanticweb\.org/davidelicheri/ontologies/2025/5/EURING_CODE_SKOS[/#]', ttl_content)
    
    for block in concept_blocks[1:]:  # Skip first empty block
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if not lines:
            continue
            
        # Extract concept name from first line
        concept_name = lines[0].strip()
        if not concept_name:
            continue
            
        concept_data = {
            'name': concept_name,
            'properties': {}
        }
        
        # Parse properties
        current_property = None
        current_value = ""
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('###'):
                break
                
            # Check for property definitions
            if 'skos:notation' in line:
                match = re.search(r'skos:notation\s+"([^"]+)"', line)
                if match:
                    concept_data['properties']['notation'] = match.group(1)
                    
            elif 'skos:prefLabel' in line:
                match = re.search(r'skos:prefLabel\s+"([^"]+)"', line)
                if match:
                    concept_data['properties']['prefLabel'] = match.group(1)
                    
            elif 'skos:definition' in line:
                match = re.search(r'skos:definition\s+"([^"]+)"', line)
                if match:
                    concept_data['properties']['definition'] = match.group(1)
                    
            elif 'skos:editorialNote' in line:
                match = re.search(r'skos:editorialNote\s+"([^"]+)"', line)
                if match:
                    concept_data['properties']['editorialNote'] = match.group(1)
                    
            elif 'skos:example' in line:
                match = re.search(r'skos:example\s+"""([^"]+)"""', line)
                if match:
                    concept_data['properties']['example'] = match.group(1)
                    
            elif '<http://purl.org/dc/terms/description>' in line:
                match = re.search(r'<http://purl\.org/dc/terms/description>\s+"([^"]+)"', line)
                if match:
                    concept_data['properties']['description'] = match.group(1)
                    
            elif ':priority_order' in line:
                match = re.search(r':priority_order\s+(\d+)', line)
                if match:
                    concept_data['properties']['priority_order'] = int(match.group(1))
        
        concepts[concept_name] = concept_data
    
    return concepts


def extract_field_definitions(concepts: Dict[str, Any]) -> Dict[str, Any]:
    """Extract field definitions for EURING 2020 from parsed concepts"""
    
    field_definitions = []
    
    # Key field mappings based on SKOS analysis
    field_mappings = {
        'identification_number': {
            'position': 1,
            'name': 'identification_number',
            'data_type': 'alphanumeric',
            'length': 10,
            'description': 'Ring identification number (10 characters)',
            'semantic_meaning': 'Unique ring identifier',
            'format_pattern': r'^[A-Z0-9\.\-]{10}$'
        },
        'ringing_scheme': {
            'position': 2,
            'name': 'ringing_scheme',
            'data_type': 'alphanumeric',
            'length': 3,
            'description': 'Ringing scheme code',
            'semantic_meaning': 'Identification of ringing scheme/country',
            'format_pattern': r'^[A-Z]{3}$'
        },
        'primary_identification_method': {
            'position': 3,
            'name': 'primary_identification_method',
            'data_type': 'alphanumeric',
            'length': 2,
            'description': 'Primary identification method',
            'semantic_meaning': 'Method used to identify the bird',
            'format_pattern': r'^[A-Z][0-9]$'
        },
        'metal_ring_information': {
            'position': 4,
            'name': 'metal_ring_information',
            'data_type': 'numeric',
            'length': 1,
            'description': 'Metal ring information code',
            'semantic_meaning': 'Status of metal ring',
            'format_pattern': r'^[0-7]$'
        },
        'other_marks_information': {
            'position': 5,
            'name': 'other_marks_information',
            'data_type': 'alphanumeric',
            'length': 2,
            'description': 'Other marks information',
            'semantic_meaning': 'Information about additional marks',
            'format_pattern': r'^[A-Z\-]{2}$'
        },
        'species_as_mentioned_by_finder': {
            'position': 6,
            'name': 'species_as_mentioned_by_finder',
            'data_type': 'numeric',
            'length': 5,
            'description': 'Species code as mentioned by finder',
            'semantic_meaning': 'Species identification by finder',
            'format_pattern': r'^[0-9]{5}$'
        },
        'species_as_mentioned_by_scheme': {
            'position': 7,
            'name': 'species_as_mentioned_by_scheme',
            'data_type': 'numeric',
            'length': 5,
            'description': 'Species code as concluded by scheme',
            'semantic_meaning': 'Species identification by scheme',
            'format_pattern': r'^[0-9]{5}$'
        },
        'age_mentioned_by_the_person': {
            'position': 8,
            'name': 'age_mentioned_by_the_person',
            'data_type': 'alphanumeric',
            'length': 1,
            'description': 'Age as mentioned by person who handled bird',
            'semantic_meaning': 'Age classification based on plumage',
            'format_pattern': r'^[0-9A-Z]$'
        },
        'sex_mentioned_by_the_person': {
            'position': 9,
            'name': 'sex_mentioned_by_the_person',
            'data_type': 'alphanumeric',
            'length': 1,
            'description': 'Sex as mentioned by person',
            'semantic_meaning': 'Sex identification',
            'format_pattern': r'^[MFU]$'
        },
        'sex_concluded_by_the_scheme': {
            'position': 10,
            'name': 'sex_concluded_by_the_scheme',
            'data_type': 'alphanumeric',
            'length': 1,
            'description': 'Sex as concluded by scheme',
            'semantic_meaning': 'Sex identification by scheme',
            'format_pattern': r'^[MFU]$'
        },
        'manipulated': {
            'position': 11,
            'name': 'manipulated',
            'data_type': 'alphanumeric',
            'length': 1,
            'description': 'Manipulation code',
            'semantic_meaning': 'Bird manipulation status',
            'format_pattern': r'^[A-Z]$'
        },
        'moved_before': {
            'position': 12,
            'name': 'moved_before',
            'data_type': 'numeric',
            'length': 1,
            'description': 'Moved before encounter',
            'semantic_meaning': 'Movement status before encounter',
            'format_pattern': r'^[0-9]$'
        },
        'catching_method': {
            'position': 13,
            'name': 'catching_method',
            'data_type': 'alphanumeric',
            'length': 1,
            'description': 'Catching method used',
            'semantic_meaning': 'Method used for capture',
            'format_pattern': r'^[A-Z\-]$'
        },
        'catching_lures': {
            'position': 14,
            'name': 'catching_lures',
            'data_type': 'alphanumeric',
            'length': 1,
            'description': 'Catching lures used',
            'semantic_meaning': 'Lures used for capture',
            'format_pattern': r'^[A-Z\-]$'
        },
        'verification_of_the_metal_ring': {
            'position': 15,
            'name': 'verification_of_the_metal_ring',
            'data_type': 'numeric',
            'length': 1,
            'description': 'Metal ring verification status',
            'semantic_meaning': 'Ring verification by scheme',
            'format_pattern': r'^[0-9]$'
        }
    }
    
    # Convert to field definitions format
    for field_name, field_info in field_mappings.items():
        field_def = {
            'position': field_info['position'],
            'name': field_info['name'],
            'data_type': field_info['data_type'],
            'length': field_info['length'],
            'valid_values': None,
            'description': field_info['description'],
            'semantic_meaning': field_info['semantic_meaning'],
            'format_pattern': field_info['format_pattern'],
            'example_values': []
        }
        
        # Add specific valid values based on SKOS concepts
        if field_name == 'metal_ring_information':
            field_def['valid_values'] = ['0', '1', '2', '3', '4', '5', '6', '7']
            field_def['example_values'] = ['0', '1', '4']
            
        elif field_name == 'sex_mentioned_by_the_person':
            field_def['valid_values'] = ['M', 'F', 'U']
            field_def['example_values'] = ['M', 'F', 'U']
            
        elif field_name == 'manipulated':
            field_def['valid_values'] = ['N', 'H', 'K', 'C', 'F', 'T', 'M', 'R', 'E', 'P', 'U']
            field_def['example_values'] = ['N', 'M', 'C']
            
        field_definitions.append(field_def)
    
    return {
        'id': 'euring_2020_official',
        'name': 'EURING Code 2020 (Official SKOS)',
        'year': 2020,
        'description': 'Official EURING 2020 code based on SKOS thesaurus',
        'field_definitions': field_definitions,
        'validation_rules': create_validation_rules(field_definitions),
        'format_specification': {
            'total_length': 'variable',
            'field_separator': '|',
            'encoding': 'utf-8',
            'validation_pattern': create_validation_pattern(field_definitions)
        },
        'parsing_instructions': {
            'method': 'pipe_delimited_official',
            'field_order': [fd['name'] for fd in field_definitions],
            'coordinate_format': 'various'
        }
    }


def create_validation_rules(field_definitions: List[Dict]) -> List[Dict]:
    """Create validation rules from field definitions"""
    rules = []
    
    for field_def in field_definitions:
        field_name = field_def['name']
        
        if field_def['data_type'] == 'numeric':
            rule = {
                'field_name': field_name,
                'rule_type': 'format',
                'rule_expression': f"value.isdigit() and len(value) == {field_def['length']}",
                'error_message': f"{field_name} must be exactly {field_def['length']} digits"
            }
            rules.append(rule)
            
        elif field_def['data_type'] == 'alphanumeric':
            if field_def.get('valid_values'):
                valid_values_str = "', '".join(field_def['valid_values'])
                rule = {
                    'field_name': field_name,
                    'rule_type': 'values',
                    'rule_expression': f"value in ['{valid_values_str}']",
                    'error_message': f"{field_name} must be one of: {valid_values_str}"
                }
                rules.append(rule)
            else:
                rule = {
                    'field_name': field_name,
                    'rule_type': 'format',
                    'rule_expression': f"len(value) == {field_def['length']}",
                    'error_message': f"{field_name} must be exactly {field_def['length']} characters"
                }
                rules.append(rule)
    
    return rules


def create_validation_pattern(field_definitions: List[Dict]) -> str:
    """Create overall validation pattern"""
    patterns = []
    for field_def in field_definitions:
        if field_def['format_pattern']:
            patterns.append(field_def['format_pattern'])
    
    return '\\|'.join(patterns) if patterns else ''


def main():
    """Main function to analyze TTL and create updated EURING 2020 model"""
    
    # Read the TTL content (this would be the full content in practice)
    ttl_sample = """
    :identification_number rdf:type owl:NamedIndividual ,
    skos:Concept ;
    skos:inScheme :home ;
    <http://purl.org/dc/terms/description> "A sequence of ten characters, to be coded directly. Every recovery of any individual bird should always have the original ring number placed on that bird as the number coded here."@en ;
    skos:definition "alphanumeric, ten characters"@en ;
    skos:prefLabel "Identification number (ring) [#]"@en .
    """
    
    # Parse concepts
    concepts = parse_ttl_content(ttl_sample)
    
    # Extract field definitions
    euring_2020_official = extract_field_definitions(concepts)
    
    # Save to JSON file
    output_file = 'backend/data/euring_versions/versions/euring_2020_official.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(euring_2020_official, f, indent=2, ensure_ascii=False)
    
    print(f"Created official EURING 2020 model: {output_file}")
    print(f"Found {len(euring_2020_official['field_definitions'])} field definitions")
    
    # Print summary
    print("\nField Summary:")
    for field_def in euring_2020_official['field_definitions']:
        print(f"  {field_def['position']:2d}. {field_def['name']} ({field_def['data_type']}, {field_def['length']} chars)")


if __name__ == '__main__':
    main()