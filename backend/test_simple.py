#!/usr/bin/env python3
"""
Simple test for EURING system
"""
import sys
import os
sys.path.append('.')

try:
    from app.services.conversion_service import EuringConversionService
    print("✓ Conversion service imported successfully")
    
    # Test conversion
    service = EuringConversionService()
    euring_1966 = "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750"
    
    print(f"Testing conversion: {euring_1966}")
    result = service.convert_semantic(euring_1966, '1966', '2020')
    
    if result['success']:
        print(f"✓ Conversion successful!")
        print(f"Result: {result['converted_string']}")
    else:
        print(f"✗ Conversion failed: {result.get('error')}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()