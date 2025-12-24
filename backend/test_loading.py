#!/usr/bin/env python3
"""
Simple test script for version loading
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.version_loader import VersionLoaderService
from app.services.skos_manager import SKOSManagerImpl

async def test_version_loading():
    """Test version loading functionality"""
    print("Testing EURING version loading...")
    
    try:
        # Test version loader (use absolute path from backend directory)
        loader = VersionLoaderService('backend/data/euring_versions')
        model = await loader.load_all_historical_versions()
        
        print(f"✓ Successfully loaded {len(model.versions)} versions")
        
        for version in model.versions:
            print(f"  - {version.name} ({version.year}): {len(version.field_definitions)} fields")
        
        # Test statistics
        stats = await loader.get_version_statistics()
        print(f"✓ Statistics: {stats['total_versions']} versions, "
              f"years {stats['year_range']['earliest']}-{stats['year_range']['latest']}")
        
        # Test SKOS manager
        skos_manager = SKOSManagerImpl('backend/data/euring_versions')
        
        # Test version characteristics
        characteristics = await skos_manager.get_version_characteristics("euring_1966")
        print(f"✓ EURING 1966 characteristics: {characteristics.field_count} fields, "
              f"length {characteristics.total_length}")
        
        # Test version compatibility
        is_compatible_1979 = await skos_manager.validate_version_compatibility("euring_1966", "euring_1979")
        print(f"✓ Compatibility 1966->1979: {is_compatible_1979}")
        
        is_compatible_2000 = await skos_manager.validate_version_compatibility("euring_1979", "euring_2000")
        print(f"✓ Compatibility 1979->2000: {is_compatible_2000}")
        
        # Test conversion rules (1963 -> 1979)
        conversion_rules = await skos_manager.get_conversion_rules("euring_1966", "euring_1979")
        print(f"✓ Conversion rules 1966->1979: {len(conversion_rules.field_mappings)} field mappings")
        
        # Test conversion rules (1979 -> 2000)
        conversion_rules_1979_2000 = await skos_manager.get_conversion_rules("euring_1979", "euring_2000")
        print(f"✓ Conversion rules 1979->2000: {len(conversion_rules_1979_2000.field_mappings)} field mappings")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_version_loading())
    sys.exit(0 if success else 1)