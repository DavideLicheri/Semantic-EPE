"""
EURING 1966 Parser - Detailed field-by-field parsing
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from ...models.euring_models import EuringVersion


class Euring1966Parser:
    """Parser for EURING 1966 format strings"""
    
    def __init__(self):
        self.field_definitions = {
            'species_code': {'position': 0, 'length': 4, 'type': 'numeric'},
            'ring_number': {'position': 1, 'length': 7, 'type': 'alphanumeric'},
            'age_code': {'position': 2, 'length': 1, 'type': 'numeric'},
            'date_code': {'position': 3, 'length': 8, 'type': 'numeric'},
            'latitude': {'position': 4, 'length': 5, 'type': 'coordinate'},
            'longitude': {'position': 5, 'length': 6, 'type': 'coordinate'},
            'condition_code': {'position': 6, 'length': 2, 'type': 'numeric'},
            'method_code': {'position': 7, 'length': 1, 'type': 'numeric'},
            'wing_length': {'position': 8, 'length': 3, 'type': 'numeric'},
            'weight': {'position': 9, 'length': 4, 'type': 'numeric'},
            'bill_length': {'position': 10, 'length': 4, 'type': 'numeric'}
        }
    
    def parse(self, euring_string: str) -> Dict[str, Any]:
        """Parse EURING 1966 string into structured data"""
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Split by spaces
        fields = euring_string.strip().split(' ')
        
        if len(fields) != 11:
            raise ValueError(f"EURING 1966 format requires exactly 11 fields, got {len(fields)}")
        
        parsed_data = {}
        
        # Parse each field
        for field_name, field_def in self.field_definitions.items():
            position = field_def['position']
            expected_length = field_def['length']
            field_type = field_def['type']
            
            if position >= len(fields):
                raise ValueError(f"Missing field {field_name} at position {position}")
            
            field_value = fields[position]
            
            # Validate field length
            if len(field_value) != expected_length:
                raise ValueError(f"Field {field_name} must be {expected_length} characters, got {len(field_value)}")
            
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
            if field_name == 'ring_number':
                if not (len(value) == 7 and value[:2].isalpha() and value[2:].isdigit()):
                    raise ValueError(f"Ring number must be 2 letters + 5 digits, got '{value}'")
            return value
        
        elif field_type == 'coordinate':
            if field_name == 'latitude':
                return self._parse_latitude(value)
            elif field_name == 'longitude':
                return self._parse_longitude(value)
        
        return value
    
    def _parse_latitude(self, value: str) -> Dict[str, Any]:
        """Parse latitude coordinate (DDMMN/S)"""
        if len(value) != 5:
            raise ValueError(f"Latitude must be 5 characters, got {len(value)}")
        
        degrees_str = value[:2]
        minutes_str = value[2:4]
        direction = value[4]
        
        if not degrees_str.isdigit() or not minutes_str.isdigit():
            raise ValueError(f"Latitude degrees and minutes must be numeric")
        
        if direction not in ['N', 'S']:
            raise ValueError(f"Latitude direction must be N or S, got '{direction}'")
        
        degrees = int(degrees_str)
        minutes = int(minutes_str)
        
        if degrees > 90:
            raise ValueError(f"Latitude degrees cannot exceed 90, got {degrees}")
        
        if minutes > 59:
            raise ValueError(f"Latitude minutes cannot exceed 59, got {minutes}")
        
        # Convert to decimal degrees
        decimal_degrees = degrees + (minutes / 60.0)
        if direction == 'S':
            decimal_degrees = -decimal_degrees
        
        return {
            'degrees': degrees,
            'minutes': minutes,
            'direction': direction,
            'decimal': decimal_degrees,
            'original': value
        }
    
    def _parse_longitude(self, value: str) -> Dict[str, Any]:
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
    
    def _parse_date(self, date_str: str) -> Dict[str, Any]:
        """Parse date in DDMMYYYY format"""
        if len(date_str) != 8 or not date_str.isdigit():
            raise ValueError(f"Date must be 8 digits in DDMMYYYY format, got '{date_str}'")
        
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:])
        
        # Basic validation
        if day < 1 or day > 31:
            raise ValueError(f"Invalid day: {day}")
        
        if month < 1 or month > 12:
            raise ValueError(f"Invalid month: {month}")
        
        if year < 1900 or year > 2100:
            raise ValueError(f"Invalid year: {year}")
        
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
    
    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Validate parsed data and return list of errors"""
        errors = []
        
        # Age code validation
        if 'age_code' in parsed_data:
            age = parsed_data['age_code']
            if age < 1 or age > 9:
                errors.append(f"Age code must be between 1 and 9, got {age}")
        
        # Species code validation (basic range check)
        if 'species_code' in parsed_data:
            species = parsed_data['species_code']
            if species < 1000 or species > 9999:
                errors.append(f"Species code should be 4 digits, got {species}")
        
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
        
        # Add parsed date
        if 'date_code' in parsed_data:
            date_str = str(parsed_data['date_code']).zfill(8)
            parsed_data['parsed_date'] = self._parse_date(date_str)
        
        # Add validation results
        errors = self.validate(parsed_data)
        parsed_data['validation_errors'] = errors
        parsed_data['is_valid'] = len(errors) == 0
        
        # Add metadata
        parsed_data['parser_version'] = '1.0'
        parsed_data['euring_version'] = '1966'
        parsed_data['original_string'] = euring_string
        
        return parsed_data