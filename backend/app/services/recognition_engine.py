"""
Recognition Engine implementation for EURING Code Recognition System
"""
import re
import time
from typing import List, Optional, Dict, Any, Tuple
from ..models.euring_models import (
    RecognitionResult, BatchRecognitionResult, EuringVersion, 
    AnalysisMetadata
)
from .interfaces import RecognitionEngine, SKOSManager
from .skos_manager import SKOSManagerImpl


class PatternMatcher:
    """Core pattern matching algorithms for EURING version detection"""
    
    def __init__(self):
        self.confidence_weights = {
            'total_length': 0.3,
            'field_pattern': 0.4,
            'validation_rules': 0.2,
            'regex_match': 0.1
        }
    
    def calculate_match_score(
        self, 
        euring_string: str, 
        version: EuringVersion
    ) -> Tuple[float, Dict[str, Any]]:
        """Calculate match score between string and version"""
        start_time = time.time()
        
        # Initialize scoring components
        scores = {}
        field_matches = {}
        
        # Quick discriminant checks for high accuracy
        discriminant_score = self._check_format_discriminants(euring_string, version)
        scores['format_discriminant'] = discriminant_score
        
        # If discriminant fails badly, heavily penalize
        if discriminant_score < 0.3:
            scores['total_length'] = 0.0
            scores['field_pattern'] = 0.0
            scores['validation_rules'] = 0.0
            scores['regex_match'] = 0.0
        else:
            # 1. Total length check
            expected_length = version.format_specification.total_length
            actual_length = len(euring_string)
            length_score = 1.0 if actual_length == expected_length else max(0.0, 1.0 - abs(actual_length - expected_length) / expected_length)
            scores['total_length'] = length_score
            
            # 2. Field pattern matching
            field_score, field_details = self._match_field_patterns(euring_string, version)
            scores['field_pattern'] = field_score
            field_matches.update(field_details)
            
            # 3. Validation rules check
            validation_score = self._check_validation_rules(euring_string, version)
            scores['validation_rules'] = validation_score
            
            # 4. Regex pattern match
            regex_score = self._check_regex_pattern(euring_string, version)
            scores['regex_match'] = regex_score
        
        # Updated weights to prioritize discriminants
        weights = {
            'format_discriminant': 0.4,
            'total_length': 0.2,
            'field_pattern': 0.2,
            'validation_rules': 0.1,
            'regex_match': 0.1
        }
        
        # Calculate weighted total score
        total_score = sum(
            scores[component] * weights[component]
            for component in scores
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        analysis_details = {
            'processing_time_ms': processing_time,
            'algorithm_version': '2.0',
            'confidence_factors': scores,
            'field_matches': field_matches
        }
        
        return total_score, analysis_details
    
    def _check_format_discriminants(self, euring_string: str, version: EuringVersion) -> float:
        """Check format-specific discriminants for high accuracy recognition"""
        version_id = version.id
        
        # 2020: Must contain pipe separators
        if version_id == "euring_2020":
            if "|" in euring_string:
                return 1.0
            else:
                return 0.0
        
        # 1966: Must contain multiple spaces (space-separated format), no pipes, no "--"
        elif version_id == "euring_1966":
            space_count = euring_string.count(" ")
            if (space_count >= 5 and 
                "|" not in euring_string and
                "--" not in euring_string):
                return 1.0
            else:
                return 0.0
        
        # 1979: Fixed length ~78, no pipes, starts with digits, contains "--", minimal spaces
        elif version_id == "euring_1979":
            space_count = euring_string.count(" ")
            if (75 <= len(euring_string) <= 82 and 
                "|" not in euring_string and
                euring_string[:5].isdigit() and
                "--" in euring_string and
                space_count <= 1):  # Allow max 1 space
                return 1.0
            else:
                return 0.0
        
        # 2000: Fixed length ~96, no spaces, no pipes, starts with letters
        elif version_id == "euring_2000":
            if (90 <= len(euring_string) <= 100 and 
                " " not in euring_string and 
                "|" not in euring_string and
                euring_string[0].isalpha()):
                return 1.0
            else:
                return 0.0
        
        # Default fallback
        return 0.5
    
    def _match_field_patterns(
        self, 
        euring_string: str, 
        version: EuringVersion
    ) -> Tuple[float, Dict[str, bool]]:
        """Match individual field patterns"""
        field_matches = {}
        total_fields = len(version.field_definitions)
        matched_fields = 0
        
        current_position = 0
        
        for field_def in version.field_definitions:
            field_name = field_def.name
            field_length = field_def.length
            
            # Extract field value from string
            if current_position + field_length <= len(euring_string):
                field_value = euring_string[current_position:current_position + field_length]
                
                # Check if field matches expected pattern
                field_match = self._validate_field_value(field_value, field_def)
                field_matches[field_name] = field_match
                
                if field_match:
                    matched_fields += 1
                    
                current_position += field_length
            else:
                field_matches[field_name] = False
        
        field_score = matched_fields / total_fields if total_fields > 0 else 0.0
        return field_score, field_matches
    
    def _validate_field_value(self, value: str, field_def) -> bool:
        """Validate a field value against its definition"""
        # Check length
        if len(value) != field_def.length:
            return False
        
        # Check valid values if specified
        if field_def.valid_values:
            return value in field_def.valid_values
        
        # Check data type constraints
        if field_def.data_type == "string":
            # For string fields, check if it contains valid characters
            if field_def.name in ["ring_number", "location_code"]:
                # Alphanumeric characters allowed
                return value.replace(' ', '').isalnum()
            elif field_def.name in ["species_code", "date_code"]:
                # Numeric only
                return value.isdigit()
        
        return True
    
    def _check_validation_rules(self, euring_string: str, version: EuringVersion) -> float:
        """Check validation rules against the string"""
        if not version.validation_rules:
            return 1.0
        
        passed_rules = 0
        total_rules = len(version.validation_rules)
        
        # Extract field values for validation
        field_values = self._extract_field_values(euring_string, version)
        
        for rule in version.validation_rules:
            field_name = rule.field_name
            if field_name in field_values:
                value = field_values[field_name]
                try:
                    # Evaluate the rule expression
                    if self._evaluate_rule(value, rule.rule_expression):
                        passed_rules += 1
                except:
                    # If rule evaluation fails, consider it as not passed
                    pass
        
        return passed_rules / total_rules if total_rules > 0 else 1.0
    
    def _extract_field_values(self, euring_string: str, version: EuringVersion) -> Dict[str, str]:
        """Extract field values from EURING string based on version definition"""
        field_values = {}
        current_position = 0
        
        for field_def in version.field_definitions:
            field_length = field_def.length
            if current_position + field_length <= len(euring_string):
                field_value = euring_string[current_position:current_position + field_length]
                field_values[field_def.name] = field_value
                current_position += field_length
            else:
                break
        
        return field_values
    
    def _evaluate_rule(self, value: str, rule_expression: str) -> bool:
        """Safely evaluate a validation rule expression"""
        # Simple rule evaluation - can be extended for more complex rules
        try:
            # Replace 'value' in expression with actual value
            safe_expression = rule_expression.replace('value', repr(value))
            # Only allow safe built-in functions
            allowed_names = {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'True': True,
                'False': False,
                'None': None
            }
            return eval(safe_expression, {"__builtins__": {}}, allowed_names)
        except:
            return False
    
    def _check_regex_pattern(self, euring_string: str, version: EuringVersion) -> float:
        """Check if string matches the version's regex pattern"""
        if not version.format_specification.validation_pattern:
            return 1.0
        
        try:
            pattern = version.format_specification.validation_pattern
            match = re.match(pattern, euring_string)
            return 1.0 if match else 0.0
        except:
            return 0.0


class ContextAnalyzer:
    """Analyzes context for disambiguation"""
    
    def __init__(self):
        self.historical_weights = {
            1963: 0.1,  # Older versions less likely
            1979: 0.3,
            2000: 0.8,
            2024: 1.0   # Recent versions more likely
        }
    
    def analyze_temporal_context(self, candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]]) -> Dict[str, float]:
        """Analyze temporal context to prefer more recent versions"""
        context_scores = {}
        
        for version, score, _ in candidates:
            # Apply temporal weighting
            temporal_weight = self.historical_weights.get(version.year, 0.5)
            context_scores[version.id] = temporal_weight
        
        return context_scores
    
    def analyze_field_consistency(
        self, 
        euring_string: str, 
        candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]]
    ) -> Dict[str, float]:
        """Analyze field consistency for disambiguation"""
        consistency_scores = {}
        
        for version, score, analysis in candidates:
            field_matches = analysis.get('field_matches', {})
            
            # Calculate consistency based on field match patterns
            total_fields = len(field_matches)
            matched_fields = sum(1 for match in field_matches.values() if match)
            
            consistency_score = matched_fields / total_fields if total_fields > 0 else 0.0
            consistency_scores[version.id] = consistency_score
        
        return consistency_scores
    
    def analyze_format_likelihood(
        self, 
        euring_string: str, 
        candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]]
    ) -> Dict[str, float]:
        """Analyze format likelihood based on string characteristics"""
        likelihood_scores = {}
        
        string_length = len(euring_string)
        
        for version, score, _ in candidates:
            expected_length = version.format_specification.total_length
            
            # Perfect length match gets highest score
            if string_length == expected_length:
                likelihood_scores[version.id] = 1.0
            else:
                # Penalize length mismatches
                length_diff = abs(string_length - expected_length)
                likelihood_scores[version.id] = max(0.0, 1.0 - (length_diff / expected_length))
        
        return likelihood_scores


class UncertaintyHandler:
    """Handles uncertainty in recognition results"""
    
    def __init__(self):
        self.uncertainty_threshold = 0.7  # Below this, consider uncertain
        self.max_alternatives = 5
    
    def assess_uncertainty(self, candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]]) -> Dict[str, Any]:
        """Assess the level of uncertainty in recognition"""
        if not candidates:
            return {'level': 'high', 'reason': 'no_candidates'}
        
        sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        best_score = sorted_candidates[0][1]
        
        if best_score < self.uncertainty_threshold:
            if len(sorted_candidates) > 1:
                second_score = sorted_candidates[1][1]
                score_gap = best_score - second_score
                
                if score_gap < 0.1:
                    return {
                        'level': 'high', 
                        'reason': 'ambiguous_candidates',
                        'score_gap': score_gap
                    }
                else:
                    return {
                        'level': 'medium', 
                        'reason': 'low_confidence',
                        'best_score': best_score
                    }
            else:
                return {
                    'level': 'medium', 
                    'reason': 'single_low_confidence',
                    'best_score': best_score
                }
        
        return {'level': 'low', 'reason': 'confident_match', 'best_score': best_score}
    
    def generate_probability_scores(
        self, 
        candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]]
    ) -> List[Tuple[EuringVersion, float]]:
        """Generate normalized probability scores for multiple options"""
        if not candidates:
            return []
        
        # Sort by score
        sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        
        # Take top candidates up to max_alternatives
        top_candidates = sorted_candidates[:self.max_alternatives]
        
        # Normalize scores to probabilities
        total_score = sum(score for _, score, _ in top_candidates)
        
        if total_score == 0:
            # Equal probability if all scores are zero
            equal_prob = 1.0 / len(top_candidates)
            return [(version, equal_prob) for version, _, _ in top_candidates]
        
        # Calculate normalized probabilities
        probabilities = []
        for version, score, _ in top_candidates:
            probability = score / total_score
            probabilities.append((version, probability))
        
        return probabilities


class AmbiguityResolver:
    """Enhanced ambiguity resolution and uncertainty handling"""
    
    def __init__(self):
        self.min_confidence_threshold = 0.6
        self.ambiguity_threshold = 0.1  # If top scores are within this range, it's ambiguous
        self.context_analyzer = ContextAnalyzer()
        self.uncertainty_handler = UncertaintyHandler()
    
    def resolve_ambiguity(
        self, 
        candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]],
        euring_string: str = ""
    ) -> Tuple[EuringVersion, float, List[EuringVersion], Dict[str, Any]]:
        """Resolve ambiguity between multiple candidate versions using context"""
        if not candidates:
            raise ValueError("No candidates provided for ambiguity resolution")
        
        # Sort candidates by score (descending)
        sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        
        # Assess uncertainty
        uncertainty_info = self.uncertainty_handler.assess_uncertainty(candidates)
        
        best_version, best_score, best_analysis = sorted_candidates[0]
        
        # Check for ambiguity
        alternative_versions = []
        if len(sorted_candidates) > 1:
            second_best_score = sorted_candidates[1][1]
            
            # If scores are very close or uncertainty is high, collect alternatives
            if (best_score - second_best_score <= self.ambiguity_threshold or 
                uncertainty_info['level'] in ['high', 'medium']):
                
                for version, score, _ in sorted_candidates[1:]:
                    if best_score - score <= self.ambiguity_threshold * 2:  # Wider threshold for alternatives
                        alternative_versions.append(version)
        
        # Apply context-based disambiguation if needed
        if alternative_versions or uncertainty_info['level'] == 'high':
            best_version, best_score, best_analysis = self._apply_context_disambiguation(
                sorted_candidates, euring_string
            )
        
        # Add uncertainty information to analysis
        best_analysis['uncertainty_assessment'] = uncertainty_info
        
        return best_version, best_score, alternative_versions, best_analysis
    
    def _apply_context_disambiguation(
        self, 
        candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]],
        euring_string: str = ""
    ) -> Tuple[EuringVersion, float, Dict[str, Any]]:
        """Apply enhanced context-based disambiguation algorithms"""
        
        # Get context scores
        temporal_scores = self.context_analyzer.analyze_temporal_context(candidates)
        consistency_scores = self.context_analyzer.analyze_field_consistency(euring_string, candidates)
        likelihood_scores = self.context_analyzer.analyze_format_likelihood(euring_string, candidates)
        
        # Calculate weighted combined scores
        enhanced_candidates = []
        for version, original_score, analysis in candidates:
            version_id = version.id
            
            # Combine different context factors
            temporal_weight = temporal_scores.get(version_id, 0.5)
            consistency_weight = consistency_scores.get(version_id, 0.5)
            likelihood_weight = likelihood_scores.get(version_id, 0.5)
            
            # Weighted combination
            enhanced_score = (
                original_score * 0.5 +  # Original pattern matching
                temporal_weight * 0.2 +  # Temporal context
                consistency_weight * 0.2 +  # Field consistency
                likelihood_weight * 0.1   # Format likelihood
            )
            
            # Add context information to analysis
            analysis['context_factors'] = {
                'temporal_score': temporal_weight,
                'consistency_score': consistency_weight,
                'likelihood_score': likelihood_weight,
                'enhanced_score': enhanced_score
            }
            
            enhanced_candidates.append((version, enhanced_score, analysis))
        
        # Return best enhanced candidate
        best_enhanced = max(enhanced_candidates, key=lambda x: x[1])
        return best_enhanced[0], best_enhanced[1], best_enhanced[2]
    
    def generate_uncertainty_options(
        self, 
        candidates: List[Tuple[EuringVersion, float, Dict[str, Any]]]
    ) -> List[Tuple[EuringVersion, float]]:
        """Generate multiple options with probability scores for uncertain cases"""
        return self.uncertainty_handler.generate_probability_scores(candidates)


class BatchProcessor:
    """Optimized batch processing for EURING string recognition"""
    
    def __init__(self, pattern_matcher: PatternMatcher, ambiguity_resolver: AmbiguityResolver):
        self.pattern_matcher = pattern_matcher
        self.ambiguity_resolver = ambiguity_resolver
        self.batch_size_threshold = 10  # Threshold for applying optimizations
    
    async def process_same_version_batch(
        self, 
        strings: List[str], 
        versions: List[EuringVersion]
    ) -> List[RecognitionResult]:
        """Optimized processing for same-version batches"""
        if not strings:
            return []
        
        # Use first string to determine the version
        first_string = strings[0]
        candidates = []
        
        for version in versions:
            score, analysis = self.pattern_matcher.calculate_match_score(
                first_string, version
            )
            candidates.append((version, score, analysis))
        
        # Get the best version for the batch
        best_version, _, _, _ = self.ambiguity_resolver.resolve_ambiguity(candidates)
        
        # Apply this version to all strings with quick validation
        results = []
        for string in strings:
            score, analysis = self.pattern_matcher.calculate_match_score(
                string, best_version
            )
            
            analysis_metadata = AnalysisMetadata(**analysis)
            
            result = RecognitionResult(
                detected_version=best_version,
                confidence=score,
                alternative_versions=None,
                analysis_details=analysis_metadata
            )
            results.append(result)
        
        return results
    
    async def process_mixed_version_batch(
        self, 
        strings: List[str], 
        versions: List[EuringVersion]
    ) -> List[RecognitionResult]:
        """Individual analysis for mixed-version batches with optimizations"""
        results = []
        
        # Group strings by length for optimization
        length_groups = {}
        for i, string in enumerate(strings):
            length = len(string)
            if length not in length_groups:
                length_groups[length] = []
            length_groups[length].append((i, string))
        
        # Process each length group separately
        for length, string_group in length_groups.items():
            # Filter versions that match this length
            compatible_versions = [
                v for v in versions 
                if v.format_specification.total_length == length
            ]
            
            if not compatible_versions:
                # If no compatible versions, use all versions but with lower confidence
                compatible_versions = versions
            
            # Process strings in this group
            for original_index, string in string_group:
                candidates = []
                for version in compatible_versions:
                    score, analysis = self.pattern_matcher.calculate_match_score(
                        string, version
                    )
                    candidates.append((version, score, analysis))
                
                # Resolve ambiguity for this string
                best_version, confidence, alternatives, analysis_details = (
                    self.ambiguity_resolver.resolve_ambiguity(candidates)
                )
                
                analysis_metadata = AnalysisMetadata(**analysis_details)
                
                result = RecognitionResult(
                    detected_version=best_version,
                    confidence=confidence,
                    alternative_versions=alternatives if alternatives else None,
                    analysis_details=analysis_metadata
                )
                
                # Insert result at correct position
                while len(results) <= original_index:
                    results.append(None)
                results[original_index] = result
        
        return results
    
    def organize_results_by_version(
        self, 
        results: List[RecognitionResult], 
        strings: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize mixed-version results by detected version"""
        organized = {}
        
        for i, result in enumerate(results):
            version_id = result.detected_version.id
            if version_id not in organized:
                organized[version_id] = []
            
            organized[version_id].append({
                'index': i,
                'string': strings[i],
                'result': result
            })
        
        return organized


class RecognitionEngineImpl(RecognitionEngine):
    """Concrete implementation of Recognition Engine"""
    
    def __init__(self, skos_manager: Optional[SKOSManager] = None):
        self.skos_manager = skos_manager or SKOSManagerImpl()
        self.pattern_matcher = PatternMatcher()
        self.ambiguity_resolver = AmbiguityResolver()
        self.batch_processor = BatchProcessor(self.pattern_matcher, self.ambiguity_resolver)
        self._versions_cache: Optional[List[EuringVersion]] = None
    
    async def recognize_version(self, euring_string: str) -> RecognitionResult:
        """Recognize the EURING version of a single string"""
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Load versions if not cached
        if self._versions_cache is None:
            version_model = await self.skos_manager.load_version_model()
            self._versions_cache = version_model.versions
        
        # Calculate match scores for all versions
        candidates = []
        for version in self._versions_cache:
            score, analysis = self.pattern_matcher.calculate_match_score(
                euring_string, version
            )
            candidates.append((version, score, analysis))
        
        # Resolve ambiguity and get best match
        best_version, confidence, alternatives, analysis_details = (
            self.ambiguity_resolver.resolve_ambiguity(candidates, euring_string)
        )
        
        # Create analysis metadata
        analysis_metadata = AnalysisMetadata(**analysis_details)
        
        return RecognitionResult(
            detected_version=best_version,
            confidence=confidence,
            alternative_versions=alternatives if alternatives else None,
            analysis_details=analysis_metadata
        )
    
    async def recognize_batch(
        self, 
        strings: List[str], 
        same_version: Optional[bool] = None
    ) -> BatchRecognitionResult:
        """Recognize versions for a batch of strings with optimization"""
        if not strings:
            raise ValueError("String list cannot be empty")
        
        # Load versions if not cached
        if self._versions_cache is None:
            version_model = await self.skos_manager.load_version_model()
            self._versions_cache = version_model.versions
        
        processing_summary = {
            'total_strings': len(strings),
            'processing_start': time.time(),
            'optimization_applied': False,
            'batch_type': 'unknown'
        }
        
        results = []
        
        if same_version is True:
            # Use optimized same-version processing
            results = await self.batch_processor.process_same_version_batch(
                strings, self._versions_cache
            )
            same_version_detected = True
            processing_summary['optimization_applied'] = True
            processing_summary['batch_type'] = 'same_version_optimized'
            
        elif same_version is False:
            # Use optimized mixed-version processing
            results = await self.batch_processor.process_mixed_version_batch(
                strings, self._versions_cache
            )
            
            # Check if all strings were actually detected as same version
            detected_versions = [r.detected_version.id for r in results]
            same_version_detected = len(set(detected_versions)) == 1
            processing_summary['optimization_applied'] = True
            processing_summary['batch_type'] = 'mixed_version_optimized'
            
            # Organize results by version for mixed batches
            if not same_version_detected:
                organized_results = self.batch_processor.organize_results_by_version(
                    results, strings
                )
                processing_summary['version_groups'] = {
                    version_id: len(group) 
                    for version_id, group in organized_results.items()
                }
        else:
            # Auto-detect batch type and apply appropriate optimization
            if len(strings) >= self.batch_processor.batch_size_threshold:
                # For larger batches, try to detect if they're same version
                sample_size = min(3, len(strings))
                sample_results = []
                
                for i in range(sample_size):
                    result = await self.recognize_version(strings[i])
                    sample_results.append(result)
                
                # Check if sample suggests same version
                sample_versions = [r.detected_version.id for r in sample_results]
                if len(set(sample_versions)) == 1:
                    # Likely same version - use optimized processing
                    results = await self.batch_processor.process_same_version_batch(
                        strings, self._versions_cache
                    )
                    same_version_detected = True
                    processing_summary['optimization_applied'] = True
                    processing_summary['batch_type'] = 'auto_detected_same_version'
                else:
                    # Mixed versions - use mixed processing
                    results = await self.batch_processor.process_mixed_version_batch(
                        strings, self._versions_cache
                    )
                    detected_versions = [r.detected_version.id for r in results]
                    same_version_detected = len(set(detected_versions)) == 1
                    processing_summary['optimization_applied'] = True
                    processing_summary['batch_type'] = 'auto_detected_mixed_version'
            else:
                # Small batch - process individually
                for string in strings:
                    result = await self.recognize_version(string)
                    results.append(result)
                
                detected_versions = [r.detected_version.id for r in results]
                same_version_detected = len(set(detected_versions)) == 1
                processing_summary['batch_type'] = 'individual_processing'
        
        processing_summary['processing_end'] = time.time()
        processing_summary['processing_time_ms'] = (
            processing_summary['processing_end'] - processing_summary['processing_start']
        ) * 1000
        
        return BatchRecognitionResult(
            results=results,
            processing_summary=processing_summary,
            same_version_detected=same_version_detected,
            total_processed=len(strings)
        )
    
    def get_confidence_level(self, result: RecognitionResult) -> float:
        """Get confidence level for a recognition result"""
        return result.confidence
    
    async def handle_uncertain_recognition(
        self, 
        euring_string: str, 
        max_alternatives: int = 5
    ) -> Dict[str, Any]:
        """Handle uncertain recognition cases by providing multiple options with probabilities"""
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Load versions if not cached
        if self._versions_cache is None:
            version_model = await self.skos_manager.load_version_model()
            self._versions_cache = version_model.versions
        
        # Calculate match scores for all versions
        candidates = []
        for version in self._versions_cache:
            score, analysis = self.pattern_matcher.calculate_match_score(
                euring_string, version
            )
            candidates.append((version, score, analysis))
        
        # Assess uncertainty
        uncertainty_info = self.ambiguity_resolver.uncertainty_handler.assess_uncertainty(candidates)
        
        # Generate probability scores for multiple options
        probability_options = self.ambiguity_resolver.generate_uncertainty_options(candidates)
        
        # Limit to requested number of alternatives
        probability_options = probability_options[:max_alternatives]
        
        return {
            'uncertainty_level': uncertainty_info['level'],
            'uncertainty_reason': uncertainty_info['reason'],
            'options': [
                {
                    'version': version.dict(),
                    'probability': probability,
                    'confidence': probability  # For compatibility
                }
                for version, probability in probability_options
            ],
            'total_options': len(probability_options),
            'recommendation': probability_options[0] if probability_options else None
        }