"""
Domain Compatibility Assessment Service for EURING Code Recognition System

This service provides domain-specific conversion compatibility checking,
lossy conversion detection and reporting, and compatibility matrices for each domain pair.

Requirements: 8.5
"""
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from datetime import datetime
from ..models.euring_models import (
    SemanticDomain, DomainCompatibilityLevel, DomainCompatibilityMatrix,
    DomainEvolution, DomainEvolutionEntry, DomainChange, DomainChangeType,
    EuringVersion, FieldDefinition, FieldMapping, DomainConversionMapping,
    TransformationRule, TransformationType
)
from .domain_evolution_analyzer import DomainEvolutionAnalyzer


class ConversionLossType(str, Enum):
    """Types of information loss during conversion"""
    FIELD_REMOVED = "field_removed"
    PRECISION_LOST = "precision_lost"
    FORMAT_CHANGED = "format_changed"
    SEMANTIC_CHANGED = "semantic_changed"
    VALIDATION_RELAXED = "validation_relaxed"
    ENCODING_CHANGED = "encoding_changed"


class CompatibilityAssessmentResult(dict):
    """Result of domain compatibility assessment"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.domain = kwargs.get('domain')
        self.from_version = kwargs.get('from_version')
        self.to_version = kwargs.get('to_version')
        self.compatibility_level = kwargs.get('compatibility_level')
        self.is_lossy = kwargs.get('is_lossy', False)
        self.loss_details = kwargs.get('loss_details', [])
        self.field_compatibility = kwargs.get('field_compatibility', {})
        self.conversion_warnings = kwargs.get('conversion_warnings', [])
        self.conversion_notes = kwargs.get('conversion_notes', [])


class DomainCompatibilityAssessor:
    """
    Service for assessing domain-specific conversion compatibility.
    
    This assessor provides:
    - Domain-specific conversion compatibility checking
    - Lossy conversion detection and detailed reporting
    - Compatibility matrices for each domain pair
    """
    
    def __init__(self):
        self._domain_evolutions: Dict[SemanticDomain, DomainEvolution] = {}
        self._version_cache: Dict[str, EuringVersion] = {}
        self._compatibility_matrices: Dict[SemanticDomain, DomainCompatibilityMatrix] = {}
        self._domain_analyzer = DomainEvolutionAnalyzer()
    
    def load_domain_evolutions(self, domain_evolutions: List[DomainEvolution]) -> None:
        """Load domain evolution data for compatibility assessment"""
        self._domain_evolutions = {
            evolution.domain: evolution for evolution in domain_evolutions
        }
        
        # Extract compatibility matrices
        for evolution in domain_evolutions:
            self._compatibility_matrices[evolution.domain] = evolution.compatibility_matrix
    
    def load_versions(self, versions: List[EuringVersion]) -> None:
        """Load version data for compatibility assessment"""
        self._version_cache = {version.id: version for version in versions}
        self._domain_analyzer.load_versions(versions)
    
    async def assess_domain_compatibility(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str,
        detailed_analysis: bool = True
    ) -> CompatibilityAssessmentResult:
        """
        Assess conversion compatibility for a specific domain between two versions.
        
        Args:
            domain: The semantic domain to assess
            from_version: Source version for conversion
            to_version: Target version for conversion
            detailed_analysis: Whether to perform detailed field-level analysis
            
        Returns:
            CompatibilityAssessmentResult with comprehensive compatibility information
            
        Validates: Requirements 8.5
        """
        if domain not in self._domain_evolutions:
            raise ValueError(f"Domain {domain.value} not found in evolution data")
        
        if from_version not in self._version_cache or to_version not in self._version_cache:
            raise ValueError(f"Version not found: {from_version} or {to_version}")
        
        # Special case: same version comparison should always be FULL compatibility
        if from_version == to_version:
            return CompatibilityAssessmentResult(
                domain=domain.value,
                from_version=from_version,
                to_version=to_version,
                compatibility_level="full",
                is_lossy=False,
                loss_details=[],
                field_compatibility={},
                conversion_warnings=[],
                conversion_notes=[f"Same version comparison: {from_version} is fully compatible with itself"],
                assessment_metadata={
                    "detailed_analysis_performed": detailed_analysis,
                    "same_version_comparison": True,
                    "assessment_timestamp": datetime.now().isoformat()
                }
            )
        
        # Get basic compatibility level from matrix
        compatibility_matrix = self._compatibility_matrices.get(domain)
        if compatibility_matrix:
            base_compatibility = compatibility_matrix.get_compatibility(from_version, to_version)
        else:
            base_compatibility = DomainCompatibilityLevel.INCOMPATIBLE
        
        # Perform detailed analysis if requested
        if detailed_analysis:
            detailed_result = await self._perform_detailed_compatibility_analysis(
                domain, from_version, to_version, base_compatibility
            )
        else:
            detailed_result = {
                'field_compatibility': {},
                'loss_details': [],
                'conversion_warnings': [],
                'conversion_notes': []
            }
        
        # Detect lossy conversion
        is_lossy, loss_details = await self._detect_lossy_conversion(
            domain, from_version, to_version
        )
        
        # Generate conversion warnings and notes
        warnings = await self._generate_conversion_warnings(
            domain, from_version, to_version, base_compatibility, is_lossy
        )
        
        notes = await self._generate_conversion_notes(
            domain, from_version, to_version, base_compatibility
        )
        
        return CompatibilityAssessmentResult(
            domain=domain.value,
            from_version=from_version,
            to_version=to_version,
            compatibility_level=base_compatibility.value,
            is_lossy=is_lossy,
            loss_details=loss_details + detailed_result['loss_details'],
            field_compatibility=detailed_result['field_compatibility'],
            conversion_warnings=warnings + detailed_result['conversion_warnings'],
            conversion_notes=notes + detailed_result['conversion_notes'],
            assessment_metadata={
                'detailed_analysis_performed': detailed_analysis,
                'assessment_timestamp': self._get_current_timestamp(),
                'assessor_version': '1.0.0'
            }
        )
    
    async def create_domain_compatibility_matrix(
        self,
        domain: SemanticDomain,
        versions: Optional[List[str]] = None
    ) -> DomainCompatibilityMatrix:
        """
        Create or update compatibility matrix for a specific domain.
        
        Args:
            domain: The semantic domain to create matrix for
            versions: Optional list of versions to include (uses all cached versions if None)
            
        Returns:
            DomainCompatibilityMatrix with all version pair compatibilities
            
        Validates: Requirements 8.5
        """
        if versions is None:
            versions = list(self._version_cache.keys())
        
        # Create new compatibility matrix
        compatibility_matrix = DomainCompatibilityMatrix(domain=domain)
        
        # Assess compatibility for all version pairs
        for from_version in versions:
            for to_version in versions:
                if from_version != to_version:
                    compatibility_level = await self._calculate_version_pair_compatibility(
                        domain, from_version, to_version
                    )
                    compatibility_matrix.set_compatibility(
                        from_version, to_version, compatibility_level
                    )
        
        # Update cached matrix
        self._compatibility_matrices[domain] = compatibility_matrix
        
        return compatibility_matrix
    
    async def get_all_domain_compatibility_matrices(self) -> Dict[SemanticDomain, DomainCompatibilityMatrix]:
        """
        Get compatibility matrices for all domains.
        
        Returns:
            Dictionary mapping each domain to its compatibility matrix
            
        Validates: Requirements 8.5
        """
        matrices = {}
        
        for domain in SemanticDomain:
            if domain in self._compatibility_matrices:
                matrices[domain] = self._compatibility_matrices[domain]
            else:
                # Create matrix if it doesn't exist
                matrices[domain] = await self.create_domain_compatibility_matrix(domain)
        
        return matrices
    
    async def detect_lossy_conversions(
        self,
        domain: SemanticDomain,
        version_pairs: Optional[List[Tuple[str, str]]] = None
    ) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """
        Detect lossy conversions for a domain across multiple version pairs.
        
        Args:
            domain: The semantic domain to analyze
            version_pairs: Optional list of version pairs to check
            
        Returns:
            Dictionary mapping version pairs to their loss analysis
            
        Validates: Requirements 8.5
        """
        if version_pairs is None:
            # Generate all possible pairs
            versions = list(self._version_cache.keys())
            version_pairs = [
                (from_v, to_v) for from_v in versions for to_v in versions
                if from_v != to_v
            ]
        
        lossy_conversions = {}
        
        for from_version, to_version in version_pairs:
            is_lossy, loss_details = await self._detect_lossy_conversion(
                domain, from_version, to_version
            )
            
            if is_lossy:
                lossy_conversions[(from_version, to_version)] = {
                    'is_lossy': True,
                    'loss_details': loss_details,
                    'loss_severity': self._calculate_loss_severity(loss_details),
                    'recommended_action': self._get_loss_recommendation(loss_details)
                }
        
        return lossy_conversions
    
    async def generate_compatibility_report(
        self,
        domain: SemanticDomain,
        include_matrices: bool = True,
        include_lossy_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compatibility report for a domain.
        
        Args:
            domain: The semantic domain to report on
            include_matrices: Whether to include compatibility matrices
            include_lossy_analysis: Whether to include lossy conversion analysis
            
        Returns:
            Comprehensive compatibility report
            
        Validates: Requirements 8.5
        """
        report = {
            'domain': domain.value,
            'report_timestamp': self._get_current_timestamp(),
            'versions_analyzed': list(self._version_cache.keys()),
            'total_version_pairs': len(self._version_cache) * (len(self._version_cache) - 1)
        }
        
        # Include compatibility matrix if requested
        if include_matrices:
            if domain in self._compatibility_matrices:
                matrix = self._compatibility_matrices[domain]
            else:
                matrix = await self.create_domain_compatibility_matrix(domain)
            
            report['compatibility_matrix'] = self._serialize_compatibility_matrix(matrix)
            report['compatibility_summary'] = self._summarize_compatibility_matrix(matrix)
        
        # Include lossy conversion analysis if requested
        if include_lossy_analysis:
            lossy_conversions = await self.detect_lossy_conversions(domain)
            report['lossy_conversions'] = {
                f"{pair[0]}_to_{pair[1]}": details
                for pair, details in lossy_conversions.items()
            }
            report['lossy_conversion_summary'] = {
                'total_lossy_conversions': len(lossy_conversions),
                'most_problematic_source': self._find_most_problematic_source(lossy_conversions),
                'most_problematic_target': self._find_most_problematic_target(lossy_conversions)
            }
        
        # Add domain-specific insights
        report['domain_insights'] = await self._generate_domain_insights(domain)
        
        return report
    
    async def _perform_detailed_compatibility_analysis(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str,
        base_compatibility: DomainCompatibilityLevel
    ) -> Dict[str, Any]:
        """Perform detailed field-level compatibility analysis"""
        from_fields = self._get_domain_fields(domain, from_version)
        to_fields = self._get_domain_fields(domain, to_version)
        
        field_compatibility = {}
        loss_details = []
        warnings = []
        notes = []
        
        # Analyze each field in source version
        for from_field in from_fields:
            field_name = from_field.name
            
            # Find corresponding field in target version
            to_field = self._find_corresponding_field(from_field, to_fields)
            
            if to_field is None:
                # Field is removed in target version
                field_compatibility[field_name] = {
                    'status': 'removed',
                    'compatibility': DomainCompatibilityLevel.INCOMPATIBLE.value,
                    'impact': 'Field not available in target version'
                }
                loss_details.append({
                    'type': ConversionLossType.FIELD_REMOVED.value,
                    'field': field_name,
                    'description': f"Field '{field_name}' is not available in {to_version}",
                    'severity': 'high'
                })
                warnings.append(f"Field '{field_name}' will be lost in conversion to {to_version}")
            else:
                # Analyze field compatibility
                field_compat = self._analyze_field_compatibility(from_field, to_field)
                field_compatibility[field_name] = field_compat
                
                if field_compat['compatibility'] in [
                    DomainCompatibilityLevel.LOSSY.value,
                    DomainCompatibilityLevel.INCOMPATIBLE.value
                ]:
                    loss_details.extend(field_compat.get('loss_details', []))
                    warnings.extend(field_compat.get('warnings', []))
        
        # Check for new fields in target version
        for to_field in to_fields:
            if not any(self._fields_correspond(f, to_field) for f in from_fields):
                field_compatibility[to_field.name] = {
                    'status': 'added',
                    'compatibility': DomainCompatibilityLevel.PARTIAL.value,
                    'impact': f'New field in {to_version}, will use default value'
                }
                notes.append(f"New field '{to_field.name}' in {to_version} will use default value")
        
        return {
            'field_compatibility': field_compatibility,
            'loss_details': loss_details,
            'conversion_warnings': warnings,
            'conversion_notes': notes
        }
    
    async def _detect_lossy_conversion(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Detect if conversion between versions is lossy"""
        from_fields = self._get_domain_fields(domain, from_version)
        to_fields = self._get_domain_fields(domain, to_version)
        
        loss_details = []
        
        # Check for removed fields
        for from_field in from_fields:
            to_field = self._find_corresponding_field(from_field, to_fields)
            if to_field is None:
                loss_details.append({
                    'type': ConversionLossType.FIELD_REMOVED.value,
                    'field': from_field.name,
                    'description': f"Field '{from_field.name}' removed in {to_version}",
                    'severity': 'high'
                })
        
        # Check for precision loss
        for from_field in from_fields:
            to_field = self._find_corresponding_field(from_field, to_fields)
            if to_field and self._has_precision_loss(from_field, to_field):
                loss_details.append({
                    'type': ConversionLossType.PRECISION_LOST.value,
                    'field': from_field.name,
                    'description': f"Precision reduced in field '{from_field.name}'",
                    'from_length': from_field.length,
                    'to_length': to_field.length,
                    'severity': 'medium'
                })
        
        # Check for format changes that cause loss
        for from_field in from_fields:
            to_field = self._find_corresponding_field(from_field, to_fields)
            if to_field and self._has_lossy_format_change(from_field, to_field):
                loss_details.append({
                    'type': ConversionLossType.FORMAT_CHANGED.value,
                    'field': from_field.name,
                    'description': f"Lossy format change in field '{from_field.name}'",
                    'from_type': from_field.data_type,
                    'to_type': to_field.data_type,
                    'severity': 'medium'
                })
        
        # Check for semantic changes
        for from_field in from_fields:
            to_field = self._find_corresponding_field(from_field, to_fields)
            if to_field and self._has_semantic_change(from_field, to_field):
                loss_details.append({
                    'type': ConversionLossType.SEMANTIC_CHANGED.value,
                    'field': from_field.name,
                    'description': f"Semantic meaning changed in field '{from_field.name}'",
                    'from_meaning': from_field.semantic_meaning,
                    'to_meaning': to_field.semantic_meaning,
                    'severity': 'high'
                })
        
        is_lossy = len(loss_details) > 0
        return is_lossy, loss_details
    
    async def _calculate_version_pair_compatibility(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> DomainCompatibilityLevel:
        """Calculate compatibility level between two versions for a domain"""
        from_fields = self._get_domain_fields(domain, from_version)
        to_fields = self._get_domain_fields(domain, to_version)
        
        if not from_fields and not to_fields:
            return DomainCompatibilityLevel.FULL
        
        if not from_fields or not to_fields:
            return DomainCompatibilityLevel.INCOMPATIBLE
        
        total_fields = len(from_fields)
        compatible_fields = 0
        partial_fields = 0
        incompatible_fields = 0
        
        for from_field in from_fields:
            to_field = self._find_corresponding_field(from_field, to_fields)
            
            if to_field is None:
                incompatible_fields += 1
            else:
                field_compat = self._analyze_field_compatibility(from_field, to_field)
                compat_level = field_compat['compatibility']
                
                if compat_level == DomainCompatibilityLevel.FULL.value:
                    compatible_fields += 1
                elif compat_level in [DomainCompatibilityLevel.PARTIAL.value, DomainCompatibilityLevel.LOSSY.value]:
                    partial_fields += 1
                else:
                    incompatible_fields += 1
        
        # Calculate overall compatibility based on field compatibility ratios
        if incompatible_fields == 0 and partial_fields == 0:
            return DomainCompatibilityLevel.FULL
        elif incompatible_fields / total_fields > 0.5:
            return DomainCompatibilityLevel.INCOMPATIBLE
        elif (incompatible_fields + partial_fields) / total_fields > 0.3:
            return DomainCompatibilityLevel.LOSSY
        else:
            return DomainCompatibilityLevel.PARTIAL
    
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
    
    def _fields_correspond(
        self,
        field1: FieldDefinition,
        field2: FieldDefinition
    ) -> bool:
        """Check if two fields correspond to each other"""
        return (field1.name == field2.name or
                (field1.semantic_meaning and field1.semantic_meaning == field2.semantic_meaning) or
                (abs(field1.position - field2.position) <= 1 and field1.data_type == field2.data_type))
    
    def _analyze_field_compatibility(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition
    ) -> Dict[str, Any]:
        """Analyze compatibility between two corresponding fields"""
        compatibility = DomainCompatibilityLevel.FULL
        warnings = []
        loss_details = []
        
        # Check data type compatibility
        if from_field.data_type != to_field.data_type:
            compatibility = DomainCompatibilityLevel.PARTIAL
            warnings.append(f"Data type changed from {from_field.data_type} to {to_field.data_type}")
        
        # Check length compatibility
        if from_field.length > to_field.length:
            compatibility = DomainCompatibilityLevel.LOSSY
            loss_details.append({
                'type': ConversionLossType.PRECISION_LOST.value,
                'description': f"Field length reduced from {from_field.length} to {to_field.length}",
                'severity': 'medium'
            })
        
        # Check valid values compatibility
        if from_field.valid_values and to_field.valid_values:
            from_values = set(from_field.valid_values)
            to_values = set(to_field.valid_values)
            
            if not from_values.issubset(to_values):
                compatibility = DomainCompatibilityLevel.LOSSY
                missing_values = from_values - to_values
                loss_details.append({
                    'type': ConversionLossType.VALIDATION_RELAXED.value,
                    'description': f"Some valid values not supported: {list(missing_values)}",
                    'severity': 'medium'
                })
        
        # Check semantic meaning compatibility
        if (from_field.semantic_meaning and to_field.semantic_meaning and
            from_field.semantic_meaning != to_field.semantic_meaning):
            compatibility = DomainCompatibilityLevel.LOSSY
            loss_details.append({
                'type': ConversionLossType.SEMANTIC_CHANGED.value,
                'description': f"Semantic meaning changed",
                'severity': 'high'
            })
        
        return {
            'compatibility': compatibility.value,
            'warnings': warnings,
            'loss_details': loss_details,
            'field_mapping': {
                'from_field': from_field.name,
                'to_field': to_field.name,
                'transformation_required': compatibility != DomainCompatibilityLevel.FULL
            }
        }
    
    def _has_precision_loss(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition
    ) -> bool:
        """Check if conversion results in precision loss"""
        return from_field.length > to_field.length
    
    def _has_format_change(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition
    ) -> bool:
        """Check if field format changes between versions"""
        return from_field.data_type != to_field.data_type
    
    def _has_lossy_format_change(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition
    ) -> bool:
        """Check if field format change results in data loss"""
        # Only consider it lossy if we're going from a more precise to less precise type
        # or if there are incompatible type changes
        if from_field.data_type == to_field.data_type:
            return False
        
        # Define lossy type conversions
        lossy_conversions = {
            ('float', 'integer'): True,  # Precision loss
            ('string', 'integer'): True,  # Potential parsing loss
            ('integer', 'string'): False,  # Generally safe expansion
            ('float', 'string'): False,   # Generally safe expansion
        }
        
        conversion_key = (from_field.data_type, to_field.data_type)
        return lossy_conversions.get(conversion_key, False)
    
    def _has_semantic_change(
        self,
        from_field: FieldDefinition,
        to_field: FieldDefinition
    ) -> bool:
        """Check if semantic meaning changes between versions"""
        return (from_field.semantic_meaning and to_field.semantic_meaning and
                from_field.semantic_meaning != to_field.semantic_meaning)
    
    async def _generate_conversion_warnings(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str,
        compatibility: DomainCompatibilityLevel,
        is_lossy: bool
    ) -> List[str]:
        """Generate conversion warnings based on compatibility assessment"""
        warnings = []
        
        if compatibility == DomainCompatibilityLevel.INCOMPATIBLE:
            warnings.append(f"Conversion from {from_version} to {to_version} is not recommended for {domain.value} domain")
        
        if is_lossy:
            warnings.append(f"Conversion will result in information loss for {domain.value} domain")
        
        if compatibility == DomainCompatibilityLevel.LOSSY:
            warnings.append(f"Significant data transformation required for {domain.value} domain")
        
        # Add domain-specific warnings
        domain_warnings = self._get_domain_specific_warnings(domain, from_version, to_version)
        warnings.extend(domain_warnings)
        
        return warnings
    
    async def _generate_conversion_notes(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str,
        compatibility: DomainCompatibilityLevel
    ) -> List[str]:
        """Generate conversion notes based on compatibility assessment"""
        notes = []
        
        if compatibility == DomainCompatibilityLevel.FULL:
            notes.append(f"Full compatibility for {domain.value} domain - no data loss expected")
        elif compatibility == DomainCompatibilityLevel.PARTIAL:
            notes.append(f"Partial compatibility for {domain.value} domain - minor adjustments needed")
        
        # Add domain-specific notes
        domain_notes = self._get_domain_specific_notes(domain, from_version, to_version)
        notes.extend(domain_notes)
        
        return notes
    
    def _get_domain_specific_warnings(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> List[str]:
        """Get domain-specific conversion warnings"""
        warnings = []
        
        if domain == SemanticDomain.IDENTIFICATION_MARKING:
            if "1966" in from_version and "2020" in to_version:
                warnings.append("Ring number format will be significantly changed")
        elif domain == SemanticDomain.BIOMETRICS:
            if "1966" in from_version:
                warnings.append("Limited biometric data available in 1966 format")
        elif domain == SemanticDomain.SPATIAL:
            if "1966" in from_version and "2020" in to_version:
                warnings.append("Coordinate precision may be reduced")
        
        return warnings
    
    def _get_domain_specific_notes(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> List[str]:
        """Get domain-specific conversion notes"""
        notes = []
        
        if domain == SemanticDomain.TEMPORAL:
            if "1966" in from_version:
                notes.append("Time information not available in 1966, will use default values")
        elif domain == SemanticDomain.METHODOLOGY:
            if "2020" in to_version:
                notes.append("Enhanced methodology tracking available in 2020 format")
        
        return notes
    
    def _serialize_compatibility_matrix(
        self,
        matrix: DomainCompatibilityMatrix
    ) -> Dict[str, Any]:
        """Serialize compatibility matrix for reporting"""
        serialized = {
            'domain': matrix.domain.value,
            'compatibility_pairs': {}
        }
        
        for (from_v, to_v), level in matrix.compatibility_map.items():
            key = f"{from_v}_to_{to_v}"
            serialized['compatibility_pairs'][key] = level.value
        
        return serialized
    
    def _summarize_compatibility_matrix(
        self,
        matrix: DomainCompatibilityMatrix
    ) -> Dict[str, Any]:
        """Create summary statistics for compatibility matrix"""
        levels = list(matrix.compatibility_map.values())
        
        if not levels:
            return {'total_pairs': 0}
        
        level_counts = {}
        for level in DomainCompatibilityLevel:
            level_counts[level.value] = sum(1 for l in levels if l == level)
        
        return {
            'total_pairs': len(levels),
            'level_distribution': level_counts,
            'most_common_level': max(level_counts.items(), key=lambda x: x[1])[0],
            'compatibility_score': self._calculate_overall_compatibility_score(levels)
        }
    
    def _calculate_overall_compatibility_score(
        self,
        levels: List[DomainCompatibilityLevel]
    ) -> float:
        """Calculate overall compatibility score (0-1) for a domain"""
        if not levels:
            return 0.0
        
        scores = {
            DomainCompatibilityLevel.FULL: 1.0,
            DomainCompatibilityLevel.PARTIAL: 0.7,
            DomainCompatibilityLevel.LOSSY: 0.4,
            DomainCompatibilityLevel.INCOMPATIBLE: 0.0
        }
        
        total_score = sum(scores[level] for level in levels)
        return total_score / len(levels)
    
    def _calculate_loss_severity(self, loss_details: List[Dict[str, Any]]) -> str:
        """Calculate overall severity of conversion losses"""
        if not loss_details:
            return 'none'
        
        high_severity = sum(1 for detail in loss_details if detail.get('severity') == 'high')
        medium_severity = sum(1 for detail in loss_details if detail.get('severity') == 'medium')
        
        if high_severity > 0:
            return 'high'
        elif medium_severity > 2:
            return 'high'
        elif medium_severity > 0:
            return 'medium'
        else:
            return 'low'
    
    def _get_loss_recommendation(self, loss_details: List[Dict[str, Any]]) -> str:
        """Get recommendation based on loss analysis"""
        severity = self._calculate_loss_severity(loss_details)
        
        if severity == 'high':
            return 'conversion_not_recommended'
        elif severity == 'medium':
            return 'conversion_with_caution'
        else:
            return 'conversion_acceptable'
    
    def _find_most_problematic_source(
        self,
        lossy_conversions: Dict[Tuple[str, str], Dict[str, Any]]
    ) -> Optional[str]:
        """Find the source version that causes most lossy conversions"""
        source_counts = {}
        
        for (from_v, to_v), details in lossy_conversions.items():
            source_counts[from_v] = source_counts.get(from_v, 0) + 1
        
        if source_counts:
            return max(source_counts.items(), key=lambda x: x[1])[0]
        return None
    
    def _find_most_problematic_target(
        self,
        lossy_conversions: Dict[Tuple[str, str], Dict[str, Any]]
    ) -> Optional[str]:
        """Find the target version that receives most lossy conversions"""
        target_counts = {}
        
        for (from_v, to_v), details in lossy_conversions.items():
            target_counts[to_v] = target_counts.get(to_v, 0) + 1
        
        if target_counts:
            return max(target_counts.items(), key=lambda x: x[1])[0]
        return None
    
    async def _generate_domain_insights(self, domain: SemanticDomain) -> Dict[str, Any]:
        """Generate insights specific to the domain"""
        insights = {
            'domain_characteristics': self._get_domain_characteristics(domain),
            'evolution_pattern': self._analyze_domain_evolution_pattern(domain),
            'conversion_recommendations': self._get_domain_conversion_recommendations(domain)
        }
        
        return insights
    
    def _get_domain_characteristics(self, domain: SemanticDomain) -> Dict[str, Any]:
        """Get characteristics specific to the domain"""
        characteristics = {
            SemanticDomain.IDENTIFICATION_MARKING: {
                'stability': 'low',
                'complexity': 'high',
                'critical_for_conversion': True,
                'description': 'Ring identification systems vary significantly across versions'
            },
            SemanticDomain.SPECIES: {
                'stability': 'high',
                'complexity': 'medium',
                'critical_for_conversion': True,
                'description': 'Species codes are generally stable with minor format changes'
            },
            SemanticDomain.DEMOGRAPHICS: {
                'stability': 'medium',
                'complexity': 'medium',
                'critical_for_conversion': True,
                'description': 'Age and sex coding systems have evolved moderately'
            },
            SemanticDomain.TEMPORAL: {
                'stability': 'medium',
                'complexity': 'low',
                'critical_for_conversion': True,
                'description': 'Date/time formats have standardized over time'
            },
            SemanticDomain.SPATIAL: {
                'stability': 'low',
                'complexity': 'high',
                'critical_for_conversion': True,
                'description': 'Coordinate systems and precision have changed significantly'
            },
            SemanticDomain.BIOMETRICS: {
                'stability': 'medium',
                'complexity': 'medium',
                'critical_for_conversion': False,
                'description': 'Measurement systems have expanded and standardized'
            },
            SemanticDomain.METHODOLOGY: {
                'stability': 'low',
                'complexity': 'medium',
                'critical_for_conversion': False,
                'description': 'Capture and handling methods have diversified'
            }
        }
        
        return characteristics.get(domain, {
            'stability': 'unknown',
            'complexity': 'unknown',
            'critical_for_conversion': False,
            'description': 'Domain characteristics not defined'
        })
    
    def _analyze_domain_evolution_pattern(self, domain: SemanticDomain) -> str:
        """Analyze the evolution pattern of a domain"""
        if domain not in self._domain_evolutions:
            return 'unknown'
        
        evolution = self._domain_evolutions[domain]
        entries = evolution.evolution_entries
        
        if len(entries) < 2:
            return 'stable'
        
        # Analyze change frequency
        total_changes = sum(len(entry.changes) for entry in entries)
        avg_changes = total_changes / len(entries)
        
        if avg_changes > 5:
            return 'rapidly_evolving'
        elif avg_changes > 2:
            return 'moderately_evolving'
        else:
            return 'slowly_evolving'
    
    def _get_domain_conversion_recommendations(self, domain: SemanticDomain) -> List[str]:
        """Get conversion recommendations specific to the domain"""
        recommendations = {
            SemanticDomain.IDENTIFICATION_MARKING: [
                "Verify ring number format compatibility before conversion",
                "Consider manual review for critical identification data",
                "Use scheme mapping tables for accurate conversion"
            ],
            SemanticDomain.SPECIES: [
                "Species code conversions are generally reliable",
                "Verify taxonomic updates between versions",
                "Check for deprecated species codes"
            ],
            SemanticDomain.SPATIAL: [
                "Coordinate precision may be lost in older formats",
                "Consider coordinate system transformations",
                "Validate geographic accuracy after conversion"
            ],
            SemanticDomain.BIOMETRICS: [
                "Measurement units may differ between versions",
                "Some measurements may not be available in older formats",
                "Use appropriate default values for missing measurements"
            ]
        }
        
        return recommendations.get(domain, [
            "Review conversion results carefully",
            "Test with sample data before bulk conversion",
            "Document any data transformations applied"
        ])
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for reporting"""
        from datetime import datetime
        return datetime.now().isoformat()