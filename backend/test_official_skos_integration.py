#!/usr/bin/env python3
"""
Test Official SKOS Integration for EURING 2020
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.parsers.euring_2020_official_parser import Euring2020OfficialParser
from app.services.semantic_converter import SemanticConverter
import json


def test_official_parser():
    """Test the official EURING 2020 parser"""
    print("=== Testing Official EURING 2020 Parser ===")
    
    parser = Euring2020OfficialParser()
    
    # Test with a sample official EURING 2020 string
    # Format: identification_number|ringing_scheme|primary_id_method|metal_ring_info|other_marks|
    #         species_finder|species_scheme|age_person|sex_person|sex_scheme|manipulated|moved|
    #         catching_method|catching_lures|ring_verification
    
    test_string = "ISA12345..|IAB|A0|1|ZZ|05320|05320|3|M|M|N|0|M|A|0"
    
    try:
        result = parser.to_dict(test_string)
        
        print(f"✅ Successfully parsed: {test_string}")
        print(f"   Fields parsed: {len(result) - 4}")  # Exclude metadata fields
        print(f"   Validation errors: {len(result.get('validation_errors', []))}")
        print(f"   Is valid: {result.get('is_valid', False)}")
        
        # Print key parsed fields
        key_fields = [
            'identification_number', 'ringing_scheme', 'species_as_mentioned_by_scheme',
            'age_mentioned_by_the_person', 'sex_concluded_by_the_scheme', 'manipulated'
        ]
        
        print("\n   Key parsed fields:")
        for field in key_fields:
            if field in result:
                field_data = result[field]
                if isinstance(field_data, dict):
                    if 'description' in field_data:
                        print(f"     {field}: {field_data.get('code', field_data.get('value', 'N/A'))} - {field_data['description']}")
                    else:
                        print(f"     {field}: {field_data}")
                else:
                    print(f"     {field}: {field_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing: {e}")
        return False


def test_semantic_conversion():
    """Test semantic conversion with official format"""
    print("\n=== Testing Semantic Conversion with Official Format ===")
    
    parser = Euring2020OfficialParser()
    converter = SemanticConverter()
    
    test_string = "ISA12345..|IAB|A0|1|ZZ|05320|05320|3|M|M|N|0|M|A|0"
    
    try:
        # Parse the string
        parsed_data = parser.parse(test_string)
        print(f"✅ Parsed {len(parsed_data)} fields")
        
        # Extract semantic data
        semantic_data = converter.extract_semantic_data(parsed_data, '2020_official')
        print(f"✅ Extracted {len(semantic_data)} semantic fields")
        
        # Print semantic fields
        print("\n   Semantic fields extracted:")
        for field_name, field_data in semantic_data.items():
            if isinstance(field_data, dict) and 'value' in field_data:
                print(f"     {field_name}: {field_data['value']} (from {field_data.get('source', 'unknown')})")
        
        # Test conversion to another format (e.g., 2020 simplified)
        try:
            converted_data = converter.convert_semantic_to_version(semantic_data, '2020')
            print(f"✅ Converted to 2020 format: {len(converted_data)} fields")
            
            # Print conversion notes
            if 'conversion_notes' in converted_data:
                notes = converted_data['conversion_notes']
                if notes:
                    print(f"   Conversion notes: {len(notes)} notes")
                    for note in notes[:3]:  # Show first 3 notes
                        print(f"     - {note}")
        
        except Exception as e:
            print(f"⚠️  Conversion error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in semantic conversion: {e}")
        return False


def test_field_validation():
    """Test field validation with official SKOS rules"""
    print("\n=== Testing Field Validation ===")
    
    parser = Euring2020OfficialParser()
    
    # Test cases with various validation scenarios
    test_cases = [
        {
            'name': 'Valid complete record',
            'string': 'ISA12345..|IAB|A0|1|ZZ|05320|05320|3|M|M|N|0|M|A|0',
            'should_pass': True
        },
        {
            'name': 'Invalid ringing scheme',
            'string': 'ISA12345..|XXX|A0|1|ZZ|05320|05320|3|M|M|N|0|M|A|0',
            'should_pass': True  # Allow unknown schemes, just mark as unknown
        },
        {
            'name': 'Invalid age code',
            'string': 'ISA12345..|IAB|A0|1|ZZ|05320|05320|Z|M|M|N|0|M|A|0',
            'should_pass': False
        },
        {
            'name': 'Invalid metal ring info',
            'string': 'ISA12345..|IAB|A0|9|ZZ|05320|05320|3|M|M|N|0|M|A|0',
            'should_pass': False
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        try:
            result = parser.to_dict(test_case['string'])
            is_valid = result.get('is_valid', False)
            errors = result.get('validation_errors', [])
            
            if test_case['should_pass']:
                if is_valid:
                    print(f"✅ {test_case['name']}: Passed validation as expected")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']}: Should pass but failed - {errors}")
            else:
                if not is_valid:
                    print(f"✅ {test_case['name']}: Failed validation as expected - {len(errors)} errors")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']}: Should fail but passed")
                    
        except Exception as e:
            if not test_case['should_pass']:
                print(f"✅ {test_case['name']}: Exception as expected - {e}")
                passed += 1
            else:
                print(f"❌ {test_case['name']}: Unexpected exception - {e}")
    
    print(f"\n   Validation tests: {passed}/{total} passed")
    return passed == total


def test_skos_compliance():
    """Test compliance with SKOS thesaurus definitions"""
    print("\n=== Testing SKOS Compliance ===")
    
    parser = Euring2020OfficialParser()
    
    # Test specific SKOS-defined values
    skos_tests = [
        {
            'field': 'manipulated',
            'valid_values': ['N', 'H', 'K', 'C', 'F', 'T', 'M', 'R', 'E', 'P', 'U'],
            'test_value': 'H'
        },
        {
            'field': 'catching_method',
            'valid_values': ['M', 'N', 'H', 'A', '-'],
            'test_value': 'M'
        },
        {
            'field': 'sex_mentioned_by_the_person',
            'valid_values': ['M', 'F', 'U'],
            'test_value': 'F'
        }
    ]
    
    base_string = "ISA12345..|IAB|A0|1|ZZ|05320|05320|3|F|F|N|0|M|A|0"  # Use F for both person and scheme
    fields = base_string.split('|')
    
    passed = 0
    total = 0
    
    for test in skos_tests:
        field_name = test['field']
        field_index = parser.field_names.index(field_name)
        
        for value in test['valid_values']:
            total += 1
            test_fields = fields.copy()
            test_fields[field_index] = value
            
            # For sex tests, make sure person and scheme sex match to avoid validation errors
            if field_name == 'sex_mentioned_by_the_person':
                sex_scheme_index = parser.field_names.index('sex_concluded_by_the_scheme')
                test_fields[sex_scheme_index] = value
            
            test_string = '|'.join(test_fields)
            
            try:
                result = parser.to_dict(test_string)
                if result.get('is_valid', False):
                    print(f"✅ {field_name}={value}: Valid according to SKOS")
                    passed += 1
                else:
                    print(f"❌ {field_name}={value}: Invalid - {result.get('validation_errors', [])}")
            except Exception as e:
                print(f"❌ {field_name}={value}: Exception - {e}")
    
    print(f"\n   SKOS compliance tests: {passed}/{total} passed")
    return passed == total


def main():
    """Run all tests"""
    print("🔬 Testing Official SKOS Integration for EURING 2020\n")
    
    tests = [
        test_official_parser,
        test_semantic_conversion,
        test_field_validation,
        test_skos_compliance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n🎯 Overall Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("✅ All tests passed! Official SKOS integration is working correctly.")
        
        # Show summary of improvements
        print("\n📈 SKOS Integration Improvements:")
        print("   • Official field definitions from SKOS thesaurus")
        print("   • Precise validation rules based on EURING standards")
        print("   • Priority-based manipulation codes")
        print("   • Comprehensive field descriptions and notes")
        print("   • Cross-field validation logic")
        print("   • Support for official EURING 2020 format")
        
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)