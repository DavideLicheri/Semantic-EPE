"""
EURING 2020 Parser - Pipe-delimited format parsing
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from ...models.euring_models import EuringVersion


class Euring2020Parser:
    """Parser for EURING 2020 format strings"""
    
    def __init__(self):
        self.field_names = [
            'species_code', 'ring_number', 'metal_ring_info', 'other_marks_info',
            'age_code', 'sex_code', 'date_code', 'time_code', 'latitude_decimal',
            'longitude_decimal', 'condition_code', 'method_code', 'accuracy_code',
            'status_info', 'verification_code', 'wing_length', 'weight',
            'bill_length', 'tarsus_length', 'fat_score', 'muscle_score', 'moult_code'
        ]
    
    def parse(self, euring_string: str) -> Dict[str, Any]:
        """Parse EURING 2020 string into structured data"""
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Split by pipe separator
        fields = euring_string.strip().split('|')
        
        if len(fields) != 22:
            raise ValueError(f"EURING 2020 format requires exactly 22 fields, got {len(fields)}")
        
        parsed_data = {}
        
        # Parse each field
        for i, field_name in enumerate(self.field_names):
            if i >= len(fields):
                raise ValueError(f"Missing field {field_name} at position {i}")
            
            field_value = fields[i]
            
            # Parse and validate field
            parsed_data[field_name] = self._parse_field(field_name, field_value)
        
        return parsed_data
    
    def _parse_field(self, field_name: str, value: str) -> Any:
        """Parse individual field based on its name and expected type"""
        
        # Numeric fields
        if field_name in ['species_code', 'metal_ring_info', 'other_marks_info', 'age_code', 
                         'sex_code', 'condition_code', 'method_code', 'accuracy_code',
                         'status_info', 'verification_code', 'bill_length', 'tarsus_length',
                         'fat_score', 'muscle_score', 'moult_code']:
            if not value.isdigit():
                raise ValueError(f"Field {field_name} must be numeric, got '{value}'")
            return int(value)
        
        # Alphanumeric fields
        elif field_name == 'ring_number':
            if not (len(value) == 8 and value[:3].isalpha() and value[3:].isdigit() and value[:3].isupper()):
                raise ValueError(f"Ring number must be 3 uppercase letters + 5 digits, got '{value}'")
            return value
        
        # Date field
        elif field_name == 'date_code':
            return self._parse_date_yyyymmdd(value)
        
        # Time field
        elif field_name == 'time_code':
            return self._parse_time_hhmm(value)
        
        # Decimal coordinate fields
        elif field_name in ['latitude_decimal', 'longitude_decimal']:
            return self._parse_decimal_coordinate(field_name, value)
        
        # Decimal measurement fields
        elif field_name in ['wing_length', 'weight']:
            return self._parse_decimal_measurement(field_name, value)
        
        return value
    
    def _parse_date_yyyymmdd(self, date_str: str) -> Dict[str, Any]:
        """Parse date in YYYYMMDD format"""
        if len(date_str) != 8 or not date_str.isdigit():
            raise ValueError(f"Date must be 8 digits in YYYYMMDD format, got '{date_str}'")
        
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        
        # Basic validation
        if year < 1900 or year > 2100:
            raise ValueError(f"Invalid year: {year}")
        
        if month < 1 or month > 12:
            raise ValueError(f"Invalid month: {month}")
        
        if day < 1 or day > 31:
            raise ValueError(f"Invalid day: {day}")
        
        try:
            date_obj = datetime(year, month, day)
        except ValueError as e:
            raise ValueError(f"Invalid date {year}-{month:02d}-{day:02d}: {e}")
        
        return {
            'year': year,
            'month': month,
            'day': day,
            'date_object': date_obj,
            'iso_format': date_obj.isoformat()[:10],
            'original': date_str
        }
    
    def _parse_time_hhmm(self, time_str: str) -> Dict[str, Any]:
        """Parse time in HHMM format"""
        if len(time_str) != 4 or not time_str.isdigit():
            raise ValueError(f"Time must be 4 digits in HHMM format, got '{time_str}'")
        
        hour = int(time_str[:2])
        minute = int(time_str[2:4])
        
        # Basic validation
        if hour < 0 or hour > 23:
            raise ValueError(f"Invalid hour: {hour}")
        
        if minute < 0 or minute > 59:
            raise ValueError(f"Invalid minute: {minute}")
        
        return {
            'hour': hour,
            'minute': minute,
            'time_string': f"{hour:02d}:{minute:02d}",
            'original': time_str
        }
    
    def _parse_decimal_coordinate(self, field_name: str, value: str) -> Dict[str, Any]:
        """Parse decimal coordinate (latitude or longitude)"""
        try:
            decimal_value = float(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a valid decimal number, got '{value}'")
        
        # Validate ranges
        if field_name == 'latitude_decimal':
            if decimal_value < -90 or decimal_value > 90:
                raise ValueError(f"Latitude must be between -90 and 90 degrees, got {decimal_value}")
        elif field_name == 'longitude_decimal':
            if decimal_value < -180 or decimal_value > 180:
                raise ValueError(f"Longitude must be between -180 and 180 degrees, got {decimal_value}")
        
        return {
            'decimal': decimal_value,
            'hemisphere': 'N' if decimal_value >= 0 else 'S' if field_name == 'latitude_decimal' else 'E' if decimal_value >= 0 else 'W',
            'absolute_value': abs(decimal_value),
            'original': value
        }
    
    def _parse_decimal_measurement(self, field_name: str, value: str) -> Dict[str, Any]:
        """Parse decimal measurement (wing length, weight)"""
        try:
            decimal_value = float(value)
        except ValueError:
            raise ValueError(f"{field_name} must be a valid decimal number, got '{value}'")
        
        # Basic sanity checks
        if decimal_value < 0:
            raise ValueError(f"{field_name} cannot be negative, got {decimal_value}")
        
        if field_name == 'wing_length' and decimal_value > 1000:
            raise ValueError(f"Wing length seems unrealistic: {decimal_value}mm")
        
        if field_name == 'weight' and decimal_value > 10000:
            raise ValueError(f"Weight seems unrealistic: {decimal_value}g")
        
        return {
            'value': decimal_value,
            'unit': 'mm' if field_name == 'wing_length' else 'g' if field_name == 'weight' else '',
            'original': value
        }
    
    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Validate parsed data and return list of errors"""
        errors = []
        
        # Species code validation
        if 'species_code' in parsed_data:
            species = parsed_data['species_code']
            if species < 10000 or species > 99999:
                errors.append(f"Species code should be 5 digits, got {species}")
        
        # Age code validation
        if 'age_code' in parsed_data:
            age = parsed_data['age_code']
            if age < 1 or age > 9:
                errors.append(f"Age code must be between 1 and 9, got {age}")
        
        # Sex code validation
        if 'sex_code' in parsed_data:
            sex = parsed_data['sex_code']
            if sex < 1 or sex > 9:
                errors.append(f"Sex code must be between 1 and 9, got {sex}")
        
        # Date validation
        if 'date_code' in parsed_data and isinstance(parsed_data['date_code'], dict):
            date_info = parsed_data['date_code']
            if 'date_object' in date_info:
                # Check if date is not in the future
                if date_info['date_object'] > datetime.now():
                    errors.append(f"Date cannot be in the future: {date_info['iso_format']}")
        
        # Measurement validation
        if 'wing_length' in parsed_data and isinstance(parsed_data['wing_length'], dict):
            wing = parsed_data['wing_length']['value']
            if wing > 0 and (wing < 30 or wing > 999):
                errors.append(f"Wing length seems unrealistic: {wing}mm")
        
        if 'weight' in parsed_data and isinstance(parsed_data['weight'], dict):
            weight = parsed_data['weight']['value']
            if weight > 0 and (weight < 1 or weight > 5000):
                errors.append(f"Weight seems unrealistic: {weight}g")
        
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
        parsed_data['euring_version'] = '2020'
        parsed_data['original_string'] = euring_string
        
        return parsed_data