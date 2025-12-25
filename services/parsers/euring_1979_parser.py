"""
EURING 1979 Parser - Fixed-length format parsing
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from ...models.euring_models import EuringVersion


class Euring1979Parser:
    """Parser for EURING 1979 format strings"""
    
    def __init__(self):
        self.field_definitions = {
            'species_code': {'start': 0, 'end': 5, 'type': 'numeric'},
            'scheme_country': {'start': 5, 'end': 7, 'type': 'alphanumeric'},
            'ring_number': {'start': 7, 'end': 14, 'type': 'alphanumeric'},
            'age_code': {'start': 14, 'end': 15, 'type': 'numeric'},
            'sex_code': {'start': 15, 'end': 16, 'type': 'numeric'},
            'status_code': {'start': 16, 'end': 17, 'type': 'numeric'},
            'date_first': {'start': 17, 'end': 23, 'type': 'date'},
            'date_current': {'start': 23, 'end': 29, 'type': 'date'},
            'latitude': {'start': 29, 'end': 35, 'type': 'coordinate'},
            'longitude': {'start': 35, 'end': 41, 'type': 'coordinate'},
            'condition_code': {'start': 41, 'end': 43, 'type': 'numeric'},
            'method_code': {'start': 43, 'end': 44, 'type': 'numeric'},
            'accuracy_code': {'start': 44, 'end': 46, 'type': 'numeric'},
            'empty_fields_1': {'start': 46, 'end': 48, 'type': 'string'},
            'wing_length': {'start': 48, 'end': 51, 'type': 'numeric'},
            'weight': {'start': 51, 'end': 55, 'type': 'numeric'},
            'empty_fields_2': {'start': 55, 'end': 57, 'type': 'string'},
            'bill_length': {'start': 57, 'end': 61, 'type': 'numeric'},
            'tarsus_length': {'start': 61, 'end': 63, 'type': 'numeric'},
            'empty_fields_3': {'start': 63, 'end': 65, 'type': 'string'},
            'additional_code_1': {'start': 65, 'end': 68, 'type': 'numeric'},
            'additional_code_2': {'start': 68, 'end': 71, 'type': 'numeric'},
            'padding': {'start': 71, 'end': 78, 'type': 'string'}
        }
    
    def parse(self, euring_string: str) -> Dict[str, Any]:
        """Parse EURING 1979 string into structured data"""
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Remove any whitespace and validate length
        euring_string = euring_string.strip()
        if len(euring_string) != 78:
            raise ValueError(f"EURING 1979 format requires exactly 78 characters, got {len(euring_string)}")
        
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
            if field_name == 'scheme_country':
                if not (len(value) == 2 and value.isalpha() and value.isupper()):
                    raise ValueError(f"Scheme country must be 2 uppercase letters, got '{value}'")
            elif field_name == 'ring_number':
                # 1979 format: 1 letter + 6 digits, but may have trailing space
                clean_value = value.rstrip()
                if not (len(clean_value) >= 6 and clean_value[0].isalpha() and clean_value[1:].replace(' ', '').isdigit()):
                    raise ValueError(f"Ring number must start with letter followed by digits, got '{value}'")
            return value
        
        elif field_type == 'date':
            return self._parse_date_ddmmyy(value)
        
        elif field_type == 'coordinate':
            if field_name == 'latitude':
                return self._parse_latitude_1979(value)
            elif field_name == 'longitude':
                return self._parse_longitude_1979(value)
        
        elif field_type == 'string':
            # Validate empty fields and padding
            if field_name.startswith('empty_fields') and value != '--':
                raise ValueError(f"Empty field {field_name} must be '--', got '{value}'")
            elif field_name == 'padding' and value != '------':
                raise ValueError(f"Padding must be '------', got '{value}'")
            return value
        
        return value
    
    def _parse_date_ddmmyy(self, date_str: str) -> Dict[str, Any]:
        """Parse date in DDMMYY format"""
        if len(date_str) != 6 or not date_str.isdigit():
            raise ValueError(f"Date must be 6 digits in DDMMYY format, got '{date_str}'")
        
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year_short = int(date_str[4:])
        
        # Convert 2-digit year to 4-digit (assuming 1900s for years 50-99, 2000s for 00-49)
        if year_short >= 50:
            year = 1900 + year_short
        else:
            year = 2000 + year_short
        
        # Basic validation
        if day < 1 or day > 31:
            raise ValueError(f"Invalid day: {day}")
        
        if month < 1 or month > 12:
            raise ValueError(f"Invalid month: {month}")
        
        try:
            date_obj = datetime(year, month, day)
        except ValueError as e:
            raise ValueError(f"Invalid date {day:02d}/{month:02d}/{year}: {e}")
        
        return {
            'day': day,
            'month': month,
            'year': year,
            'date_object': date_obj,
            'iso_format': date_obj.isoformat()[:10],
            'original': date_str
        }
    
    def _parse_latitude_1979(self, value: str) -> Dict[str, Any]:
        """Parse latitude coordinate (DDMMN/S)"""
        if len(value) != 6:
            raise ValueError(f"Latitude must be 6 characters, got {len(value)}")
        
        degrees_str = value[:2]
        minutes_str = value[2:4]
        seconds_str = value[4:5]
        direction = value[5]
        
        if not degrees_str.isdigit() or not minutes_str.isdigit() or not seconds_str.isdigit():
            raise ValueError(f"Latitude degrees, minutes, and seconds must be numeric")
        
        if direction not in ['N', 'S']:
            raise ValueError(f"Latitude direction must be N or S, got '{direction}'")
        
        degrees = int(degrees_str)
        minutes = int(minutes_str)
        seconds = int(seconds_str) * 6  # Convert to actual seconds (0-9 -> 0-54)
        
        if degrees > 90:
            raise ValueError(f"Latitude degrees cannot exceed 90, got {degrees}")
        
        if minutes > 59:
            raise ValueError(f"Latitude minutes cannot exceed 59, got {minutes}")
        
        # Convert to decimal degrees
        decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if direction == 'S':
            decimal_degrees = -decimal_degrees
        
        return {
            'degrees': degrees,
            'minutes': minutes,
            'seconds': seconds,
            'direction': direction,
            'decimal': decimal_degrees,
            'original': value
        }
    
    def _parse_longitude_1979(self, value: str) -> Dict[str, Any]:
        """Parse longitude coordinate (DDDMME/W)"""
        if len(value) != 6:
            raise ValueError(f"Longitude must be 6 characters, got {len(value)}")
        
        degrees_str = value[:3]
        minutes_str = value[3:5]
        direction = value[5]
        
        if not degrees_str.isdigit() or not minutes_str.isdigit():
            raise ValueError(f"Longitude degrees and minutes must be numeric")
        
        if direction not in ['E', 'W']:
            raise ValueError(f"Longitude direction must be E or W, got '{direction}'")
        
        degrees = int(degrees_str)
        minutes = int(minutes_str)
        
        if degrees > 180:
            raise ValueError(f"Longitude degrees cannot exceed 180, got {degrees}")
        
        if minutes > 59:
            raise ValueError(f"Longitude minutes cannot exceed 59, got {minutes}")
        
        # Convert to decimal degrees
        decimal_degrees = degrees + (minutes / 60.0)
        if direction == 'W':
            decimal_degrees = -decimal_degrees
        
        return {
            'degrees': degrees,
            'minutes': minutes,
            'direction': direction,
            'decimal': decimal_degrees,
            'original': value
        }
    
    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Validate parsed data and return list of errors"""
        errors = []
        
        # Age code validation
        if 'age_code' in parsed_data:
            age = parsed_data['age_code']
            if age < 0 or age > 9:
                errors.append(f"Age code must be between 0 and 9, got {age}")
        
        # Sex code validation
        if 'sex_code' in parsed_data:
            sex = parsed_data['sex_code']
            if sex < 0 or sex > 9:
                errors.append(f"Sex code must be between 0 and 9, got {sex}")
        
        # Species code validation (basic range check)
        if 'species_code' in parsed_data:
            species = parsed_data['species_code']
            if species < 10000 or species > 99999:
                errors.append(f"Species code should be 5 digits, got {species}")
        
        # Biometric measurements validation (basic sanity checks)
        if 'wing_length' in parsed_data:
            wing = parsed_data['wing_length']
            if wing > 0 and (wing < 30 or wing > 999):  # 0 might mean "not measured"
                errors.append(f"Wing length seems unrealistic: {wing}mm")
        
        if 'weight' in parsed_data:
            weight = parsed_data['weight']
            if weight > 0 and (weight < 10 or weight > 9999):  # Weight in 0.1g units
                errors.append(f"Weight seems unrealistic: {weight/10}g")
        
        return errors
    
    def to_dict(self, euring_string: str) -> Dict[str, Any]:
        """Parse string and return complete structured data"""
        parsed_data = self.parse(euring_string)
        
        # Add validation results
        errors = self.validate(parsed_data)
        parsed_data['validation_errors'] = errors
        parsed_data['is_valid'] = len(errors) == 0
        
        # Add metadata
        parsed_data['parser_version'] = '1.0'
        parsed_data['euring_version'] = '1979'
        parsed_data['original_string'] = euring_string
        
        return parsed_data