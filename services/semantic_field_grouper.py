"""
Semantic Field Grouper Service for EURING Code Recognition System

This service implements algorithms to group fields by semantic relationships,
performs domain-specific field analysis, and creates semantic meaning extraction
and categorization.

Requirements: 8.4
"""
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
import re
from dataclasses import dataclass
from ..models.euring_models import (
    SemanticDomain, FieldDefinition, EuringVersion, 
    DomainEvolutionEntry, SemanticDomainDefinition
)


@dataclass
class SemanticRelationship:
    """Represents a semantic relationship between fields"""
    field1: str
    field2: str
    relationship_type: str
    strength: float  # 0.0 to 1.0
    semantic_basis: str
    domain: SemanticDomain


@dataclass
class FieldGroup:
    """Represents a group of semantically related fields"""
    group_id: str
    group_name: str
    fields: List[str]
    semantic_theme: str
    domain: SemanticDomain
    cohesion_score: float  # 0.0 to 1.0
    relationships: List[SemanticRelationship]


@dataclass
class SemanticMeaning:
    """Represents extracted semantic meaning of a field"""
    field_name: str
    primary_concept: str
    secondary_concepts: List[str]
    semantic_category: str
    domain: SemanticDomain
    confidence: float  # 0.0 to 1.0
    linguistic_patterns: List[str]


class SemanticFieldGrouper:
    """
    Service for grouping fields by semantic relationships and analyzing domain-specific patterns.
    
    This service provides:
    - Algorithms to group fields by semantic relationships
    - Domain-specific field analysis
    - Semantic meaning extraction and categorization
    """
    
    def __init__(self):
        self._semantic_patterns = self._initialize_semantic_patterns()
        self._domain_vocabularies = self._initialize_domain_vocabularies()
        self._relationship_rules = self._initialize_relationship_rules()
    
    def group_fields_by_semantics(
        self,
        fields: List[FieldDefinition],
        domain: Optional[SemanticDomain] = None
    ) -> List[FieldGroup]:
        """
        Group fields by semantic relationships using clustering algorithms.
        
        Args:
            fields: List of field definitions to group
            domain: Optional domain filter for domain-specific grouping
            
        Returns:
            List of field groups with semantic relationships
            
        Validates: Requirements 8.4
        """
        # Filter fields by domain if specified
        if domain:
            fields = [f for f in fields if f.semantic_domain == domain]
        
        # Extract semantic meanings for all fields
        semantic_meanings = [self.extract_semantic_meaning(field) for field in fields]
        
        # Calculate semantic relationships between all field pairs
        relationships = self._calculate_semantic_relationships(semantic_meanings)
        
        # Group fields using semantic clustering
        field_groups = self._cluster_fields_by_semantics(semantic_meanings, relationships)
        
        # Refine groups using domain-specific rules
        refined_groups = self._refine_groups_with_domain_rules(field_groups, domain)
        
        return refined_groups
    
    def analyze_domain_specific_fields(
        self,
        domain: SemanticDomain,
        versions: List[EuringVersion]
    ) -> Dict[str, Any]:
        """
        Perform domain-specific field analysis across versions.
        
        Args:
            domain: The semantic domain to analyze
            versions: List of EURING versions to analyze
            
        Returns:
            Dictionary containing domain-specific analysis results
            
        Validates: Requirements 8.4
        """
        # Collect all fields for the domain across versions
        domain_fields = []
        version_field_map = {}
        
        for version in versions:
            version_fields = [f for f in version.field_definitions if f.semantic_domain == domain]
            domain_fields.extend(version_fields)
            version_field_map[version.id] = version_fields
        
        # Analyze field evolution patterns within domain
        evolution_patterns = self._analyze_field_evolution_patterns(version_field_map)
        
        # Identify domain-specific semantic themes
        semantic_themes = self._identify_domain_semantic_themes(domain_fields, domain)
        
        # Analyze field naming conventions
        naming_conventions = self._analyze_domain_naming_conventions(domain_fields, domain)
        
        # Calculate domain cohesion metrics
        cohesion_metrics = self._calculate_domain_cohesion(domain_fields, domain)
        
        # Identify cross-field dependencies
        field_dependencies = self._identify_field_dependencies(domain_fields, domain)
        
        return {
            "domain": domain.value,
            "total_fields_analyzed": len(domain_fields),
            "versions_analyzed": len(versions),
            "evolution_patterns": evolution_patterns,
            "semantic_themes": semantic_themes,
            "naming_conventions": naming_conventions,
            "cohesion_metrics": cohesion_metrics,
            "field_dependencies": field_dependencies,
            "domain_vocabulary": self._domain_vocabularies.get(domain, {}),
            "analysis_summary": {
                "most_stable_fields": self._find_most_stable_fields(version_field_map),
                "most_volatile_fields": self._find_most_volatile_fields(version_field_map),
                "semantic_consistency_score": cohesion_metrics.get("consistency_score", 0.0)
            }
        }
    
    def extract_semantic_meaning(self, field: FieldDefinition) -> SemanticMeaning:
        """
        Extract semantic meaning from a field definition.
        
        Args:
            field: Field definition to analyze
            
        Returns:
            SemanticMeaning object with extracted concepts and categories
            
        Validates: Requirements 8.4
        """
        # Analyze field name for semantic patterns
        name_concepts = self._extract_concepts_from_name(field.name)
        
        # Analyze description for additional semantic information
        description_concepts = self._extract_concepts_from_description(field.description)
        
        # Determine primary concept
        primary_concept = self._determine_primary_concept(
            name_concepts, description_concepts, field.semantic_domain
        )
        
        # Identify secondary concepts
        secondary_concepts = self._identify_secondary_concepts(
            name_concepts, description_concepts, primary_concept
        )
        
        # Categorize semantic meaning
        semantic_category = self._categorize_semantic_meaning(
            primary_concept, secondary_concepts, field.semantic_domain
        )
        
        # Calculate confidence based on pattern matches
        confidence = self._calculate_semantic_confidence(
            field, primary_concept, secondary_concepts
        )
        
        # Identify linguistic patterns
        linguistic_patterns = self._identify_linguistic_patterns(field.name, field.description)
        
        return SemanticMeaning(
            field_name=field.name,
            primary_concept=primary_concept,
            secondary_concepts=secondary_concepts,
            semantic_category=semantic_category,
            domain=field.semantic_domain or SemanticDomain.METHODOLOGY,
            confidence=confidence,
            linguistic_patterns=linguistic_patterns
        )
    
    def categorize_semantic_fields(
        self,
        fields: List[FieldDefinition],
        domain: SemanticDomain
    ) -> Dict[str, List[str]]:
        """
        Categorize fields within a domain by semantic meaning.
        
        Args:
            fields: List of field definitions to categorize
            domain: The semantic domain for categorization
            
        Returns:
            Dictionary mapping semantic categories to field lists
            
        Validates: Requirements 8.4
        """
        # Filter fields by domain
        domain_fields = [f for f in fields if f.semantic_domain == domain]
        
        # Extract semantic meanings
        semantic_meanings = [self.extract_semantic_meaning(field) for field in domain_fields]
        
        # Group by semantic categories
        categories = defaultdict(list)
        for meaning in semantic_meanings:
            categories[meaning.semantic_category].append(meaning.field_name)
        
        # Add domain-specific subcategories
        subcategories = self._create_domain_subcategories(semantic_meanings, domain)
        categories.update(subcategories)
        
        return dict(categories)
    
    def _initialize_semantic_patterns(self) -> Dict[str, List[str]]:
        """Initialize semantic patterns for field analysis"""
        return {
            "identification": [
                r"ring", r"number", r"id", r"identifier", r"scheme", r"mark", r"tag"
            ],
            "species": [
                r"species", r"code", r"taxonomy", r"finder", r"mentioned"
            ],
            "demographics": [
                r"age", r"sex", r"gender", r"adult", r"juvenile", r"male", r"female"
            ],
            "temporal": [
                r"date", r"time", r"when", r"current", r"first", r"timestamp"
            ],
            "spatial": [
                r"lat", r"lon", r"coordinate", r"location", r"place", r"accuracy", r"region"
            ],
            "biometrics": [
                r"wing", r"weight", r"bill", r"tarsus", r"fat", r"muscle", r"moult", r"measurement"
            ],
            "methodology": [
                r"method", r"condition", r"status", r"catch", r"lure", r"manipulat", r"moved"
            ]
        }
    
    def _initialize_domain_vocabularies(self) -> Dict[SemanticDomain, Dict[str, List[str]]]:
        """Initialize domain-specific vocabularies"""
        return {
            SemanticDomain.IDENTIFICATION_MARKING: {
                "ring_types": ["metal", "plastic", "color", "flag"],
                "marking_methods": ["ring", "band", "tag", "mark", "collar"],
                "verification": ["verify", "check", "confirm", "validate"]
            },
            SemanticDomain.SPECIES: {
                "taxonomy": ["species", "genus", "family", "order"],
                "identification": ["code", "number", "id", "identifier"],
                "sources": ["finder", "scheme", "observer", "ringer"]
            },
            SemanticDomain.DEMOGRAPHICS: {
                "age_classes": ["adult", "juvenile", "pullus", "nestling", "fledgling"],
                "sex_classes": ["male", "female", "unknown", "undetermined"],
                "determination": ["concluded", "mentioned", "observed", "estimated"]
            },
            SemanticDomain.TEMPORAL: {
                "time_units": ["date", "time", "year", "month", "day", "hour"],
                "events": ["capture", "observation", "handling", "release"],
                "sequence": ["first", "current", "last", "previous"]
            },
            SemanticDomain.SPATIAL: {
                "coordinates": ["latitude", "longitude", "decimal", "encoded"],
                "accuracy": ["precision", "accuracy", "error", "uncertainty"],
                "locations": ["region", "country", "site", "place", "location"]
            },
            SemanticDomain.BIOMETRICS: {
                "measurements": ["length", "width", "height", "diameter"],
                "body_parts": ["wing", "bill", "tarsus", "tail", "head"],
                "conditions": ["fat", "muscle", "moult", "score", "index"]
            },
            SemanticDomain.METHODOLOGY: {
                "capture_methods": ["net", "trap", "hand", "cannon", "mist"],
                "conditions": ["weather", "light", "temperature", "wind"],
                "procedures": ["handling", "processing", "manipulation", "treatment"]
            }
        }
    
    def _initialize_relationship_rules(self) -> List[Dict[str, Any]]:
        """Initialize rules for identifying semantic relationships"""
        return [
            {
                "type": "coordinate_pair",
                "pattern": [r"lat", r"lon"],
                "strength": 0.9,
                "description": "Latitude and longitude form coordinate pairs"
            },
            {
                "type": "measurement_group",
                "pattern": [r"wing", r"bill", r"tarsus", r"weight"],
                "strength": 0.8,
                "description": "Biometric measurements are related"
            },
            {
                "type": "identification_chain",
                "pattern": [r"ring", r"scheme", r"verify"],
                "strength": 0.85,
                "description": "Ring identification chain"
            },
            {
                "type": "demographic_pair",
                "pattern": [r"age", r"sex"],
                "strength": 0.7,
                "description": "Age and sex are demographic characteristics"
            },
            {
                "type": "temporal_sequence",
                "pattern": [r"date", r"time"],
                "strength": 0.8,
                "description": "Date and time form temporal information"
            }
        ]
    
    def _calculate_semantic_relationships(
        self,
        semantic_meanings: List[SemanticMeaning]
    ) -> List[SemanticRelationship]:
        """Calculate semantic relationships between fields"""
        relationships = []
        
        for i, meaning1 in enumerate(semantic_meanings):
            for j, meaning2 in enumerate(semantic_meanings[i+1:], i+1):
                relationship = self._calculate_pairwise_relationship(meaning1, meaning2)
                if relationship and relationship.strength > 0.3:  # Threshold for meaningful relationships
                    relationships.append(relationship)
        
        return relationships
    
    def _calculate_pairwise_relationship(
        self,
        meaning1: SemanticMeaning,
        meaning2: SemanticMeaning
    ) -> Optional[SemanticRelationship]:
        """Calculate relationship strength between two semantic meanings"""
        # Same domain bonus
        domain_bonus = 0.3 if meaning1.domain == meaning2.domain else 0.0
        
        # Concept overlap
        concept_overlap = self._calculate_concept_overlap(meaning1, meaning2)
        
        # Pattern matching
        pattern_match = self._check_relationship_patterns(meaning1.field_name, meaning2.field_name)
        
        # Calculate overall strength
        strength = (concept_overlap + pattern_match + domain_bonus) / 3.0
        
        if strength < 0.1:
            return None
        
        # Determine relationship type
        relationship_type = self._determine_relationship_type(meaning1, meaning2, pattern_match)
        
        return SemanticRelationship(
            field1=meaning1.field_name,
            field2=meaning2.field_name,
            relationship_type=relationship_type,
            strength=min(strength, 1.0),
            semantic_basis=f"{meaning1.primary_concept}-{meaning2.primary_concept}",
            domain=meaning1.domain if meaning1.domain == meaning2.domain else SemanticDomain.METHODOLOGY
        )
    
    def _cluster_fields_by_semantics(
        self,
        semantic_meanings: List[SemanticMeaning],
        relationships: List[SemanticRelationship]
    ) -> List[FieldGroup]:
        """Cluster fields into groups based on semantic relationships"""
        # Create adjacency list for relationship graph
        field_graph = defaultdict(list)
        for rel in relationships:
            field_graph[rel.field1].append((rel.field2, rel.strength))
            field_graph[rel.field2].append((rel.field1, rel.strength))
        
        # Find connected components using DFS
        visited = set()
        groups = []
        
        for meaning in semantic_meanings:
            if meaning.field_name not in visited:
                group_fields = []
                group_relationships = []
                self._dfs_cluster(
                    meaning.field_name, field_graph, visited, 
                    group_fields, group_relationships, relationships
                )
                
                if len(group_fields) > 1:  # Only create groups with multiple fields
                    group = self._create_field_group(
                        group_fields, group_relationships, semantic_meanings
                    )
                    groups.append(group)
        
        return groups
    
    def _dfs_cluster(
        self,
        field: str,
        graph: Dict[str, List[Tuple[str, float]]],
        visited: Set[str],
        group_fields: List[str],
        group_relationships: List[SemanticRelationship],
        all_relationships: List[SemanticRelationship]
    ):
        """Depth-first search for clustering fields"""
        visited.add(field)
        group_fields.append(field)
        
        for neighbor, strength in graph[field]:
            if neighbor not in visited and strength > 0.5:  # Strong relationship threshold
                # Find the relationship object
                rel = next((r for r in all_relationships 
                           if (r.field1 == field and r.field2 == neighbor) or
                              (r.field1 == neighbor and r.field2 == field)), None)
                if rel:
                    group_relationships.append(rel)
                
                self._dfs_cluster(neighbor, graph, visited, group_fields, group_relationships, all_relationships)
    
    def _create_field_group(
        self,
        fields: List[str],
        relationships: List[SemanticRelationship],
        semantic_meanings: List[SemanticMeaning]
    ) -> FieldGroup:
        """Create a field group from clustered fields"""
        # Find semantic meanings for group fields
        group_meanings = [m for m in semantic_meanings if m.field_name in fields]
        
        # Determine dominant domain
        domain_counts = defaultdict(int)
        for meaning in group_meanings:
            domain_counts[meaning.domain] += 1
        dominant_domain = max(domain_counts.keys(), key=lambda d: domain_counts[d])
        
        # Generate group name and theme
        primary_concepts = [m.primary_concept for m in group_meanings]
        group_name = self._generate_group_name(primary_concepts, dominant_domain)
        semantic_theme = self._generate_semantic_theme(group_meanings)
        
        # Calculate cohesion score
        cohesion_score = self._calculate_group_cohesion(relationships, len(fields))
        
        return FieldGroup(
            group_id=f"{dominant_domain.value}_{hash(tuple(sorted(fields))) % 10000}",
            group_name=group_name,
            fields=fields,
            semantic_theme=semantic_theme,
            domain=dominant_domain,
            cohesion_score=cohesion_score,
            relationships=relationships
        )
    
    def _refine_groups_with_domain_rules(
        self,
        groups: List[FieldGroup],
        domain: Optional[SemanticDomain]
    ) -> List[FieldGroup]:
        """Refine field groups using domain-specific rules"""
        refined_groups = []
        
        for group in groups:
            # Apply domain-specific refinements
            if domain and group.domain == domain:
                refined_group = self._apply_domain_specific_refinements(group, domain)
                refined_groups.append(refined_group)
            else:
                refined_groups.append(group)
        
        # Merge similar groups if they exist
        merged_groups = self._merge_similar_groups(refined_groups)
        
        return merged_groups
    
    def _extract_concepts_from_name(self, name: str) -> List[str]:
        """Extract semantic concepts from field name"""
        concepts = []
        
        # Split by common separators
        parts = re.split(r'[_\-\s]+', name.lower())
        
        # Match against semantic patterns
        for domain, patterns in self._semantic_patterns.items():
            for pattern in patterns:
                if any(re.search(pattern, part) for part in parts):
                    concepts.append(domain)
                    break
        
        # Add specific concepts from parts
        concepts.extend([part for part in parts if len(part) > 2])
        
        return list(set(concepts))
    
    def _extract_concepts_from_description(self, description: str) -> List[str]:
        """Extract semantic concepts from field description"""
        concepts = []
        
        if not description:
            return concepts
        
        description_lower = description.lower()
        
        # Match against domain vocabularies
        for domain, vocab in self._domain_vocabularies.items():
            for category, terms in vocab.items():
                for term in terms:
                    if term in description_lower:
                        concepts.append(f"{domain.value}_{category}")
        
        return concepts
    
    def _determine_primary_concept(
        self,
        name_concepts: List[str],
        description_concepts: List[str],
        domain: Optional[SemanticDomain]
    ) -> str:
        """Determine the primary semantic concept"""
        all_concepts = name_concepts + description_concepts
        
        if not all_concepts:
            return "unknown"
        
        # Prefer domain-specific concepts
        if domain:
            domain_concepts = [c for c in all_concepts if domain.value in c]
            if domain_concepts:
                return domain_concepts[0]
        
        # Return most frequent concept
        concept_counts = defaultdict(int)
        for concept in all_concepts:
            concept_counts[concept] += 1
        
        return max(concept_counts.keys(), key=lambda c: concept_counts[c])
    
    def _identify_secondary_concepts(
        self,
        name_concepts: List[str],
        description_concepts: List[str],
        primary_concept: str
    ) -> List[str]:
        """Identify secondary semantic concepts"""
        all_concepts = list(set(name_concepts + description_concepts))
        return [c for c in all_concepts if c != primary_concept][:3]  # Top 3 secondary
    
    def _categorize_semantic_meaning(
        self,
        primary_concept: str,
        secondary_concepts: List[str],
        domain: Optional[SemanticDomain]
    ) -> str:
        """Categorize the semantic meaning"""
        if domain:
            # Use domain-specific categorization
            domain_vocab = self._domain_vocabularies.get(domain, {})
            for category, terms in domain_vocab.items():
                if any(term in primary_concept.lower() for term in terms):
                    return f"{domain.value}_{category}"
        
        # Fallback to general categorization
        if any(pattern in primary_concept for pattern in ["id", "number", "code"]):
            return "identifier"
        elif any(pattern in primary_concept for pattern in ["measure", "length", "score"]):
            return "measurement"
        elif any(pattern in primary_concept for pattern in ["date", "time"]):
            return "temporal"
        elif any(pattern in primary_concept for pattern in ["lat", "lon", "location"]):
            return "spatial"
        else:
            return "descriptive"
    
    def _calculate_semantic_confidence(
        self,
        field: FieldDefinition,
        primary_concept: str,
        secondary_concepts: List[str]
    ) -> float:
        """Calculate confidence in semantic meaning extraction"""
        confidence = 0.5  # Base confidence
        
        # Boost for clear semantic domain assignment
        if field.semantic_domain:
            confidence += 0.2
        
        # Boost for meaningful primary concept
        if primary_concept != "unknown":
            confidence += 0.2
        
        # Boost for secondary concepts
        confidence += min(len(secondary_concepts) * 0.1, 0.3)
        
        # Boost for semantic meaning field
        if field.semantic_meaning:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _identify_linguistic_patterns(self, name: str, description: str) -> List[str]:
        """Identify linguistic patterns in field names and descriptions"""
        patterns = []
        
        # Naming patterns
        if '_' in name:
            patterns.append("underscore_separated")
        if re.search(r'[A-Z]', name):
            patterns.append("camel_case")
        if name.endswith('_code'):
            patterns.append("code_suffix")
        if name.endswith('_info'):
            patterns.append("info_suffix")
        
        # Description patterns
        if description:
            if '(' in description and ')' in description:
                patterns.append("parenthetical_info")
            if re.search(r'\d+', description):
                patterns.append("numeric_specification")
        
        return patterns
    
    def _analyze_field_evolution_patterns(
        self,
        version_field_map: Dict[str, List[FieldDefinition]]
    ) -> Dict[str, Any]:
        """Analyze how fields evolve across versions within a domain"""
        evolution_patterns = {
            "field_lifecycle": {},
            "naming_evolution": {},
            "semantic_drift": {},
            "stability_analysis": {}
        }
        
        # Track field appearances across versions
        field_appearances = defaultdict(list)
        for version_id, fields in version_field_map.items():
            for field in fields:
                field_appearances[field.name].append(version_id)
        
        # Analyze field lifecycle
        for field_name, versions in field_appearances.items():
            evolution_patterns["field_lifecycle"][field_name] = {
                "first_appearance": min(versions),
                "last_appearance": max(versions),
                "total_versions": len(versions),
                "stability": "stable" if len(versions) > len(version_field_map) * 0.7 else "volatile"
            }
        
        return evolution_patterns
    
    def _identify_domain_semantic_themes(
        self,
        fields: List[FieldDefinition],
        domain: SemanticDomain
    ) -> List[Dict[str, Any]]:
        """Identify semantic themes within a domain"""
        themes = []
        
        # Extract all semantic meanings
        semantic_meanings = [self.extract_semantic_meaning(field) for field in fields]
        
        # Group by primary concepts
        concept_groups = defaultdict(list)
        for meaning in semantic_meanings:
            concept_groups[meaning.primary_concept].append(meaning)
        
        # Create themes from concept groups
        for concept, meanings in concept_groups.items():
            if len(meanings) > 1:  # Only themes with multiple fields
                theme = {
                    "theme_name": concept,
                    "field_count": len(meanings),
                    "fields": [m.field_name for m in meanings],
                    "semantic_categories": list(set(m.semantic_category for m in meanings)),
                    "average_confidence": sum(m.confidence for m in meanings) / len(meanings)
                }
                themes.append(theme)
        
        return sorted(themes, key=lambda t: t["field_count"], reverse=True)
    
    def _analyze_domain_naming_conventions(
        self,
        fields: List[FieldDefinition],
        domain: SemanticDomain
    ) -> Dict[str, Any]:
        """Analyze naming conventions within a domain"""
        conventions = {
            "common_prefixes": defaultdict(int),
            "common_suffixes": defaultdict(int),
            "separator_patterns": defaultdict(int),
            "length_distribution": defaultdict(int)
        }
        
        for field in fields:
            name = field.name
            
            # Analyze prefixes (first 3-5 characters)
            if len(name) > 3:
                conventions["common_prefixes"][name[:3]] += 1
            if len(name) > 5:
                conventions["common_prefixes"][name[:5]] += 1
            
            # Analyze suffixes
            if len(name) > 4:
                conventions["common_suffixes"][name[-4:]] += 1
            if len(name) > 6:
                conventions["common_suffixes"][name[-6:]] += 1
            
            # Analyze separators
            if '_' in name:
                conventions["separator_patterns"]["underscore"] += 1
            if '-' in name:
                conventions["separator_patterns"]["hyphen"] += 1
            
            # Length distribution
            length_category = f"{(len(name) // 5) * 5}-{(len(name) // 5) * 5 + 4}"
            conventions["length_distribution"][length_category] += 1
        
        # Convert to regular dicts and sort
        return {
            "common_prefixes": dict(sorted(conventions["common_prefixes"].items(), 
                                         key=lambda x: x[1], reverse=True)[:5]),
            "common_suffixes": dict(sorted(conventions["common_suffixes"].items(), 
                                         key=lambda x: x[1], reverse=True)[:5]),
            "separator_patterns": dict(conventions["separator_patterns"]),
            "length_distribution": dict(conventions["length_distribution"])
        }
    
    def _calculate_domain_cohesion(
        self,
        fields: List[FieldDefinition],
        domain: SemanticDomain
    ) -> Dict[str, float]:
        """Calculate cohesion metrics for a domain"""
        if not fields:
            return {"consistency_score": 0.0, "semantic_cohesion": 0.0}
        
        # Extract semantic meanings
        semantic_meanings = [self.extract_semantic_meaning(field) for field in fields]
        
        # Calculate semantic consistency
        primary_concepts = [m.primary_concept for m in semantic_meanings]
        concept_diversity = len(set(primary_concepts)) / len(primary_concepts) if primary_concepts else 0
        consistency_score = 1.0 - concept_diversity  # Lower diversity = higher consistency
        
        # Calculate semantic cohesion based on relationships
        relationships = self._calculate_semantic_relationships(semantic_meanings)
        if len(fields) > 1:
            max_possible_relationships = len(fields) * (len(fields) - 1) / 2
            actual_relationships = len([r for r in relationships if r.strength > 0.5])
            semantic_cohesion = actual_relationships / max_possible_relationships
        else:
            semantic_cohesion = 1.0
        
        return {
            "consistency_score": consistency_score,
            "semantic_cohesion": semantic_cohesion,
            "average_confidence": sum(m.confidence for m in semantic_meanings) / len(semantic_meanings)
        }
    
    def _identify_field_dependencies(
        self,
        fields: List[FieldDefinition],
        domain: SemanticDomain
    ) -> List[Dict[str, Any]]:
        """Identify dependencies between fields in a domain"""
        dependencies = []
        
        # Check for coordinate pairs
        lat_fields = [f for f in fields if 'lat' in f.name.lower()]
        lon_fields = [f for f in fields if 'lon' in f.name.lower()]
        
        for lat_field in lat_fields:
            for lon_field in lon_fields:
                dependencies.append({
                    "type": "coordinate_pair",
                    "fields": [lat_field.name, lon_field.name],
                    "dependency_strength": 0.9,
                    "description": "Latitude and longitude form coordinate pairs"
                })
        
        # Check for measurement groups
        measurement_fields = [f for f in fields if any(term in f.name.lower() 
                                                     for term in ['length', 'weight', 'score'])]
        if len(measurement_fields) > 1:
            dependencies.append({
                "type": "measurement_group",
                "fields": [f.name for f in measurement_fields],
                "dependency_strength": 0.7,
                "description": "Related biometric measurements"
            })
        
        return dependencies
    
    def _find_most_stable_fields(
        self,
        version_field_map: Dict[str, List[FieldDefinition]]
    ) -> List[str]:
        """Find fields that appear in most versions (most stable)"""
        field_counts = defaultdict(int)
        for fields in version_field_map.values():
            for field in fields:
                field_counts[field.name] += 1
        
        total_versions = len(version_field_map)
        stable_fields = [field for field, count in field_counts.items() 
                        if count >= total_versions * 0.8]  # Appear in 80%+ of versions
        
        return sorted(stable_fields)
    
    def _find_most_volatile_fields(
        self,
        version_field_map: Dict[str, List[FieldDefinition]]
    ) -> List[str]:
        """Find fields that appear in few versions (most volatile)"""
        field_counts = defaultdict(int)
        for fields in version_field_map.values():
            for field in fields:
                field_counts[field.name] += 1
        
        volatile_fields = [field for field, count in field_counts.items() 
                          if count == 1]  # Appear in only one version
        
        return sorted(volatile_fields)
    
    def _calculate_concept_overlap(
        self,
        meaning1: SemanticMeaning,
        meaning2: SemanticMeaning
    ) -> float:
        """Calculate concept overlap between two semantic meanings"""
        concepts1 = set([meaning1.primary_concept] + meaning1.secondary_concepts)
        concepts2 = set([meaning2.primary_concept] + meaning2.secondary_concepts)
        
        if not concepts1 or not concepts2:
            return 0.0
        
        intersection = len(concepts1 & concepts2)
        union = len(concepts1 | concepts2)
        
        return intersection / union if union > 0 else 0.0
    
    def _check_relationship_patterns(self, field1: str, field2: str) -> float:
        """Check if field names match relationship patterns"""
        field1_lower = field1.lower()
        field2_lower = field2.lower()
        
        for rule in self._relationship_rules:
            patterns = rule["pattern"]
            if len(patterns) == 2:
                if (any(re.search(patterns[0], field1_lower) for p in [patterns[0]]) and
                    any(re.search(patterns[1], field2_lower) for p in [patterns[1]])):
                    return rule["strength"]
                if (any(re.search(patterns[1], field1_lower) for p in [patterns[1]]) and
                    any(re.search(patterns[0], field2_lower) for p in [patterns[0]])):
                    return rule["strength"]
        
        return 0.0
    
    def _determine_relationship_type(
        self,
        meaning1: SemanticMeaning,
        meaning2: SemanticMeaning,
        pattern_match: float
    ) -> str:
        """Determine the type of relationship between two meanings"""
        if pattern_match > 0.8:
            # Check specific patterns
            for rule in self._relationship_rules:
                if pattern_match >= rule["strength"] * 0.9:
                    return rule["type"]
        
        if meaning1.domain == meaning2.domain:
            return "domain_related"
        elif meaning1.semantic_category == meaning2.semantic_category:
            return "category_related"
        else:
            return "semantic_related"
    
    def _calculate_group_cohesion(self, relationships: List[SemanticRelationship], field_count: int) -> float:
        """Calculate cohesion score for a field group"""
        if field_count < 2:
            return 1.0
        
        max_possible_relationships = field_count * (field_count - 1) / 2
        actual_relationships = len(relationships)
        
        if max_possible_relationships == 0:
            return 1.0
        
        relationship_density = actual_relationships / max_possible_relationships
        average_strength = sum(r.strength for r in relationships) / len(relationships) if relationships else 0
        
        return (relationship_density + average_strength) / 2.0
    
    def _generate_group_name(self, concepts: List[str], domain: SemanticDomain) -> str:
        """Generate a descriptive name for a field group"""
        # Find most common concept
        concept_counts = defaultdict(int)
        for concept in concepts:
            concept_counts[concept] += 1
        
        if concept_counts:
            primary_concept = max(concept_counts.keys(), key=lambda c: concept_counts[c])
            return f"{domain.value}_{primary_concept}_group"
        else:
            return f"{domain.value}_group"
    
    def _generate_semantic_theme(self, meanings: List[SemanticMeaning]) -> str:
        """Generate a semantic theme description for a group"""
        categories = [m.semantic_category for m in meanings]
        primary_concepts = [m.primary_concept for m in meanings]
        
        if len(set(categories)) == 1:
            return f"Fields related to {categories[0]}"
        elif len(set(primary_concepts)) <= 2:
            return f"Fields involving {' and '.join(set(primary_concepts))}"
        else:
            return "Semantically related fields"
    
    def _apply_domain_specific_refinements(
        self,
        group: FieldGroup,
        domain: SemanticDomain
    ) -> FieldGroup:
        """Apply domain-specific refinements to a field group"""
        # This could include domain-specific splitting or merging logic
        # For now, return the group as-is
        return group
    
    def _merge_similar_groups(self, groups: List[FieldGroup]) -> List[FieldGroup]:
        """Merge groups that are very similar"""
        # Simple implementation - could be enhanced with more sophisticated merging
        return groups
    
    def _create_domain_subcategories(
        self,
        semantic_meanings: List[SemanticMeaning],
        domain: SemanticDomain
    ) -> Dict[str, List[str]]:
        """Create domain-specific subcategories"""
        subcategories = defaultdict(list)
        
        # Group by linguistic patterns
        pattern_groups = defaultdict(list)
        for meaning in semantic_meanings:
            for pattern in meaning.linguistic_patterns:
                pattern_groups[f"pattern_{pattern}"].append(meaning.field_name)
        
        # Only include patterns with multiple fields
        for pattern, fields in pattern_groups.items():
            if len(fields) > 1:
                subcategories[pattern] = fields
        
        return dict(subcategories)