"""
Domain-Specific Conversion Service for EURING Code Recognition System

This service implements domain-specific conversion rules, transformation logic,
and compatibility assessment for each semantic domain.

Requirements: 5.4, 8.5
"""
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import json
from pathlib import Path

from ..models.euring_models import (
    SemanticDomain, DomainCompatibilityLevel, DomainConversionMapping,
    FieldMapping, TransformationRule, TransformationType,
    EuringVersion, FieldDefinition, ConversionMapping
)
from .domain_compatibility_assessor import DomainCompatibilityAssessor


class DomainConversionService:
    """
    Service for creating and managing domain-specific conversion rules.
    
    This service provides:
    - DomainConversionMapping creation for each semantic domain
    - Domain-specific transformation rules implementation
    - Domain compatibility level assessment
    """
    
    def __init__(self):
        self._domain_conversion_mappings: Dict[Tuple[str, str, SemanticDomain], DomainConversionMapping] = {}
        self._versions: Dict[str, EuringVersion] = {}
        self._compatibility_assessor = DomainCompatibilityAssessor()
        self._transformation_rules = self._initialize_transformation_rules()
    
    def load_versions(self, versions: List[EuringVersion]) -> None:
        """Load version data for domain conversion processing"""
        self._versions = {version.id: version for version in versions}
        self._compatibility_assessor.load_versions(versions)
    
    async def create_domain_conversion_mapping(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> DomainConversionMapping:
        """
        Create domain-specific conversion mapping between two versions.
        
        Args:
            domain: The semantic domain to create mapping for
            from_version: Source version for conversion
            to_version: Target version for conversion
            
        Returns:
            DomainConversionMapping with domain-specific rules and transformations
            
        Validates: Requirements 5.4, 8.5
        """
        if from_version not in self._versions or to_version not in self._versions:
            raise ValueError(f"Version not found: {from_version} or {to_version}")
        
        # Get domain fields for both versions
        from_fields = self._get_domain_fields(domain, from_version)
        to_fields = self._get_domain_fields(domain, to_version)
        
        # Create field mappings for this domain
        field_mappings = await self._create_domain_field_mappings(
            domain, from_fields, to_fields, from_version, to_version
        )
        
        # Create transformation rules for this domain
        transformation_rules = await self._create_domain_transformation_rules(
            domain, from_fields, to_fields, from_version, to_version
        )
        
        # Assess compatibility level for this domain
        try:
            compatibility_result = await self._compatibility_assessor.assess_domain_compatibility(
                domain, from_version, to_version, detailed_analysis=True
            )
            compatibility_level = DomainCompatibilityLevel(compatibility_result.compatibility_level)
            is_lossy = compatibility_result.is_lossy
        except ValueError:
            # Domain evolution data not available, use basic assessment
            compatibility_level = self._assess_basic_compatibility(
                domain, from_fields, to_fields, from_version, to_version
            )
            is_lossy = self._detect_basic_lossy_conversion(from_fields, to_fields)
        
        # Generate conversion notes
        conversion_notes = await self._generate_domain_conversion_notes(
            domain, from_version, to_version, compatibility_level, is_lossy
        )
        
        domain_mapping = DomainConversionMapping(
            domain=domain,
            compatibility=compatibility_level,
            field_mappings=field_mappings,
            transformation_rules=transformation_rules,
            lossy_conversion=is_lossy,
            conversion_notes=conversion_notes
        )
        
        # Cache the mapping
        mapping_key = (from_version, to_version, domain)
        self._domain_conversion_mappings[mapping_key] = domain_mapping
        
        return domain_mapping
    
    async def get_domain_conversion_mapping(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Optional[DomainConversionMapping]:
        """Get existing domain conversion mapping or create if not exists"""
        mapping_key = (from_version, to_version, domain)
        
        if mapping_key in self._domain_conversion_mappings:
            return self._domain_conversion_mappings[mapping_key]
        
        # Create new mapping if not exists
        try:
            return await self.create_domain_conversion_mapping(domain, from_version, to_version)
        except Exception:
            return None
    
    async def create_all_domain_conversion_mappings(
        self,
        from_version: str,
        to_version: str
    ) -> List[DomainConversionMapping]:
        """Create conversion mappings for all domains between two versions"""
        domain_mappings = []
        
        for domain in SemanticDomain:
            try:
                mapping = await self.create_domain_conversion_mapping(
                    domain, from_version, to_version
                )
                domain_mappings.append(mapping)
            except Exception as e:
                # Log error but continue with other domains
                print(f"Warning: Could not create mapping for domain {domain.value}: {e}")
                continue
        
        return domain_mappings
    
    async def update_conversion_mapping_with_domains(
        self,
        conversion_mapping: ConversionMapping
    ) -> ConversionMapping:
        """Update existing conversion mapping with domain-specific mappings"""
        if conversion_mapping.domain_mappings is None:
            conversion_mapping.domain_mappings = []
        
        # Create domain mappings for all domains
        domain_mappings = await self.create_all_domain_conversion_mappings(
            conversion_mapping.from_version,
            conversion_mapping.to_version
        )
        
        # Update the conversion mapping
        conversion_mapping.domain_mappings = domain_mappings
        
        return conversion_mapping
    
    async def assess_domain_compatibility_level(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> DomainCompatibilityLevel:
        """Assess compatibility level for a specific domain between versions"""
        try:
            result = await self._compatibility_assessor.assess_domain_compatibility(
                domain, from_version, to_version, detailed_analysis=False
            )
            return DomainCompatibilityLevel(result.compatibility_level)
        except ValueError:
            # Domain evolution data not available, use basic assessment
            from_fields = self._get_domain_fields(domain, from_version)
            to_fields = self._get_domain_fields(domain, to_version)
            return self._assess_basic_compatibility(
                domain, from_fields, to_fields, from_version, to_version
            )
    
    async def get_domain_transformation_rules(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> List[TransformationRule]:
        """Get transformation rules specific to a domain"""
        mapping = await self.get_domain_conversion_mapping(domain, from_version, to_version)
        if mapping:
            return mapping.transformation_rules
        return []
    
    async def apply_domain_transformation(
        self,
        domain: SemanticDomain,
        field_data: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Apply domain-specific transformations to field data"""
        mapping = await self.get_domain_conversion_mapping(domain, from_version, to_version)
        if not mapping:
            return field_data
        
        transformed_data = field_data.copy()
        
        # Apply field mappings
        for field_mapping in mapping.field_mappings:
            if field_mapping.source_field in field_data:
                source_value = field_data[field_mapping.source_field]
                transformed_value = await self._apply_field_transformation(
                    source_value, field_mapping, domain, from_version, to_version
                )
                transformed_data[field_mapping.target_field] = transformed_value
        
        # Apply transformation rules
        for rule in mapping.transformation_rules:
            transformed_data = await self._apply_transformation_rule(
                transformed_data, rule, domain, from_version, to_version
            )
        
        return transformed_data
    
    def _get_domain_fields(
        self,
        domain: SemanticDomain,
        version: str
    ) -> List[FieldDefinition]:
        """Get fields belonging to a domain in a specific version"""
        if version not in self._versions:
            return []
        
        version_obj = self._versions[version]
        return [
            field for field in version_obj.field_definitions
            if field.semantic_domain == domain
        ]
    
    async def _create_domain_field_mappings(
        self,
        domain: SemanticDomain,
        from_fields: List[FieldDefinition],
        to_fields: List[FieldDefinition],
        from_version: str,
        to_version: str
    ) -> List[FieldMapping]:
        """Create field mappings specific to a domain"""
        field_mappings = []
        
        # Create mappings for each source field
        for from_field in from_fields:
            # Find corresponding field in target version
            to_field = self._find_corresponding_field(from_field, to_fields)
            
            if to_field:
                # Determine transformation type based on field compatibility
                transformation_type = self._determine_transformation_type(from_field, to_field)
                
                # Calculate conversion accuracy
                accuracy = self._calculate_conversion_accuracy(from_field, to_field)
                
                field_mapping = FieldMapping(
                    source_field=from_field.name,
                    target_field=to_field.name,
                    transformation_type=transformation_type,
                    transformation_function=self._get_transformation_function(
                        from_field, to_field, domain, from_version, to_version
                    ),
                    semantic_domain=domain,
                    conversion_accuracy=accuracy
                )
                field_mappings.append(field_mapping)
        
        return field_mappings
    
    async def _create_domain_transformation_rules(
        self,
        domain: SemanticDomain,
        from_fields: List[FieldDefinition],
        to_fields: List[FieldDefinition],
        from_version: str,
        to_version: str
    ) -> List[TransformationRule]:
        """Create transformation rules specific to a domain"""
        transformation_rules = []
        
        # Get domain-specific transformation rules
        domain_rules = self._transformation_rules.get(domain, {})
        version_pair_key = f"{from_version}_to_{to_version}"
        
        if version_pair_key in domain_rules:
            for rule_config in domain_rules[version_pair_key]:
                rule = TransformationRule(
                    rule_id=f"{domain.value}_{rule_config['rule_id']}",
                    source_field=rule_config.get('source_field'),
                    target_field=rule_config['target_field'],
                    transformation_type=TransformationType(rule_config['transformation_type']),
                    transformation_expression=rule_config['transformation_expression'],
                    conditions=rule_config.get('conditions')
                )
                transformation_rules.append(rule)
        
        # Add default rules for missing fields
        to_field_names = {field.name for field in to_fields}
        from_field_names = {field.name for field in from_fields}
        
        # Rules for new fields in target version
        for to_field in to_fields:
            if to_field.name not in from_field_names:
                default_rule = self._create_default_field_rule(to_field, domain)
                if default_rule:
                    transformation_rules.append(default_rule)
        
        return transformation_rules
    
    def _find_corresponding_field(
        self,
        source_field: FieldDefinition,
        target_fields: List[FieldDefinition]
    ) -> Optional[FieldDefinition]:
        """Find corresponding field in target version"""
        # First try exact name match
        for field in target_fields:
            if field.name == source_field.name:
                return field
        
        # Then try semantic meaning match
        if source_field.semantic_meaning:
            for field in target_fields:
                if (field.semantic_meaning and 
                    field.semantic_meaning == source_field.semantic_meaning):
                    return field
        
        # Finally try position-based matching for similar fields
        for field in target_fields:
            if (abs(field.position - source_field.position) <= 2 and
                field.data_type == source_field.data_type):
                return field
        
        return None
    
    def _determine_transformation_type(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition
    ) -> TransformationType:
        """Determine the type of transformation needed between fields"""
        if (from_field.data_type == to_field.data_type and
            from_field.length == to_field.length and
            from_field.valid_values == to_field.valid_values):
            return TransformationType.DIRECT
        
        if from_field.data_type != to_field.data_type:
            return TransformationType.CALCULATED
        
        if from_field.length != to_field.length:
            return TransformationType.CALCULATED
        
        if from_field.valid_values != to_field.valid_values:
            return TransformationType.CONDITIONAL
        
        return TransformationType.DIRECT
    
    def _calculate_conversion_accuracy(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition
    ) -> float:
        """Calculate conversion accuracy between two fields"""
        accuracy = 1.0
        
        # Reduce accuracy for data type changes
        if from_field.data_type != to_field.data_type:
            accuracy *= 0.8
        
        # Reduce accuracy for length reductions
        if from_field.length > to_field.length:
            accuracy *= 0.7
        
        # Reduce accuracy for valid value mismatches
        if (from_field.valid_values and to_field.valid_values and
            set(from_field.valid_values) != set(to_field.valid_values)):
            accuracy *= 0.9
        
        # Reduce accuracy for semantic meaning changes
        if (from_field.semantic_meaning and to_field.semantic_meaning and
            from_field.semantic_meaning != to_field.semantic_meaning):
            accuracy *= 0.6
        
        return max(accuracy, 0.1)  # Minimum 10% accuracy
    
    def _get_transformation_function(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Optional[str]:
        """Get transformation function for field conversion"""
        # Domain-specific transformation functions
        domain_functions = {
            SemanticDomain.IDENTIFICATION_MARKING: {
                'ring_number': self._get_ring_number_transformation,
                'scheme_code': self._get_scheme_transformation,
            },
            SemanticDomain.SPECIES: {
                'species_code': self._get_species_code_transformation,
            },
            SemanticDomain.DEMOGRAPHICS: {
                'age_code': self._get_age_code_transformation,
                'sex_code': self._get_sex_code_transformation,
            },
            SemanticDomain.TEMPORAL: {
                'date_code': self._get_date_transformation,
                'time_code': self._get_time_transformation,
            },
            SemanticDomain.SPATIAL: {
                'latitude': self._get_coordinate_transformation,
                'longitude': self._get_coordinate_transformation,
            },
            SemanticDomain.BIOMETRICS: {
                'wing_length': self._get_measurement_transformation,
                'weight': self._get_measurement_transformation,
                'bill_length': self._get_measurement_transformation,
            },
            SemanticDomain.METHODOLOGY: {
                'method_code': self._get_method_transformation,
                'condition_code': self._get_condition_transformation,
            }
        }
        
        if domain in domain_functions:
            field_functions = domain_functions[domain]
            for field_pattern, func in field_functions.items():
                if field_pattern in from_field.name.lower():
                    return func(from_field, to_field, from_version, to_version)
        
        # Default transformation based on field types
        if from_field.data_type != to_field.data_type:
            return f"convert_{from_field.data_type}_to_{to_field.data_type}"
        
        if from_field.length != to_field.length:
            if from_field.length > to_field.length:
                return f"truncate_to_length({to_field.length})"
            else:
                return f"pad_to_length({to_field.length})"
        
        return None
    
    def _create_default_field_rule(
        self,
        field: FieldDefinition,
        domain: SemanticDomain
    ) -> Optional[TransformationRule]:
        """Create default rule for new fields in target version"""
        # Domain-specific default values
        default_values = {
            SemanticDomain.IDENTIFICATION_MARKING: {
                'metal_ring_info': '0',
                'other_marks_info': '00000',
                'verification_code': '0',
            },
            SemanticDomain.DEMOGRAPHICS: {
                'sex_code': '9',  # Unknown
            },
            SemanticDomain.TEMPORAL: {
                'time_code': '1200',  # Noon
            },
            SemanticDomain.SPATIAL: {
                'accuracy_code': '01',
            },
            SemanticDomain.BIOMETRICS: {
                'fat_score': '0',
                'muscle_score': '0',
                'moult_code': '0',
            },
            SemanticDomain.METHODOLOGY: {
                'status_info': '0',
            }
        }
        
        domain_defaults = default_values.get(domain, {})
        
        for field_pattern, default_value in domain_defaults.items():
            if field_pattern in field.name.lower():
                return TransformationRule(
                    rule_id=f"default_{field.name}",
                    source_field=None,
                    target_field=field.name,
                    transformation_type=TransformationType.CALCULATED,
                    transformation_expression=f"'{default_value}'",
                    conditions=None
                )
        
        # Generic default based on data type
        if field.data_type == 'integer':
            default_value = '0'
        elif field.data_type == 'float':
            default_value = '0.0'
        elif field.data_type == 'string':
            default_value = "''"
        else:
            default_value = 'None'
        
        return TransformationRule(
            rule_id=f"default_{field.name}",
            source_field=None,
            target_field=field.name,
            transformation_type=TransformationType.CALCULATED,
            transformation_expression=default_value,
            conditions=None
        )
    
    async def _generate_domain_conversion_notes(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str,
        compatibility_level: DomainCompatibilityLevel,
        is_lossy: bool
    ) -> List[str]:
        """Generate conversion notes specific to domain and version pair"""
        notes = []
        
        # Add compatibility level note
        if compatibility_level == DomainCompatibilityLevel.FULL:
            notes.append(f"Full compatibility for {domain.value} domain")
        elif compatibility_level == DomainCompatibilityLevel.PARTIAL:
            notes.append(f"Partial compatibility for {domain.value} domain - minor adjustments needed")
        elif compatibility_level == DomainCompatibilityLevel.LOSSY:
            notes.append(f"Lossy conversion for {domain.value} domain - some information will be lost")
        else:
            notes.append(f"Incompatible conversion for {domain.value} domain")
        
        # Add lossy conversion note
        if is_lossy:
            notes.append(f"Information loss detected in {domain.value} domain conversion")
        
        # Add domain-specific notes
        domain_specific_notes = self._get_domain_specific_conversion_notes(
            domain, from_version, to_version
        )
        notes.extend(domain_specific_notes)
        
        return notes
    
    def _get_domain_specific_conversion_notes(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> List[str]:
        """Get domain-specific conversion notes"""
        notes = []
        
        if domain == SemanticDomain.IDENTIFICATION_MARKING:
            if "1966" in from_version and "2020" in to_version:
                notes.append("Ring number format significantly expanded in 2020")
                notes.append("Metal ring and other marks information added")
            elif "2020" in from_version and "1966" in to_version:
                notes.append("Ring number format will be truncated")
                notes.append("Metal ring and other marks information will be lost")
        
        elif domain == SemanticDomain.TEMPORAL:
            if "1966" in from_version:
                notes.append("Time information not available in 1966, using default noon")
            if "2020" in to_version:
                notes.append("Enhanced time precision available in 2020 format")
        
        elif domain == SemanticDomain.SPATIAL:
            if "1966" in from_version and "2020" in to_version:
                notes.append("Coordinate format converted from degrees/minutes to decimal")
                notes.append("Accuracy information added based on original precision")
            elif "2020" in from_version and "1966" in to_version:
                notes.append("Decimal coordinates converted to degrees/minutes format")
                notes.append("Some precision may be lost in conversion")
        
        elif domain == SemanticDomain.BIOMETRICS:
            if "1966" in from_version:
                notes.append("Limited biometric measurements in 1966 format")
                notes.append("Additional measurements will use default values")
            if "2020" in to_version:
                notes.append("Enhanced biometric tracking available in 2020")
        
        elif domain == SemanticDomain.METHODOLOGY:
            if "2020" in to_version:
                notes.append("Enhanced methodology and status tracking in 2020")
            elif "1966" in to_version:
                notes.append("Simplified methodology information in 1966 format")
        
        return notes
    
    # Transformation function generators for different domains
    def _get_ring_number_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get ring number transformation function"""
        if "1966" in from_version and "2020" in to_version:
            return "expand_ring_number_1966_to_2020"
        elif "2020" in from_version and "1966" in to_version:
            return "truncate_ring_number_2020_to_1966"
        elif from_field.length != to_field.length:
            if from_field.length > to_field.length:
                return f"truncate_to_length({to_field.length})"
            else:
                return f"pad_to_length({to_field.length})"
        return "direct_copy"
    
    def _get_species_code_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get species code transformation function"""
        if from_field.length != to_field.length:
            if from_field.length < to_field.length:
                return f"pad_species_code_to_length({to_field.length})"
            else:
                return f"truncate_species_code_to_length({to_field.length})"
        return "direct_copy"
    
    def _get_age_code_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get age code transformation function"""
        if "1966" in from_version and "2000" in to_version:
            return "convert_age_1966_to_2000"
        elif "2000" in from_version and "1966" in to_version:
            return "convert_age_2000_to_1966"
        return "direct_copy"
    
    def _get_sex_code_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get sex code transformation function"""
        return "direct_copy"  # Sex codes are generally stable
    
    def _get_date_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get date transformation function"""
        if "1966" in from_version and "2020" in to_version:
            return "convert_date_ddmmyyyy_to_yyyymmdd"
        elif "2020" in from_version and "1966" in to_version:
            return "convert_date_yyyymmdd_to_ddmmyyyy"
        return "direct_copy"
    
    def _get_time_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get time transformation function"""
        return "default_time_1200"  # Most older versions don't have time
    
    def _get_coordinate_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get coordinate transformation function"""
        if "1966" in from_version and "2020" in to_version:
            return "convert_degrees_minutes_to_decimal"
        elif "2020" in from_version and "1966" in to_version:
            return "convert_decimal_to_degrees_minutes"
        return "direct_copy"
    
    def _get_measurement_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get measurement transformation function"""
        if from_field.data_type != to_field.data_type:
            return f"convert_{from_field.data_type}_to_{to_field.data_type}"
        return "direct_copy"
    
    def _get_method_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get method code transformation function"""
        if from_field.length != to_field.length:
            if from_field.length < to_field.length:
                return f"pad_method_code_to_length({to_field.length})"
            else:
                return f"truncate_method_code_to_length({to_field.length})"
        return "direct_copy"
    
    def _get_condition_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get condition code transformation function"""
        return "direct_copy"
    
    def _get_scheme_transformation(
        self, from_field: FieldDefinition, to_field: FieldDefinition,
        from_version: str, to_version: str
    ) -> str:
        """Get scheme code transformation function"""
        return "direct_copy"
    
    async def _apply_field_transformation(
        self,
        source_value: Any,
        field_mapping: FieldMapping,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Any:
        """Apply transformation to a field value"""
        if field_mapping.transformation_type == TransformationType.DIRECT:
            return source_value
        
        # Apply transformation function if specified
        if field_mapping.transformation_function:
            return await self._execute_transformation_function(
                source_value, field_mapping.transformation_function
            )
        
        return source_value
    
    async def _apply_transformation_rule(
        self,
        data: Dict[str, Any],
        rule: TransformationRule,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Apply a transformation rule to data"""
        if rule.transformation_type == TransformationType.CALCULATED:
            # Execute the transformation expression
            try:
                if rule.source_field and rule.source_field in data:
                    source_value = data[rule.source_field]
                    # Simple expression evaluation (in production, use safer evaluation)
                    if rule.transformation_expression.startswith("'") and rule.transformation_expression.endswith("'"):
                        # String literal
                        result = rule.transformation_expression[1:-1]
                    else:
                        # For now, just use the expression as-is
                        result = rule.transformation_expression
                else:
                    # No source field, use expression directly
                    if rule.transformation_expression.startswith("'") and rule.transformation_expression.endswith("'"):
                        result = rule.transformation_expression[1:-1]
                    else:
                        result = rule.transformation_expression
                
                data[rule.target_field] = result
            except Exception:
                # If transformation fails, use default value
                data[rule.target_field] = "0"
        
        return data
    
    async def _execute_transformation_function(
        self,
        value: Any,
        function_name: str
    ) -> Any:
        """Execute a named transformation function"""
        # This is a simplified implementation
        # In production, you would have a registry of transformation functions
        
        if function_name == "direct_copy":
            return value
        elif function_name.startswith("pad_to_length("):
            length = int(function_name.split("(")[1].split(")")[0])
            return str(value).ljust(length, '0')
        elif function_name.startswith("truncate_to_length("):
            length = int(function_name.split("(")[1].split(")")[0])
            return str(value)[:length]
        elif function_name == "default_time_1200":
            return "1200"
        else:
            # Unknown function, return original value
            return value
    
    def _initialize_transformation_rules(self) -> Dict[SemanticDomain, Dict[str, List[Dict[str, Any]]]]:
        """Initialize domain-specific transformation rules"""
        return {
            SemanticDomain.IDENTIFICATION_MARKING: {
                "1966_to_2020": [
                    {
                        "rule_id": "default_metal_ring",
                        "target_field": "metal_ring_info",
                        "transformation_type": "calculated",
                        "transformation_expression": "'0'"
                    },
                    {
                        "rule_id": "default_other_marks",
                        "target_field": "other_marks_info",
                        "transformation_type": "calculated",
                        "transformation_expression": "'00000'"
                    }
                ]
            },
            SemanticDomain.TEMPORAL: {
                "1966_to_2020": [
                    {
                        "rule_id": "default_time",
                        "target_field": "time_code",
                        "transformation_type": "calculated",
                        "transformation_expression": "'1200'"
                    }
                ]
            },
            SemanticDomain.SPATIAL: {
                "1966_to_2020": [
                    {
                        "rule_id": "default_accuracy",
                        "target_field": "accuracy_code",
                        "transformation_type": "calculated",
                        "transformation_expression": "'01'"
                    }
                ]
            },
            SemanticDomain.BIOMETRICS: {
                "1966_to_2020": [
                    {
                        "rule_id": "default_fat_score",
                        "target_field": "fat_score",
                        "transformation_type": "calculated",
                        "transformation_expression": "'0'"
                    },
                    {
                        "rule_id": "default_muscle_score",
                        "target_field": "muscle_score",
                        "transformation_type": "calculated",
                        "transformation_expression": "'0'"
                    },
                    {
                        "rule_id": "default_moult_code",
                        "target_field": "moult_code",
                        "transformation_type": "calculated",
                        "transformation_expression": "'0'"
                    }
                ]
            },
            SemanticDomain.METHODOLOGY: {
                "1966_to_2020": [
                    {
                        "rule_id": "default_status_info",
                        "target_field": "status_info",
                        "transformation_type": "calculated",
                        "transformation_expression": "'0'"
                    },
                    {
                        "rule_id": "default_verification",
                        "target_field": "verification_code",
                        "transformation_type": "calculated",
                        "transformation_expression": "'0'"
                    }
                ]
            }
        }
    
    def _assess_basic_compatibility(
        self,
        domain: SemanticDomain,
        from_fields: List[FieldDefinition],
        to_fields: List[FieldDefinition],
        from_version: str,
        to_version: str
    ) -> DomainCompatibilityLevel:
        """Basic compatibility assessment when domain evolution data is not available"""
        if not from_fields and not to_fields:
            return DomainCompatibilityLevel.FULL
        
        if not from_fields or not to_fields:
            return DomainCompatibilityLevel.INCOMPATIBLE
        
        # Calculate field compatibility ratios
        total_from_fields = len(from_fields)
        compatible_fields = 0
        partial_fields = 0
        
        for from_field in from_fields:
            to_field = self._find_corresponding_field(from_field, to_fields)
            
            if to_field is None:
                continue  # Incompatible field
            
            # Check field compatibility
            if (from_field.name == to_field.name and
                from_field.data_type == to_field.data_type and
                from_field.semantic_meaning == to_field.semantic_meaning):
                compatible_fields += 1
            else:
                partial_fields += 1
        
        # Calculate compatibility based on ratios
        if compatible_fields == total_from_fields:
            return DomainCompatibilityLevel.FULL
        elif (compatible_fields + partial_fields) / total_from_fields >= 0.7:
            return DomainCompatibilityLevel.PARTIAL
        elif (compatible_fields + partial_fields) / total_from_fields >= 0.3:
            return DomainCompatibilityLevel.LOSSY
        else:
            return DomainCompatibilityLevel.INCOMPATIBLE
    
    def _detect_basic_lossy_conversion(
        self,
        from_fields: List[FieldDefinition],
        to_fields: List[FieldDefinition]
    ) -> bool:
        """Basic lossy conversion detection"""
        for from_field in from_fields:
            to_field = self._find_corresponding_field(from_field, to_fields)
            
            if to_field is None:
                return True  # Field will be lost
            
            # Check for precision loss
            if from_field.length > to_field.length:
                return True
            
            # Check for data type changes that might cause loss
            if (from_field.data_type == 'float' and to_field.data_type == 'integer'):
                return True
        
        return False