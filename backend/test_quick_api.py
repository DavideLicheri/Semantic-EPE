#!/usr/bin/env python3
"""
Quick API test for EURING system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversion_service import EuringConversionService
from app.services.recognition_engine import RecognitionEngineImpl
import asyncio


async def test_recognition():
    """Test recognition engine"""
    print("=== TEST RECOGNITION ENGINE ===")
    
    engine = RecognitionEngineImpl()
    test_strings = [
        "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",  # 1966
        "05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2"  # 2020
    ]
    
    for test_string in test_strings:
        print(f"\nTesting: {test_string[:50]}...")
        try:
            result = await engine.recognize_version(test_string)
            print(f"✓ Recognized as: {result.get('version', 'unknown')}")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
        except Exception as e:
            print(f"✗ Error: {e}")


def test_conversion():
    """Test conversion service"""
    print("\n=== TEST CONVERSION SERVICE ===")
    
    service = EuringConversionService()
    
    # Test 1966 → 2020
    euring_1966 = "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750"
    print(f"\nConverting 1966 → 2020:")
    print(f"Source: {euring_1966}")
    
    try:
        result = service.convert_semantic(euring_1966, '1966', '2020')
        if result['success']:
            print(f"✓ Target: {result['converted_string']}")
            
            # Test reverse conversion
            print(f"\nTesting reverse conversion 2020 → 1966:")
            reverse_result = service.convert_semantic(result['converted_string'], '2020', '1966')
            if reverse_result['success']:
                print(f"✓ Reverse: {reverse_result['converted_string']}")
                
                # Compare
                if euring_1966 == reverse_result['converted_string']:
                    print("✓ Perfect bidirectional conversion!")
                else:
                    print("⚠ Bidirectional conversion with differences (expected)")
            else:
                print(f"✗ Reverse conversion failed: {reverse_result.get('error')}")
        else:
            print(f"✗ Conversion failed: {result.get('error')}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("Quick API test for EURING system\n")
    
    # Test recognition
    asyncio.run(test_recognition())
    
    # Test conversion
    test_conversion()
    
    print("\n=== SUMMARY ===")
    print("Core services tested. If no errors above, the API should work correctly.")