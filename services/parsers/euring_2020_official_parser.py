"""
EURING 2020 Official Parser - Based on SKOS Thesaurus
Handles the official EURING 2020 format with precise field definitions
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from ...models.euring_models import EuringVersion


class Euring2020OfficialParser:
    """Parser for official EURING 2020 format based on SKOS thesaurus"""
    
    def __init__(self):
        self.field_names = [
            'identification_number',
            'ringing_scheme', 
            'primary_identification_method',
            'metal_ring_information',
            'other_marks_information',
            'species_as_mentioned_by_finder',
            'species_as_mentioned_by_scheme',
            'age_mentioned_by_the_person',
            'sex_mentioned_by_the_person',
            'sex_concluded_by_the_scheme',
            'manipulated',
            'moved_before',
            'catching_method',
            'catching_lures',
            'verification_of_the_metal_ring'
        ]
        
        # Valid values based on SKOS thesaurus
        self.valid_values = {
            'ringing_scheme': ['IAB', 'DEH'],
            'primary_identification_method': ['A0', 'B0', 'C0', 'D0', 'E0', 'F0', 'G0', 'H0', 'K0', 'L0', 'R0', 'T0'],
            'metal_ring_information': ['0', '1', '2', '3', '4', '5', '6', '7'],
            'other_marks_information': ['ZZ', 'OM', 'OP', 'OT', 'MM', 'B-', 'BB', 'BC', 'BD', 'BE', 'C-', 'CB', 'CC', 'CD', 'CE'],
            'age_mentioned_by_the_person': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
            'sex_mentioned_by_the_person': ['M', 'F', 'U'],
            'sex_concluded_by_the_scheme': ['M', 'F', 'U'],
            'manipulated': ['N', 'H', 'K', 'C', 'F', 'T', 'M', 'R', 'E', 'P', 'U'],
            'moved_before': ['0', '2', '4', '6', '9'],
            'catching_method': ['A', 'B', 'C', 'D', 'F', 'G', 'H', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Z', '-'],
            'catching_lures': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'M', 'N', 'U', '-'],
            'verification_of_the_metal_ring': ['0', '1', '9']
        }
        
        # Priority order for manipulation codes (lower = higher priority)
        self.manipulation_priority = {
            'H': 1,  # hand reared
            'K': 2,  # fledging provoked
            'C': 3,  # captive >24h
            'F': 4,  # transported from
            'T': 5,  # transported to
            'M': 6,  # manipulated
            'R': 7,  # ringing accident
            'E': 8,  # euthanised
            'P': 9,  # poor condition
            'N': 10, # normal
            'U': 11  # unknown
        }
    
    def parse(self, euring_string: str) -> Dict[str, Any]:
        """Parse official EURING 2020 string into structured data"""
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Split by pipe separator
        fields = euring_string.strip().split('|')
        
        if len(fields) != 15:
            raise ValueError(f"Official EURING 2020 format requires exactly 15 fields, got {len(fields)}")
        
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
        """Parse individual field based on SKOS definitions"""
        
        if field_name == 'identification_number':
            return self._parse_identification_number(value)
            
        elif field_name == 'ringing_scheme':
            return self._parse_ringing_scheme(value)
            
        elif field_name == 'primary_identification_method':
            return self._parse_primary_identification_method(value)
            
        elif field_name == 'metal_ring_information':
            return self._parse_metal_ring_information(value)
            
        elif field_name == 'other_marks_information':
            return self._parse_other_marks_information(value)
            
        elif field_name in ['species_as_mentioned_by_finder', 'species_as_mentioned_by_scheme']:
            return self._parse_species_code(field_name, value)
            
        elif field_name == 'age_mentioned_by_the_person':
            return self._parse_age_code(value)
            
        elif field_name in ['sex_mentioned_by_the_person', 'sex_concluded_by_the_scheme']:
            return self._parse_sex_code(field_name, value)
            
        elif field_name == 'manipulated':
            return self._parse_manipulation_code(value)
            
        elif field_name == 'moved_before':
            return self._parse_moved_before(value)
            
        elif field_name == 'catching_method':
            return self._parse_catching_method(value)
            
        elif field_name == 'catching_lures':
            return self._parse_catching_lures(value)
            
        elif field_name == 'verification_of_the_metal_ring':
            return self._parse_ring_verification(value)
        
        return value
    
    def _parse_identification_number(self, value: str) -> Dict[str, Any]:
        """Parse identification number (ring number)"""
        if len(value) != 10:
            raise ValueError(f"Identification number must be exactly 10 characters, got {len(value)}")
        
        # Check for valid characters (letters, numbers, dots, dashes)
        if not re.match(r'^[A-Z0-9\.\-]{10}$', value):
            raise ValueError(f"Identification number contains invalid characters: {value}")
        
        # Analyze the structure
        has_dots = '.' in value
        has_dashes = '-' in value
        letters = ''.join(c for c in value if c.isalpha())
        numbers = ''.join(c for c in value if c.isdigit())
        
        return {
            'value': value,
            'letters': letters,
            'numbers': numbers,
            'has_padding': has_dots,
            'has_unknown_parts': has_dashes,
            'is_complete': not has_dashes,
            'notes': self._get_ring_number_notes(value)
        }
    
    def _get_ring_number_notes(self, value: str) -> List[str]:
        """Get notes about ring number format"""
        notes = []
        if '.' in value:
            notes.append("Padded with dots (fewer than 10 original characters)")
        if '-' in value:
            notes.append("Contains unknown/worn parts (marked with dashes)")
        if value.startswith('NMR'):
            notes.append("Not-metal-ring number (bird not metal-ringed on first capture)")
        return notes
    
    def _parse_ringing_scheme(self, value: str) -> Dict[str, Any]:
        """Parse ringing scheme code"""
        if len(value) != 3:
            raise ValueError(f"Ringing scheme must be 3 characters, got {len(value)}")
        
        if not value.isalpha() or not value.isupper():
            raise ValueError(f"Ringing scheme must be 3 uppercase letters, got {value}")
        
        # Check if it's a valid scheme (allow unknown schemes but warn)
        if value not in self.valid_values['ringing_scheme']:
            # Don't raise error, just mark as unknown
            pass
        
        # Map to known schemes
        scheme_names = {
            'IAB': 'Bologna Ozzano (BO) Ringing Centre / Italian Ringing Centre',
            'DEH': 'Hiddensee Ringing Centre'
        }
        
        return {
            'code': value,
            'name': scheme_names.get(value, 'Unknown scheme'),
            'is_known': value in scheme_names
        }
    
    def _parse_primary_identification_method(self, value: str) -> Dict[str, Any]:
        """Parse primary identification method"""
        if len(value) != 2:
            raise ValueError(f"Primary identification method must be 2 characters, got {len(value)}")
        
        if not (value[0].isalpha() and value[1].isdigit()):
            raise ValueError(f"Primary identification method must be letter + digit, got {value}")
        
        # Map to method descriptions
        method_descriptions = {
            'A0': 'Metal ring',
            'B0': 'Coloured or numbered leg ring(s)',
            'C0': 'Coloured or numbered neck ring(s)',
            'D0': 'Wing tags',
            'E0': 'Radio tracking device',
            'F0': 'Satellite tracking device',
            'G0': 'Transponder',
            'H0': 'Nasal mark(s)',
            'K0': 'GPS loggers',
            'L0': 'Geolocator loggers (recording daylight)',
            'R0': 'Flight feather(s) stamped with a number',
            'T0': 'Body or wing painting or bleaching'
        }
        
        return {
            'code': value,
            'description': method_descriptions.get(value, 'Unknown method'),
            'is_metal_ring': value == 'A0',
            'is_electronic': value in ['E0', 'F0', 'G0', 'K0', 'L0']
        }
    
    def _parse_metal_ring_information(self, value: str) -> Dict[str, Any]:
        """Parse metal ring information"""
        if not value.isdigit() or len(value) != 1:
            raise ValueError(f"Metal ring information must be single digit, got {value}")
        
        if value not in self.valid_values['metal_ring_information']:
            raise ValueError(f"Metal ring information must be 0-7, got {value}")
        
        # Map to descriptions
        descriptions = {
            '0': 'Metal ring is NOT PRESENT',
            '1': 'Metal ring ADDED on tarsus or above (position unknown)',
            '2': 'Metal ring ADDED on tarsus',
            '3': 'Metal ring ADDED above tarsus',
            '4': 'Metal ring is ALREADY PRESENT',
            '5': 'Metal ring CHANGED',
            '6': 'Metal ring REMOVED (bird released alive)',
            '7': 'Metal ring ADDED WHERE A METAL RING WAS ALREADY PRESENT'
        }
        
        return {
            'code': int(value),
            'description': descriptions[value],
            'ring_present': value in ['4', '5', '7'],
            'ring_added': value in ['1', '2', '3', '7'],
            'ring_removed': value == '6'
        }
    
    def _parse_other_marks_information(self, value: str) -> Dict[str, Any]:
        """Parse other marks information"""
        if len(value) != 2:
            raise ValueError(f"Other marks information must be 2 characters, got {len(value)}")
        
        # Special cases
        special_cases = {
            'ZZ': 'No other marks present or not known to be present',
            'OM': 'Other mark(s) present',
            'OP': 'Other permanent mark(s) present',
            'OT': 'Other temporary mark(s) present',
            'MM': 'More than one mark added/present/removed'
        }
        
        if value in special_cases:
            return {
                'code': value,
                'description': special_cases[value],
                'is_special_case': True,
                'mark_type': None,
                'mark_status': None
            }
        
        # Regular format: first char = mark type, second = status
        mark_types = {
            'B': 'Coloured or numbered leg ring(s) or flags',
            'C': 'Coloured or numbered neck-ring(s)',
            'D': 'Coloured or numbered wing tag(s)',
            'E': 'Radio-tracking device',
            'F': 'Satellite-tracking device',
            'G': 'Transponder',
            'H': 'Nasal mark(s)',
            'K': 'GPS logger',
            'L': 'Geolocator logger (recording daylight)',
            'R': 'Flight feathers stamped with the ring number',
            'S': 'Tape on the ring',
            'T': 'Dye mark (some part of plumage dyed, painted or bleached)'
        }
        
        mark_statuses = {
            '-': 'Unknown',
            'B': 'Mark added',
            'C': 'Mark already present',
            'D': 'Mark removed',
            'E': 'Mark changed'
        }
        
        mark_type = value[0]
        mark_status = value[1]
        
        return {
            'code': value,
            'description': f"{mark_types.get(mark_type, 'Unknown mark')} - {mark_statuses.get(mark_status, 'Unknown status')}",
            'is_special_case': False,
            'mark_type': mark_types.get(mark_type),
            'mark_status': mark_statuses.get(mark_status)
        }
    
    def _parse_species_code(self, field_name: str, value: str) -> Dict[str, Any]:
        """Parse species code"""
        if len(value) != 5 or not value.isdigit():
            raise ValueError(f"Species code must be exactly 5 digits, got {value}")
        
        species_code = int(value)
        
        return {
            'code': species_code,
            'original': value,
            'is_finder_identification': 'finder' in field_name,
            'is_scheme_verification': 'scheme' in field_name,
            'notes': ['Based on Voous numbering system', 'Updated to IOC taxonomy']
        }
    
    def _parse_age_code(self, value: str) -> Dict[str, Any]:
        """Parse age code"""
        if len(value) != 1:
            raise ValueError(f"Age code must be single character, got {len(value)}")
        
        if value not in self.valid_values['age_mentioned_by_the_person']:
            raise ValueError(f"Age code must be 0-9 or A-H, got {value}")
        
        # Determine if it's numeric or alphabetic
        is_numeric = value.isdigit()
        
        age_descriptions = {
            '0': 'Age unknown, not recorded',
            '1': 'Pullus (nestling or chick, unable to fly freely, still dependent on parents)',
            '2': 'Fully grown, year of hatching unknown',
            '3': 'First-year (hatched during the calendar year of ringing)',
            '4': 'Fully grown, hatched before this calendar year, exact year unknown',
            '5': 'Second-year (hatched during the calendar year before ringing)',
            '6': 'Fully grown, hatched before the calendar year before ringing, exact year unknown',
            '7': 'Third-year',
            '8': 'Fully grown, at least third-year, exact year unknown',
            '9': 'Fourth-year or older',
            'A': 'Fifth-year',
            'B': 'Sixth-year',
            'C': 'Seventh-year',
            'D': 'Eighth-year',
            'E': 'Ninth-year',
            'F': 'Tenth-year',
            'G': 'Eleventh-year',
            'H': 'Twelfth-year or older'
        }
        
        return {
            'code': value,
            'description': age_descriptions.get(value, 'Unknown age code'),
            'is_numeric': is_numeric,
            'is_exact_year': is_numeric and int(value) % 2 == 1 if is_numeric else False,
            'notes': ['Statement about plumage, not actual age in years', 'Changes overnight Dec 31-Jan 1']
        }
    
    def _parse_sex_code(self, field_name: str, value: str) -> Dict[str, Any]:
        """Parse sex code"""
        if value not in self.valid_values['sex_mentioned_by_the_person']:
            raise ValueError(f"Sex code must be M, F, or U, got {value}")
        
        sex_descriptions = {
            'M': 'Male',
            'F': 'Female',
            'U': 'Unknown'
        }
        
        return {
            'code': value,
            'description': sex_descriptions[value],
            'is_determined': value != 'U',
            'is_person_determination': 'person' in field_name,
            'is_scheme_verification': 'scheme' in field_name
        }
    
    def _parse_manipulation_code(self, value: str) -> Dict[str, Any]:
        """Parse manipulation code with priority"""
        if value not in self.valid_values['manipulated']:
            raise ValueError(f"Manipulation code must be one of {self.valid_values['manipulated']}, got {value}")
        
        manipulation_descriptions = {
            'N': 'Normal, not manipulated bird',
            'H': 'Hand reared',
            'K': 'Fledging provoked',
            'C': 'Captive for more than 24 hours',
            'F': 'Transported (more than 10 km) FROM co-ordinates coded',
            'T': 'Transported (more than 10 km) TO co-ordinates coded',
            'M': 'Manipulated (injection, biopsy, radio- or satellite telemetry etc.)',
            'R': 'Ringing accident',
            'E': 'Euthanised; bird humanely destroyed',
            'P': 'Poor condition when caught',
            'U': 'Uncoded or unknown if manipulated bird or not'
        }
        
        return {
            'code': value,
            'description': manipulation_descriptions[value],
            'priority_order': self.manipulation_priority[value],
            'is_normal': value == 'N',
            'is_manipulated': value not in ['N', 'U']
        }
    
    def _parse_moved_before(self, value: str) -> Dict[str, Any]:
        """Parse moved before code"""
        if value not in self.valid_values['moved_before']:
            raise ValueError(f"Moved before code must be 0, 2, 4, 6, or 9, got {value}")
        
        moved_descriptions = {
            '0': 'Not moved (excluding short movements on foot from catching place to ringing station)',
            '2': 'Moved unintentionally by man or other agency',
            '4': 'Moved intentionally by man',
            '6': 'Moved by water (e.g. found on shoreline)',
            '9': 'Uncoded or unknown if moved or not'
        }
        
        return {
            'code': int(value),
            'description': moved_descriptions[value],
            'was_moved': value != '0',
            'movement_type': 'none' if value == '0' else 'unintentional' if value == '2' else 'intentional' if value == '4' else 'water' if value == '6' else 'unknown'
        }
    
    def _parse_catching_method(self, value: str) -> Dict[str, Any]:
        """Parse catching method"""
        if value not in self.valid_values['catching_method']:
            raise ValueError(f"Invalid catching method code: {value}")
        
        method_descriptions = {
            'A': 'Actively triggered trap (by ringer)',
            'B': 'Trap automatically triggered by bird',
            'C': 'Cannon net or rocket net',
            'D': 'Dazzling',
            'F': 'Caught in flight by anything other than a static mist net (e.g. flicked)',
            'G': 'Nets put just under the water\'s surface and lifted up as waterfowl swim over it',
            'H': 'By hand (with or without hook, noose, etc.)',
            'L': 'Clap net',
            'M': 'Mist net',
            'N': 'On nest (any method)',
            'O': 'Any other system',
            'P': 'Phut net',
            'R': 'Round up whilst flightless',
            'S': 'Bal-chatri or other snare device',
            'T': 'Helgoland trap or duck decoy',
            'U': 'Dutch net for Pluvialis apricaria',
            'V': 'Roosting in cavity',
            'W': 'Passive walk-in / maze trap',
            'Z': 'Unknown',
            '-': 'Not applicable (found dead/shot, no catching)'
        }
        
        return {
            'code': value,
            'description': method_descriptions[value],
            'is_active_method': value in ['A', 'C', 'D', 'F', 'H', 'L', 'P', 'R', 'S'],
            'is_passive_method': value in ['B', 'M', 'T', 'V', 'W'],
            'not_applicable': value == '-'
        }
    
    def _parse_catching_lures(self, value: str) -> Dict[str, Any]:
        """Parse catching lures"""
        if value not in self.valid_values['catching_lures']:
            raise ValueError(f"Invalid catching lures code: {value}")
        
        lure_descriptions = {
            'A': 'Food',
            'B': 'Water',
            'C': 'Light',
            'D': 'Decoy birds (alive)',
            'E': 'Decoy birds (stuffed specimens or artificial decoy)',
            'F': 'Playback call (same species)',
            'G': 'Playback call (other species)',
            'H': 'Sound from mechanical whistle',
            'M': 'More than one lure used',
            'N': 'Definitely no lure used',
            'U': 'Unknown or not coded',
            '-': 'Not applicable (found dead/shot, no catching lure)'
        }
        
        return {
            'code': value,
            'description': lure_descriptions[value],
            'lure_used': value not in ['N', 'U', '-'],
            'multiple_lures': value == 'M',
            'not_applicable': value == '-'
        }
    
    def _parse_ring_verification(self, value: str) -> Dict[str, Any]:
        """Parse ring verification status"""
        if value not in self.valid_values['verification_of_the_metal_ring']:
            raise ValueError(f"Ring verification must be 0, 1, or 9, got {value}")
        
        verification_descriptions = {
            '0': 'Ring NOT verified by scheme',
            '1': 'Ring verified by scheme',
            '9': 'Unknown if ring verified by scheme'
        }
        
        return {
            'code': int(value),
            'description': verification_descriptions[value],
            'is_verified': value == '1',
            'verification_methods': ['ring sent', 'photograph', 'photocopy', 'rubbing', 'carbon copy'] if value == '1' else []
        }
    
    def validate(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Validate parsed data according to SKOS rules"""
        errors = []
        
        # Cross-field validation
        if 'primary_identification_method' in parsed_data and 'metal_ring_information' in parsed_data:
            pim = parsed_data['primary_identification_method']
            mri = parsed_data['metal_ring_information']
            
            if isinstance(pim, dict) and isinstance(mri, dict):
                # If primary method is metal ring, metal ring should be present
                if pim.get('is_metal_ring') and mri.get('code') == 0:
                    errors.append("Primary identification is metal ring but metal ring information indicates not present")
        
        # Species consistency check (only warn if very different)
        if 'species_as_mentioned_by_finder' in parsed_data and 'species_as_mentioned_by_scheme' in parsed_data:
            finder_species = parsed_data['species_as_mentioned_by_finder']
            scheme_species = parsed_data['species_as_mentioned_by_scheme']
            
            if isinstance(finder_species, dict) and isinstance(scheme_species, dict):
                finder_code = finder_species.get('code')
                scheme_code = scheme_species.get('code')
                if finder_code and scheme_code and abs(finder_code - scheme_code) > 1000:
                    errors.append("Species identification significantly differs between finder and scheme")
        
        # Sex consistency check (only if scheme explicitly disagrees)
        if 'sex_mentioned_by_the_person' in parsed_data and 'sex_concluded_by_the_scheme' in parsed_data:
            person_sex = parsed_data['sex_mentioned_by_the_person']
            scheme_sex = parsed_data['sex_concluded_by_the_scheme']
            
            if isinstance(person_sex, dict) and isinstance(scheme_sex, dict):
                person_code = person_sex.get('code')
                scheme_code = scheme_sex.get('code')
                # Only flag if scheme explicitly contradicts (not if scheme says unknown)
                if (person_code in ['M', 'F'] and scheme_code in ['M', 'F'] and 
                    person_code != scheme_code):
                    errors.append("Sex determination explicitly contradicted by scheme")
        
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
        parsed_data['euring_version'] = '2020_official'
        parsed_data['original_string'] = euring_string
        parsed_data['skos_based'] = True
        
        return parsed_data