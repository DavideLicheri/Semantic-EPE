"""
Semantic Domain Mapper Service
Automatically assigns semantic domains to EURING fields based on their names and meanings
"""
from typing import Dict, List, Optional
from ..models.euring_models import SemanticDomain, FieldDefinition


class SemanticDomainMapper:
    """
    Maps EURING fields to semantic domains based on field names, descriptions, and semantic meanings
    """
    
    def __init__(self):
        # Mapping rules based on field names and semantic meanings
        self.field_name_mappings = {
            # Identification & Marking
            SemanticDomain.IDENTIFICATION_MARKING: [
                'scheme', 'scheme_code', 'ring_prefix', 'ring_number', 'ring_series',
                'identification_number', 'primary_identification_method',
                'verification_metal_ring', 'metal_ring_information', 'other_marks',
                'ring_type', 'ring_material', 'ring_condition', 'ring_readability'
            ],
            
            # Species
            SemanticDomain.SPECIES: [
                'species', 'species_reported', 'species_concluded', 'species_code',
                'taxonomy', 'subspecies', 'species_group', 'family', 'genus'
            ],
            
            # Demographics  
            SemanticDomain.DEMOGRAPHICS: [
                'sex', 'sex_reported', 'sex_concluded', 'age', 'age_reported', 'age_concluded',
                'status', 'brood_size', 'pullus_age', 'accuracy_pullus_age',
                'breeding_status', 'reproductive_status', 'maturity'
            ],
            
            # Temporal
            SemanticDomain.TEMPORAL: [
                'day', 'month', 'year', 'date', 'time', 'accuracy_date', 'accuracy_time',
                'elapsed_time', 'season', 'period', 'timestamp', 'datetime',
                'capture_date', 'recovery_date', 'observation_date'
            ],
            
            # Spatial
            SemanticDomain.SPATIAL: [
                'latitude', 'longitude', 'coordinates', 'area_code', 'area_code_edb',
                'accuracy_coordinates', 'location', 'place', 'site', 'region',
                'country', 'locality', 'habitat', 'elevation', 'distance', 'direction'
            ],
            
            # Biometrics
            SemanticDomain.BIOMETRICS: [
                'wing', 'weight', 'bill', 'tarsus', 'fat', 'muscle', 'moult',
                'body_mass', 'wing_length', 'bill_length', 'tarsus_length',
                'fat_score', 'muscle_score', 'moult_score', 'condition_score',
                'biometric', 'measurement', 'morphology'
            ],
            
            # Methodology
            SemanticDomain.METHODOLOGY: [
                'manipulation', 'moved_before', 'catching_method', 'lures_used',
                'condition_code', 'circumstances_code', 'circumstances_presumed',
                'euring_code_identifier', 'method', 'technique', 'protocol',
                'equipment', 'trap_type', 'net_type', 'capture_effort',
                'weather', 'conditions', 'observer', 'ringer'
            ]
        }
        
        # Semantic meaning mappings
        self.semantic_meaning_mappings = {
            SemanticDomain.IDENTIFICATION_MARKING: [
                'ringing scheme', 'ring number', 'ring series', 'metal ring',
                'identification', 'marking', 'scheme identifier', 'ring prefix'
            ],
            
            SemanticDomain.SPECIES: [
                'species', 'taxonomy', 'classification', 'scientific name',
                'common name', 'subspecies', 'family', 'genus'
            ],
            
            SemanticDomain.DEMOGRAPHICS: [
                'sex', 'age', 'gender', 'maturity', 'breeding', 'reproductive',
                'status', 'brood', 'pullus', 'demographic'
            ],
            
            SemanticDomain.TEMPORAL: [
                'date', 'time', 'temporal', 'chronological', 'when',
                'day', 'month', 'year', 'season', 'period', 'elapsed'
            ],
            
            SemanticDomain.SPATIAL: [
                'location', 'position', 'coordinates', 'latitude', 'longitude',
                'spatial', 'geographic', 'place', 'site', 'area', 'region',
                'distance', 'direction', 'where'
            ],
            
            SemanticDomain.BIOMETRICS: [
                'measurement', 'biometric', 'morphology', 'size', 'length',
                'weight', 'mass', 'wing', 'bill', 'tarsus', 'fat', 'muscle',
                'moult', 'condition', 'physical'
            ],
            
            SemanticDomain.METHODOLOGY: [
                'method', 'technique', 'protocol', 'procedure', 'how',
                'capture', 'catching', 'manipulation', 'circumstances',
                'conditions', 'equipment', 'trap', 'net', 'lure'
            ]
        }
    
    def assign_semantic_domain(self, field: FieldDefinition) -> SemanticDomain:
        """
        Assign a semantic domain to a field based on its name, description, and semantic meaning
        """
        field_name_lower = field.name.lower()
        description_lower = field.description.lower() if field.description else ""
        semantic_meaning_lower = field.semantic_meaning.lower() if field.semantic_meaning else ""
        
        # Combined text for analysis
        combined_text = f"{field_name_lower} {description_lower} {semantic_meaning_lower}"
        
        # Score each domain
        domain_scores = {}
        
        for domain, field_names in self.field_name_mappings.items():
            score = 0
            
            # Check field name matches
            for name_pattern in field_names:
                if name_pattern in field_name_lower:
                    score += 10  # High weight for field name matches
            
            # Check semantic meaning matches
            if domain in self.semantic_meaning_mappings:
                for meaning_pattern in self.semantic_meaning_mappings[domain]:
                    if meaning_pattern in combined_text:
                        score += 5  # Medium weight for semantic meaning matches
            
            domain_scores[domain] = score
        
        # Return domain with highest score, or default to METHODOLOGY if no clear match
        if max(domain_scores.values()) > 0:
            return max(domain_scores, key=domain_scores.get)
        else:
            return SemanticDomain.METHODOLOGY  # Default fallback
    
    def assign_domains_to_fields(self, fields: List[FieldDefinition]) -> List[FieldDefinition]:
        """
        Assign semantic domains to a list of fields
        """
        updated_fields = []
        
        for field in fields:
            # Only assign if not already assigned
            if field.semantic_domain is None:
                field.semantic_domain = self.assign_semantic_domain(field)
            updated_fields.append(field)
        
        return updated_fields
    
    def get_domain_statistics(self, fields: List[FieldDefinition]) -> Dict[SemanticDomain, int]:
        """
        Get statistics of domain distribution across fields
        """
        stats = {domain: 0 for domain in SemanticDomain}
        
        for field in fields:
            if field.semantic_domain:
                stats[field.semantic_domain] += 1
        
        return stats
    
    def validate_domain_assignment(self, field: FieldDefinition) -> bool:
        """
        Validate that a field's semantic domain assignment makes sense
        """
        if not field.semantic_domain:
            return False
        
        # Check if the assigned domain is reasonable based on field characteristics
        assigned_domain = field.semantic_domain
        expected_domain = self.assign_semantic_domain(field)
        
        return assigned_domain == expected_domain
    
    def get_unassigned_fields(self, fields: List[FieldDefinition]) -> List[FieldDefinition]:
        """
        Get fields that don't have semantic domains assigned
        """
        return [field for field in fields if field.semantic_domain is None]
    
    def reassign_all_domains(self, fields: List[FieldDefinition]) -> List[FieldDefinition]:
        """
        Reassign semantic domains to all fields (override existing assignments)
        """
        updated_fields = []
        
        for field in fields:
            field.semantic_domain = self.assign_semantic_domain(field)
            updated_fields.append(field)
        
        return updated_fields


# Global instance
semantic_domain_mapper = SemanticDomainMapper()