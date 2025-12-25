"""
Semantic Converter for EURING Codes
Handles conversion based on semantic meaning rather than literal values
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re
from dataclasses import dataclass


@dataclass
class SemanticField:
    """Represents a semantic field with its properties"""
    name: str
    semantic_meaning: str
    data_type: str
    required: bool = True
    default_value: Any = None
    conversion_notes: List[str] = None
    
    def __post_init__(self):
        if self.conversion_notes is None:
            self.conversion_notes = []


class SemanticConverter:
    """Converts EURING codes based on semantic meaning"""
    
    def __init__(self):
        self.semantic_fields = self._define_semantic_fields()
        self.version_mappings = self._define_version_mappings()
    
    def _define_semantic_fields(self) -> Dict[str, SemanticField]:
        """Define all semantic fields across EURING versions"""
        return {
            'species_identification': SemanticField(
                name='species_identification',
                semantic_meaning='EURING species code identifying the bird species',
                data_type='numeric',
                required=True
            ),
            'ring_identification': SemanticField(
                name='ring_identification',
                semantic_meaning='Unique identifier of the ring attached to the bird',
                data_type='alphanumeric',
                required=True
            ),
            'ringing_scheme': SemanticField(
                name='ringing_scheme',
                semantic_meaning='Identification of the ringing scheme or country',
                data_type='alphanumeric',
                required=False,
                default_value='XX'
            ),
            'age_classification': SemanticField(
                name='age_classification',
                semantic_meaning='Age category of the bird at time of capture',
                data_type='numeric',
                required=True,
                default_value=9  # Unknown
            ),
            'sex_classification': SemanticField(
                name='sex_classification',
                semantic_meaning='Sex identification of the bird',
                data_type='numeric',
                required=False,
                default_value=9  # Unknown
            ),
            'capture_date': SemanticField(
                name='capture_date',
                semantic_meaning='Date when the bird was captured or observed',
                data_type='date',
                required=True
            ),
            'capture_time': SemanticField(
                name='capture_time',
                semantic_meaning='Time when the bird was captured or observed',
                data_type='time',
                required=False,
                default_value='1200'  # Noon
            ),
            'geographic_latitude': SemanticField(
                name='geographic_latitude',
                semantic_meaning='Latitude coordinate of capture location',
                data_type='coordinate',
                required=True
            ),
            'geographic_longitude': SemanticField(
                name='geographic_longitude',
                semantic_meaning='Longitude coordinate of capture location',
                data_type='coordinate',
                required=True
            ),
            'capture_conditions': SemanticField(
                name='capture_conditions',
                semantic_meaning='Conditions or circumstances of capture',
                data_type='numeric',
                required=False,
                default_value=0
            ),
            'capture_method': SemanticField(
                name='capture_method',
                semantic_meaning='Method used for capture or observation',
                data_type='numeric',
                required=False,
                default_value=1
            ),
            'wing_measurement': SemanticField(
                name='wing_measurement',
                semantic_meaning='Wing length measurement in millimeters',
                data_type='measurement',
                required=False,
                default_value=0
            ),
            'weight_measurement': SemanticField(
                name='weight_measurement',
                semantic_meaning='Body weight measurement',
                data_type='measurement',
                required=False,
                default_value=0
            ),
            'bill_measurement': SemanticField(
                name='bill_measurement',
                semantic_meaning='Bill length measurement',
                data_type='measurement',
                required=False,
                default_value=0
            )
        }
    
    def _define_version_mappings(self) -> Dict[str, Dict[str, str]]:
        """Define how semantic fields map to version-specific fields"""
        return {
            '1966': {
                'species_identification': 'species_code',
                'ring_identification': 'ring_number',
                'age_classification': 'age_code',
                'capture_date': 'date_code',
                'geographic_latitude': 'latitude',
                'geographic_longitude': 'longitude',
                'capture_conditions': 'condition_code',
                'capture_method': 'method_code',
                'wing_measurement': 'wing_length',
                'weight_measurement': 'weight',
                'bill_measurement': 'bill_length'
            },
            '1979': {
                'species_identification': 'species_code',
                'ringing_scheme': 'scheme_country',
                'ring_identification': 'ring_number',
                'age_classification': 'age_code',
                'sex_classification': 'sex_code',
                'capture_date': 'date_current',  # Use current date
                'geographic_latitude': 'latitude_encoded',
                'geographic_longitude': 'longitude_encoded',
                'capture_conditions': 'condition_code',
                'capture_method': 'method_code',
                'wing_measurement': 'wing_length',
                'weight_measurement': 'weight',
                'bill_measurement': 'bill_length'
            },
            '2000': {
                'species_identification': 'scheme_code',  # May be encoded
                'ringing_scheme': 'scheme_code',
                'ring_identification': 'ring_number',
                'age_classification': 'age_code',
                'capture_date': 'date_current',
                'geographic_latitude': 'latitude_value',
                'geographic_longitude': 'longitude_value',
                'wing_measurement': 'measurement_1',
                'weight_measurement': 'measurement_2',
                'bill_measurement': 'measurement_3'
            },
            '2020': {
                'species_identification': 'species_code',
                'ring_identification': 'ring_number',
                'age_classification': 'age_code',
                'sex_classification': 'sex_code',
                'capture_date': 'date_code',
                'capture_time': 'time_code',
                'geographic_latitude': 'latitude_decimal',
                'geographic_longitude': 'longitude_decimal',
                'capture_conditions': 'condition_code',
                'capture_method': 'method_code',
                'wing_measurement': 'wing_length',
                'weight_measurement': 'weight',
                'bill_measurement': 'bill_length'
            },
            '2020_official': {
                'species_identification': 'species_as_mentioned_by_scheme',
                'ring_identification': 'identification_number',
                'ringing_scheme': 'ringing_scheme',
                'age_classification': 'age_mentioned_by_the_person',
                'sex_classification': 'sex_concluded_by_the_scheme',
                'capture_method': 'catching_method',
                'capture_conditions': 'manipulated',
                'movement_status': 'moved_before',
                'capture_lures': 'catching_lures',
                'ring_verification': 'verification_of_the_metal_ring',
                'metal_ring_status': 'metal_ring_information',
                'other_marks': 'other_marks_information',
                'primary_id_method': 'primary_identification_method'
            }
        }
    
    def extract_semantic_data(self, parsed_data: Dict[str, Any], source_version: str) -> Dict[str, Any]:
        """Extract semantic data from parsed version-specific data"""
        semantic_data = {}
        version_mapping = self.version_mappings.get(source_version, {})
        
        for semantic_field_name, field_def in self.semantic_fields.items():
            version_field_name = version_mapping.get(semantic_field_name)
            
            if version_field_name and version_field_name in parsed_data:
                raw_value = parsed_data[version_field_name]
                semantic_value = self._convert_to_semantic(
                    raw_value, field_def, source_version, version_field_name
                )
                semantic_data[semantic_field_name] = semantic_value
            elif field_def.required:
                # Use default value for required fields
                semantic_data[semantic_field_name] = {
                    'value': field_def.default_value,
                    'source': 'default',
                    'notes': [f'Field not available in {source_version}, using default']
                }
        
        return semantic_data
    
    def _convert_to_semantic(self, raw_value: Any, field_def: SemanticField, 
                           source_version: str, version_field_name: str) -> Dict[str, Any]:
        """Convert raw value to semantic representation"""
        
        if field_def.data_type == 'numeric':
            return self._convert_numeric_semantic(raw_value, field_def, source_version)
        elif field_def.data_type == 'alphanumeric':
            return self._convert_alphanumeric_semantic(raw_value, field_def, source_version)
        elif field_def.data_type == 'date':
            return self._convert_date_semantic(raw_value, field_def, source_version)
        elif field_def.data_type == 'time':
            return self._convert_time_semantic(raw_value, field_def, source_version)
        elif field_def.data_type == 'coordinate':
            return self._convert_coordinate_semantic(raw_value, field_def, source_version)
        elif field_def.data_type == 'measurement':
            return self._convert_measurement_semantic(raw_value, field_def, source_version)
        else:
            return {
                'value': raw_value,
                'source': source_version,
                'notes': ['Direct copy - unknown data type']
            }
    
    def _convert_numeric_semantic(self, raw_value: Any, field_def: SemanticField, 
                                source_version: str) -> Dict[str, Any]:
        """Convert numeric values to semantic representation"""
        try:
            if isinstance(raw_value, (int, float)):
                numeric_value = raw_value
            else:
                numeric_value = int(str(raw_value).strip())
            
            return {
                'value': numeric_value,
                'source': source_version,
                'data_type': 'numeric',
                'notes': []
            }
        except (ValueError, TypeError):
            return {
                'value': field_def.default_value,
                'source': 'default',
                'data_type': 'numeric',
                'notes': [f'Could not parse numeric value: {raw_value}']
            }
    
    def _convert_alphanumeric_semantic(self, raw_value: Any, field_def: SemanticField, 
                                     source_version: str) -> Dict[str, Any]:
        """Convert alphanumeric values to semantic representation"""
        clean_value = str(raw_value).strip()
        
        return {
            'value': clean_value,
            'source': source_version,
            'data_type': 'alphanumeric',
            'original_format': f'{source_version}_format',
            'notes': []
        }
    
    def _convert_date_semantic(self, raw_value: Any, field_def: SemanticField, 
                             source_version: str) -> Dict[str, Any]:
        """Convert date values to semantic representation"""
        
        if isinstance(raw_value, dict) and 'date_object' in raw_value:
            # Already parsed date
            return {
                'value': raw_value['date_object'],
                'iso_format': raw_value.get('iso_format'),
                'source': source_version,
                'data_type': 'date',
                'original_format': raw_value.get('original', ''),
                'notes': []
            }
        
        # Try to parse different date formats
        date_str = str(raw_value).strip()
        
        try:
            if len(date_str) == 8:
                if source_version in ['1966']:
                    # DDMMYYYY format
                    day = int(date_str[:2])
                    month = int(date_str[2:4])
                    year = int(date_str[4:])
                    date_obj = datetime(year, month, day)
                elif source_version in ['2020']:
                    # YYYYMMDD format
                    year = int(date_str[:4])
                    month = int(date_str[4:6])
                    day = int(date_str[6:])
                    date_obj = datetime(year, month, day)
                else:
                    raise ValueError("Unknown date format")
            elif len(date_str) == 6:
                # DDMMYY format (1979)
                day = int(date_str[:2])
                month = int(date_str[2:4])
                year_short = int(date_str[4:])
                year = 1900 + year_short if year_short > 50 else 2000 + year_short
                date_obj = datetime(year, month, day)
            else:
                raise ValueError("Unrecognized date format")
            
            return {
                'value': date_obj,
                'iso_format': date_obj.isoformat()[:10],
                'source': source_version,
                'data_type': 'date',
                'original_format': date_str,
                'notes': []
            }
            
        except (ValueError, TypeError) as e:
            return {
                'value': None,
                'source': 'error',
                'data_type': 'date',
                'original_format': date_str,
                'notes': [f'Could not parse date: {e}']
            }
    
    def _convert_coordinate_semantic(self, raw_value: Any, field_def: SemanticField, 
                                   source_version: str) -> Dict[str, Any]:
        """Convert coordinate values to semantic representation"""
        
        if isinstance(raw_value, dict) and 'decimal' in raw_value:
            # Already parsed coordinate
            return {
                'value': raw_value['decimal'],
                'source': source_version,
                'data_type': 'coordinate',
                'format': 'decimal',
                'original': raw_value.get('original', ''),
                'notes': []
            }
        
        if isinstance(raw_value, (int, float)):
            # Already decimal
            return {
                'value': float(raw_value),
                'source': source_version,
                'data_type': 'coordinate',
                'format': 'decimal',
                'notes': []
            }
        
        # Try to parse string coordinate
        coord_str = str(raw_value).strip()
        
        try:
            # Try decimal format first
            decimal_value = float(coord_str)
            return {
                'value': decimal_value,
                'source': source_version,
                'data_type': 'coordinate',
                'format': 'decimal',
                'original': coord_str,
                'notes': []
            }
        except ValueError:
            pass
        
        # Try degrees/minutes format
        if len(coord_str) >= 4 and coord_str[-1] in 'NSEW':
            try:
                direction = coord_str[-1]
                numbers = coord_str[:-1]
                
                if len(numbers) == 4:  # DDMM
                    degrees = int(numbers[:2])
                    minutes = int(numbers[2:])
                elif len(numbers) == 5:  # DDDMM
                    degrees = int(numbers[:3])
                    minutes = int(numbers[3:])
                else:
                    raise ValueError("Unknown coordinate format")
                
                decimal = degrees + (minutes / 60.0)
                if direction in 'SW':
                    decimal = -decimal
                
                return {
                    'value': decimal,
                    'source': source_version,
                    'data_type': 'coordinate',
                    'format': 'degrees_minutes',
                    'original': coord_str,
                    'degrees': degrees,
                    'minutes': minutes,
                    'direction': direction,
                    'notes': []
                }
            except (ValueError, IndexError):
                pass
        
        return {
            'value': 0.0,
            'source': 'default',
            'data_type': 'coordinate',
            'format': 'unknown',
            'original': coord_str,
            'notes': [f'Could not parse coordinate: {coord_str}']
        }
    
    def _convert_measurement_semantic(self, raw_value: Any, field_def: SemanticField, 
                                    source_version: str) -> Dict[str, Any]:
        """Convert measurement values to semantic representation"""
        
        if isinstance(raw_value, dict) and 'value' in raw_value:
            # Already parsed measurement
            return {
                'value': raw_value['value'],
                'unit': raw_value.get('unit', ''),
                'source': source_version,
                'data_type': 'measurement',
                'notes': []
            }
        
        try:
            if isinstance(raw_value, (int, float)):
                numeric_value = float(raw_value)
            else:
                numeric_value = float(str(raw_value).strip())
            
            # Determine unit based on field and version
            unit = self._determine_measurement_unit(field_def.name, source_version, numeric_value)
            
            return {
                'value': numeric_value,
                'unit': unit,
                'source': source_version,
                'data_type': 'measurement',
                'notes': []
            }
            
        except (ValueError, TypeError):
            return {
                'value': 0.0,
                'unit': '',
                'source': 'default',
                'data_type': 'measurement',
                'notes': [f'Could not parse measurement: {raw_value}']
            }
    
    def _determine_measurement_unit(self, field_name: str, version: str, value: float) -> str:
        """Determine the unit of measurement based on field, version, and value"""
        
        if field_name == 'wing_measurement':
            if version in ['2020'] or value > 50:
                return 'mm'
            else:
                return 'mm'  # Assume mm for all wing measurements
        
        elif field_name == 'weight_measurement':
            if version in ['1966', '1979']:
                return '0.1g'  # Traditional format uses 0.1g units
            elif version in ['2020']:
                return 'g'
            else:
                return 'g'
        
        elif field_name == 'bill_measurement':
            if version in ['1966', '1979']:
                return '0.1mm'  # Traditional format uses 0.1mm units
            elif version in ['2020']:
                return 'mm'
            else:
                return 'mm'
        
        return ''
    
    def convert_semantic_to_version(self, semantic_data: Dict[str, Any], 
                                  target_version: str) -> Dict[str, Any]:
        """Convert semantic data to target version format"""
        
        version_data = {}
        version_mapping = self.version_mappings.get(target_version, {})
        conversion_notes = []
        
        for semantic_field_name, semantic_value in semantic_data.items():
            target_field_name = version_mapping.get(semantic_field_name)
            
            if target_field_name:
                converted_value = self._convert_from_semantic(
                    semantic_value, semantic_field_name, target_version
                )
                version_data[target_field_name] = converted_value
                
                # Collect conversion notes
                if isinstance(semantic_value, dict) and 'notes' in semantic_value:
                    conversion_notes.extend(semantic_value['notes'])
        
        version_data['conversion_notes'] = conversion_notes
        return version_data
    
    def _convert_from_semantic(self, semantic_value: Dict[str, Any], 
                             semantic_field_name: str, target_version: str) -> Any:
        """Convert semantic value to target version format"""
        
        if not isinstance(semantic_value, dict) or 'value' not in semantic_value:
            return semantic_value
        
        value = semantic_value['value']
        data_type = semantic_value.get('data_type', '')
        
        # Handle None values
        if value is None:
            if semantic_field_name == 'species_identification':
                return '00000' if target_version in ['2020', '1979'] else 0
            elif semantic_field_name in ['geographic_latitude', 'geographic_longitude']:
                return 0.0
            elif semantic_field_name == 'capture_date':
                return '01011900' if target_version == '2020' else '01011900'
            else:
                return 0
        
        if semantic_field_name == 'species_identification':
            if target_version == '1966':
                # Remove leading zero for 1966
                return int(str(value).lstrip('0')) if str(value).startswith('0') else value
            else:
                # Add leading zero for other versions
                return f"{int(value):05d}"
        
        elif semantic_field_name == 'ring_identification':
            if target_version == '2020':
                # Ensure 3 letters + 5 digits format for 2020
                ring_str = str(value)
                letters = ''.join(c for c in ring_str if c.isalpha())[:2]
                digits = ''.join(c for c in ring_str if c.isdigit())[:5]
                # Pad letters to 3 characters and digits to 5
                letters = f"{letters}A"[:3]  # Add 'A' if needed, truncate to 3
                digits = digits.zfill(5)
                return f"{letters}{digits}"
            else:
                return value
        
        elif semantic_field_name == 'capture_date' and data_type == 'date':
            if value is None:
                return '01011900' if target_version == '2020' else '01011900'
            
            if target_version == '1966':
                return f"{value.day:02d}{value.month:02d}{value.year:04d}"
            elif target_version == '2020':
                return f"{value.year:04d}{value.month:02d}{value.day:02d}"
            elif target_version in ['1979']:
                return f"{value.day:02d}{value.month:02d}{value.year % 100:02d}"
        
        elif semantic_field_name in ['geographic_latitude', 'geographic_longitude']:
            if data_type == 'coordinate':
                if target_version in ['1966']:
                    # Convert to degrees/minutes format
                    return self._decimal_to_degrees_minutes(value, semantic_field_name)
                elif target_version in ['2020']:
                    # Keep as decimal
                    return float(value)
        
        elif data_type == 'measurement':
            unit = semantic_value.get('unit', '')
            if semantic_field_name == 'weight_measurement':
                if target_version in ['1966', '1979'] and unit == 'g':
                    # Convert grams to 0.1g units
                    return int(value * 10)
                elif target_version in ['2020'] and unit == '0.1g':
                    # Convert 0.1g units to grams
                    return float(value / 10)
        
        return value
    
    def _decimal_to_degrees_minutes(self, decimal_degrees: float, coord_type: str) -> str:
        """Convert decimal degrees to degrees/minutes format"""
        abs_decimal = abs(decimal_degrees)
        degrees = int(abs_decimal)
        minutes = int((abs_decimal - degrees) * 60)
        
        if coord_type == 'geographic_latitude':
            direction = 'N' if decimal_degrees >= 0 else 'S'
            return f"{degrees:02d}{minutes:02d}{direction}"
        else:  # longitude
            direction = 'E' if decimal_degrees >= 0 else 'W'
            return f"{degrees:03d}{minutes:02d}{direction}"