#!/usr/bin/env python3
"""
Check if semantic domain assignments are working correctly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.skos_manager import SKOSManagerImpl
from app.models.euring_models import SemanticDomain


async def check_domain_assignments():
    """Check if versions have semantic domain assignments"""
    print("🔍 Checking semantic domain assignments")
    
    skos_manager = SKOSManagerImpl()
    await skos_manager.load_version_model()
    
    versions = await skos_manager.get_all_versions()
    
    print(f"📊 Loaded {len(versions)} versions")
    
    for version in versions:
        print(f"\n📋 Version: {version.name} ({version.id})")
        print(f"   Total fields: {len(version.field_definitions)}")
        
        # Count fields by domain
        domain_counts = {}
        for field in version.field_definitions:
            domain = field.semantic_domain
            if domain:
                domain_counts[domain.value] = domain_counts.get(domain.value, 0) + 1
            else:
                domain_counts['unassigned'] = domain_counts.get('unassigned', 0) + 1
        
        print(f"   Domain assignments:")
        for domain, count in domain_counts.items():
            print(f"     {domain}: {count} fields")
        
        # Show first few fields with their domains
        print(f"   Sample fields:")
        for field in version.field_definitions[:3]:
            domain_name = field.semantic_domain.value if field.semantic_domain else "None"
            print(f"     - {field.name}: {domain_name}")


if __name__ == "__main__":
    asyncio.run(check_domain_assignments())