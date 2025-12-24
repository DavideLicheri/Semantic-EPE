"""
EURING 2000 Parser - Complex fixed-length format parsing
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from ...models.euring_models import EuringVersion


class Euring2000Parser:
    """Parser for EURING 2000 format strings"""
    
    def __init__(self):
        self.field_definitions = {
            'scheme_code': {'start': 0, 'end': 4, 'type': 'alphanumeric'},
            'ring_prefix': {'start': 4, 'end': 7, 'type': 'alphanumeric'},
            'separator': {'start': 7, 'end': 10, 'type': 'string'},
            'ring_number': {'start': 10, 'end': 17, 'type': 'numeric'},
            'ring_suffix': {'start': 17, 'end': 19, 'type': 'alphanumeric'},
            'date_first': {'start': 19, 'end': 24, 'type': 'date_encoded'},
            'date_current': {'start': 24, 'end': 29, 'type': 'date_encoded'},
            'status_code': {'start': 29, 'end': 30, 'type': 'alphanumeric'},
            'age_code': {'start': 30, 'end': 31, 'type': 'numeric'},
            'location_code': {'start': 31, 'end': 36, 'type': 'alphanumeric'},
            'accuracy_code': {'start': 36, 'end': 38, 'type': 'alphanumeric'},
            'empty_fields_1': {'start': 38, 'end': 43, 'type': 'string'},
            'measurement_1': {'start': 43, 'end': 47, 'type': 'numeric'},
            'measurement_2': {'start': 47, 'end': 50, 'type': 'numeric'},
            'measurement_3': {'start': 50, 'end': 53, 'type': 'numeric'},
            'measurement_4': {'start': 53, 'end': 56, 'type': 'numeric'},
            'region_code': {'start': 56, 'end': 60, 'type': 'alphanumeric'},
            'latitude_sign': {'start': 60, 'end': 61, 'type': 'string'},
            'latitude_value': {'start': 61, 'end': 67, 'type': 'numeric'},
            'longitude_sign': {'start': 67, 'end': 68, 'type': 'string'},
            'longitude_value': {'start': 68, 'end': 74, 'type': 'numeric'},
            'additional_codes': {'start': 74, 'end': 86, 'type': 'numeric'},
            'empty_fields_2': {'start': 86, 'end': 89, 'type': 'string'},
            'final_code': {'start': 89, 'end': 96, 'type': 'numeric'}
        }
    
    def parse(self, euring_string: str) -> Dict[str, Any]:
        """Parse EURING 2000 string into structured data"""
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Remove any whitespace and validate length
        euring_string = euring_string.strip()
        if len(euring_string) != 96:
            raise ValueError(f"EURING 2000 format requires exactly 96 characters, got {len(euring_string)}")
        
        parsed_data = {}
        
        # Parse each field
        for field_name, field_def in self.field_definitions.items():
            start = field_def['start']
            end = field_def['end']
            field_type = field_def['type']
            
            field_value = euring_string[start:end]
            
            # Parse and validate field
            parsed_data[field_name] = self._parse_field(field_name, field_value, field_type)
        
        return parsed_data
    
    def _parse_field(self, field_name: str, value: str, field_type: str) -> Any:
        """Parse individual field based on its type"""
        
        if field_type == 'numeric':
            if not value.isdigit():
                raise ValueError(f"Field {field_name} must be numeric, got '{value}'")
            return int(value)
        
        elif field_type == 'alphanumeric':
            if not value.isalnum() or not value.isupper():
                raise ValueError(f"Field {field_name} must be uppercase alphanumeric, got '{value}'")
            return value
        
        elif field_type == 'date_encoded':
            return self._parse_encoded_date(value)
        
        elif field_type == 'string':
            # Validate separators and empty fields
            if field_name == 'separator' and value != '...':
                raise ValueError(f"Separator must be '...', got '{value}'")
            elif field_name == 'empty_fields_1' and value != '-----':
                raise ValueError(f"Empty field {field_name} must be '-----', got '{value}'")
            elif field_name == 'empty_fields_2' and value != '---':
                raise ValueError(f"Empty field {field_name} must be '---', got '{value}'")
            elif field_name.endswith('_sign') and value not in ['+', '-']:
                raise ValueError(f"Sign field {field_name} must be + or -, got '{value}'")
            return value
        
        return value
    
    def _parse_encoded_date(self, date_str: str) -> Dict[str, Any]:
        """Parse encoded date (5 digits)"""
        if len(date_str) != 5 or not date_str.isdigit():
            raise ValueError(f"Encoded date must be 5 digits, got '{date_str}'")
        
        # This is a simplified interpretation - actual EURING 2000 date encoding may be different
        # The encoding likely represents days since a reference date or similar
        encoded_value = int(date_str)
        
        return {
            'encoded_value': encoded_value,
            'original': date_str,
            'note': 'Encoded date format - requires EURING specification for proper decoding'
        }
    
    def _parse_coordinates(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse coordinate fields into decimal degrees"""
        coordinates = {}
        
        if 'latitude_sign' in parsed_data and 'latitude_value' in parsed_data:
            lat_sign = parsed_data['latitude_sign']
            lat_value = parsed_data['latitude_value']
            
            # Convert encoded latitude to decimal degrees
            # This is a simplified interpretation - actual encoding may be different
            decimal_lat = lat_value / 10000.0  # Assuming 4 decimal places
            if lat_sign == '-':
                decimal_lat = -decimal_lat
            
            coordinates['latitude'] = {
                'decimal': decimal_lat,
                'sign': lat_sign,
                'encoded_value': lat_value,
                'original': f"{lat_sign}{lat_value:06d}"
            }
        
        if 'longitude_sign' in parsed_data and 'longitude_value' in parsed_data:
            lon_sign = parsed_data['longitude_sign']
            lon_value = parsed_data['longitude_value']
            
            # Convert encoded longitude to decimal degrees
            decimal_lon = lon_value / 10000.0  # Assuming 4 decimal places
            if lon_sign == '-':
                decimal_lon = -decimal_lon
            
            coordinates['longitude'] = {
                'decimal': decimal_lon,
                'sign': lon_sign,
                'encoded_value': lon_value,
                'original': f"{lon_sign}{lon_value:06d}"
            }
        
        return coordinates
    
    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Validate parsed data and return list of errors"""
        errors = []
        
        # Age code validation
        if 'age_code' in parsed_data:
            age = parsed_data['age_code']
            if age < 0 or age > 9:
                errors.append(f"Age code must be between 0 and 9, got {age}")
        
        # Ring number validation
        if 'ring_number' in parsed_data:
            ring_num = parsed_data['ring_number']
            if ring_num < 1000000 or ring_num > 9999999:
                errors.append(f"Ring number should be 7 digits, got {ring_num}")
        
        # Coordinate validation
        coordinates = self._parse_coordinates(parsed_data)
        if 'latitude' in coordinates:
            lat = coordinates['latitude']['decimal']
            if lat < -90 or lat > 90:
                errors.append(f"Latitude out of valid range: {lat}")
        
        if 'longitude' in coordinates:
            lon = coordinates['longitude']['decimal']
            if lon < -180 or lon > 180:
                errors.append(f"Longitude out of valid range: {lon}")
        
        return errors
    
    def to_dict(self, euring_string: str) -> Dict[str, Any]:
        """Parse string and return complete structured data"""
        parsed_data = self.parse(euring_string)
        
        # Add parsed coordinates
        coordinates = self._parse_coordinates(parsed_data)
        if coordinates:
            parsed_data['coordinates'] = coordinates
        
        # Add validation results
        errors = self.validate(parsed_data)
        parsed_data['validation_errors'] = errors
        parsed_data['is_valid'] = len(errors) == 0
        
        # Add metadata
        parsed_data['parser_version'] = '1.0'
        parsed_data['euring_version'] = '2000'
        parsed_data['original_string'] = euring_string
        
        return parsed_data