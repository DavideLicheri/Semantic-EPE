"""
Core service interfaces for EURING Code Recognition System
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..models.euring_models import (
    RecognitionResult, BatchRecognitionResult, EuringVersionModel,
    ConversionResult, BatchConversionResult, ValidationResult, 
    QuotaCheckResult, UserQuota, CostCalculation, PaymentResult, 
    BillingHistory, ConversionRequest, SemanticDomain, DomainEvolution,
    DomainCompatibilityMatrix, DomainCompatibilityLevel
)


class RecognitionEngine(ABC):
    """Interface for EURING string recognition engine"""
    
    @abstractmethod
    async def recognize_version(self, euring_string: str) -> RecognitionResult:
        """Recognize the EURING version of a single string"""
        pass
    
    @abstractmethod
    async def recognize_batch(
        self, 
        strings: List[str], 
        same_version: Optional[bool] = None
    ) -> BatchRecognitionResult:
        """Recognize versions for a batch of strings"""
        pass
    
    @abstractmethod
    def get_confidence_level(self, result: RecognitionResult) -> float:
        """Get confidence level for a recognition result"""
        pass


class SKOSManager(ABC):
    """Interface for SKOS model management"""
    
    @abstractmethod
    async def load_version_model(self) -> EuringVersionModel:
        """Load the complete EURING version model"""
        pass
    
    @abstractmethod
    async def get_version_characteristics(self, version: str) -> 'VersionCharacteristics':
        """Get characteristics for a specific version"""
        pass
    
    @abstractmethod
    async def get_conversion_rules(
        self, 
        from_version: str, 
        to_version: str
    ) -> 'ConversionRules':
        """Get conversion rules between two versions"""
        pass
    
    @abstractmethod
    async def validate_version_compatibility(
        self, 
        from_version: str, 
        to_version: str
    ) -> bool:
        """Check if conversion between versions is possible"""
        pass
    
    @abstractmethod
    async def get_domain_evolution(self, domain: SemanticDomain) -> DomainEvolution:
        """Get evolution data for a specific domain"""
        pass
    
    @abstractmethod
    async def analyze_domain_compatibility(
        self,
        domain: SemanticDomain,
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """Analyze compatibility between versions for a specific domain"""
        pass
    
    @abstractmethod
    async def get_semantic_domains(self) -> List[SemanticDomain]:
        """Get list of available semantic domains"""
        pass
    
    @abstractmethod
    async def get_domain_specific_version_characteristics(
        self, 
        version: str, 
        domain: SemanticDomain
    ) -> Dict[str, Any]:
        """Get version characteristics specific to a semantic domain"""
        pass
    
    @abstractmethod
    async def get_all_domain_characteristics(self, version: str) -> Dict[SemanticDomain, Dict[str, Any]]:
        """Get characteristics for all domains in a specific version"""
        pass
    
    @abstractmethod
    async def get_domain_field_mappings(
        self, 
        domain: SemanticDomain, 
        from_version: str, 
        to_version: str
    ) -> List[Dict[str, Any]]:
        """Get field mappings for a specific domain between two versions"""
        pass
    
    @abstractmethod
    async def get_domain_evolution_summary(self, domain: SemanticDomain) -> Dict[str, Any]:
        """Get a summary of domain evolution across all versions"""
        pass
    
    @abstractmethod
    async def compare_domain_between_versions(
        self, 
        domain: SemanticDomain, 
        version1: str, 
        version2: str
    ) -> Dict[str, Any]:
        """Compare a specific domain between two versions"""
        pass


class ConversionService(ABC):
    """Interface for EURING string conversion service"""
    
    @abstractmethod
    async def convert_string(
        self, 
        input_string: str, 
        from_version: str, 
        to_version: str
    ) -> ConversionResult:
        """Convert a single EURING string between versions"""
        pass
    
    @abstractmethod
    async def convert_batch(
        self, 
        inputs: List[ConversionRequest]
    ) -> BatchConversionResult:
        """Convert multiple EURING strings"""
        pass
    
    @abstractmethod
    async def validate_conversion(self, result: ConversionResult) -> ValidationResult:
        """Validate a conversion result"""
        pass
    
    @abstractmethod
    async def check_conversion_quota(
        self, 
        user_id: str, 
        requested_count: int
    ) -> QuotaCheckResult:
        """Check if user has quota for requested conversions"""
        pass


class BillingService(ABC):
    """Interface for billing and quota management"""
    
    @abstractmethod
    async def check_user_quota(self, user_id: str) -> UserQuota:
        """Check current quota status for a user"""
        pass
    
    @abstractmethod
    async def calculate_cost(
        self, 
        user_id: str, 
        conversion_count: int
    ) -> CostCalculation:
        """Calculate cost for a number of conversions"""
        pass
    
    @abstractmethod
    async def process_payment(self, user_id: str, amount: float) -> PaymentResult:
        """Process payment for conversions"""
        pass
    
    @abstractmethod
    async def update_pricing(self, new_price_per_string: float) -> None:
        """Update the price per string conversion"""
        pass
    
    @abstractmethod
    async def get_user_billing_history(self, user_id: str) -> List[BillingHistory]:
        """Get billing history for a user"""
        pass


class DomainEvolutionAnalyzer(ABC):
    """Interface for domain evolution analysis service"""
    
    @abstractmethod
    async def analyze_domain_evolution(
        self, 
        domain: SemanticDomain,
        start_version: Optional[str] = None,
        end_version: Optional[str] = None
    ) -> DomainEvolution:
        """Analyze historical changes within a specific domain"""
        pass
    
    @abstractmethod
    async def compare_domain_versions(
        self,
        domain: SemanticDomain,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """Compare two versions within a specific domain"""
        pass
    
    @abstractmethod
    async def generate_evolution_timeline(
        self,
        domain: SemanticDomain,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """Generate evolution timeline for a specific domain"""
        pass


# Additional model classes referenced in interfaces
class VersionCharacteristics(BaseModel):
    """Characteristics of a specific EURING version"""
    version_id: str
    field_count: int
    total_length: int
    unique_patterns: List[str]
    validation_rules: List[str]


class ConversionRules(BaseModel):
    """Rules for converting between EURING versions"""
    from_version: str
    to_version: str
    field_mappings: List[dict]
    transformation_functions: List[str]
    compatibility_score: float