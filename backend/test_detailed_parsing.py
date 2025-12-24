#!/usr/bin/env python3
"""
Test script for detailed EURING parsing and conversion
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.parsers.euring_1966_parser import Euring1966Parser
from app.services.parsers.euring_1979_parser import Euring1979Parser
from app.services.parsers.euring_2000_parser import Euring2000Parser
from app.services.parsers.euring_2020_parser import Euring2020Parser
from app.services.conversion_service import EuringConversionService
from app.services.recognition_engine import RecognitionEngineImpl
import json


def test_detailed_parsing():
    """Test detailed parsing of all EURING versions"""
    
    # Real EURING strings from context
    test_strings = {
        '1966': '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
        '1979': '05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------',
        '2000': 'IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086',
        '2020': '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2'
    }
    
    parsers = {
        '1966': Euring1966Parser(),
        '1979': Euring1979Parser(),
        '2000': Euring2000Parser(),
        '2020': Euring2020Parser()
    }
    
    print("=== DETAILED EURING PARSING TEST ===\n")
    
    for version, euring_string in test_strings.items():
        print(f"Testing EURING {version} Parser:")
        print(f"String: {euring_string}")
        print(f"Length: {len(euring_string)} characters")
        
        try:
            parser = parsers[version]
            result = parser.to_dict(euring_string)
            
            print(f"✓ Parsing successful")
            print(f"  Valid: {result.get('is_valid', False)}")
            print(f"  Errors: {len(result.get('validation_errors', []))}")
            
            if result.get('validation_errors'):
                for error in result['validation_errors']:
                    print(f"    - {error}")
            
            # Show key parsed fields
            key_fields = ['species_code', 'ring_number', 'age_code', 'date_code', 'latitude', 'longitude']
            print("  Key fields:")
            for field in key_fields:
                if field in result:
                    value = result[field]
                    if isinstance(value, dict):
                        # Show simplified version for complex fields
                        if 'original' in value:
                            print(f"    {field}: {value['original']} (parsed)")
                        elif 'decimal' in value:
                            print(f"    {field}: {value['decimal']} decimal")
                        else:
                            print(f"    {field}: {str(value)[:50]}...")
                    else:
                        print(f"    {field}: {value}")
            
        except Exception as e:
            print(f"✗ Parsing failed: {str(e)}")
        
        print()


def test_recognition_engine():
    """Test recognition engine with real strings"""
    
    test_strings = {
        '1966': '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
        '1979': '05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------',
        '2000': 'IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086',
        '2020': '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2'
    }
    
    print("=== RECOGNITION ENGINE TEST ===\n")
    
    engine = RecognitionEngineImpl()
    
    for expected_version, euring_string in test_strings.items():
        print(f"Testing recognition of EURING {expected_version}:")
        print(f"String: {euring_string[:60]}...")
        
        try:
            result = engine.recognize_version(euring_string)
            
            detected_version = result.get('version')
            confidence = result.get('confidence', 0)
            
            if detected_version == f"euring_{expected_version}":
                print(f"✓ Correctly identified as {detected_version}")
                print(f"  Confidence: {confidence:.2%}")
            else:
                print(f"✗ Incorrectly identified as {detected_version} (expected euring_{expected_version})")
                print(f"  Confidence: {confidence:.2%}")
            
            # Show discriminant analysis
            if 'discriminant_analysis' in result:
                analysis = result['discriminant_analysis']
                print(f"  Discriminants: {analysis}")
            
        except Exception as e:
            print(f"✗ Recognition failed: {str(e)}")
        
        print()


def test_conversion_service():
    """Test conversion between versions"""
    
    print("=== CONVERSION SERVICE TEST ===\n")
    
    # Test 1966 to 2020 conversion
    euring_1966 = '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750'
    euring_2020 = '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2'
    
    converter = EuringConversionService()
    
    print("Testing 1966 → 2020 conversion:")
    print(f"Source: {euring_1966}")
    
    try:
        result = converter.convert(euring_1966, '1966', '2020')
        
        if result['success']:
            print(f"✓ Conversion successful")
            print(f"Target: {result['converted_string']}")
            print(f"Notes: {len(result.get('conversion_notes', []))} conversion notes")
            
            for note in result.get('conversion_notes', []):
                print(f"  - {note}")
        else:
            print(f"✗ Conversion failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"✗ Conversion error: {str(e)}")
    
    print()
    
    # Test 2020 to 1966 conversion
    print("Testing 2020 → 1966 conversion:")
    print(f"Source: {euring_2020}")
    
    try:
        result = converter.convert(euring_2020, '2020', '1966')
        
        if result['success']:
            print(f"✓ Conversion successful")
            print(f"Target: {result['converted_string']}")
            print(f"Notes: {len(result.get('conversion_notes', []))} conversion notes")
            
            for note in result.get('conversion_notes', []):
                print(f"  - {note}")
        else:
            print(f"✗ Conversion failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"✗ Conversion error: {str(e)}")
    
    print()


def test_field_semantic_analysis():
    """Test semantic field analysis across versions"""
    
    print("=== SEMANTIC FIELD ANALYSIS ===\n")
    
    # Parse the same conceptual data across versions
    test_strings = {
        '1966': '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
        '2020': '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2'
    }
    
    parsers = {
        '1966': Euring1966Parser(),
        '2020': Euring2020Parser()
    }
    
    parsed_data = {}
    
    for version, euring_string in test_strings.items():
        try:
            parser = parsers[version]
            result = parser.to_dict(euring_string)
            parsed_data[version] = result
            print(f"Parsed {version}: ✓")
        except Exception as e:
            print(f"Failed to parse {version}: {e}")
            return
    
    print("\nSemantic field comparison:")
    
    # Compare semantic fields
    semantic_fields = [
        ('species_code', 'Species identification'),
        ('ring_number', 'Ring identifier'),
        ('age_code', 'Age classification'),
        ('latitude', 'Geographic latitude'),
        ('longitude', 'Geographic longitude'),
        ('wing_length', 'Wing measurement'),
        ('weight', 'Body weight')
    ]
    
    for field_name, description in semantic_fields:
        print(f"\n{description} ({field_name}):")
        
        for version in ['1966', '2020']:
            if version in parsed_data:
                data = parsed_data[version]
                
                if field_name in data:
                    value = data[field_name]
                    
                    if isinstance(value, dict):
                        if 'decimal' in value:
                            print(f"  {version}: {value['decimal']} (decimal)")
                        elif 'original' in value:
                            print(f"  {version}: {value['original']} (original)")
                        elif 'value' in value:
                            print(f"  {version}: {value['value']} {value.get('unit', '')}")
                        else:
                            print(f"  {version}: {str(value)[:30]}...")
                    else:
                        print(f"  {version}: {value}")
                else:
                    print(f"  {version}: [not available]")


if __name__ == "__main__":
    print("Starting comprehensive EURING parsing and conversion tests...\n")
    
    test_detailed_parsing()
    test_recognition_engine()
    test_conversion_service()
    test_field_semantic_analysis()
    
    print("=== TEST SUMMARY ===")
    print("All tests completed. Check output above for detailed results.")
    print("This validates the detailed SKOS models and parsing capabilities.")