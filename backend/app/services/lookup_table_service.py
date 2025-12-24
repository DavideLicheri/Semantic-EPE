"""
Lookup Table Service for EURING Field Values
Manages predefined value lists for EURING fields with code-meaning mappings
"""
from typing import Dict, List, Optional, Any
from ..models.euring_models import EuringVersion
from ..services.skos_manager import SKOSManagerImpl

class LookupTableService:
    """Service for managing EURING field lookup tables"""
    
    def __init__(self):
        self.skos_manager = SKOSManagerImpl()
        self._lookup_cache: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
        self._custom_meanings: Dict[str, Dict[str, str]] = {}  # field_name -> {code: meaning}
        
        # Predefined lookup tables for common EURING fields
        self._predefined_lookups = {
            "scheme_code": {
                "name": "Ringing Scheme Codes",
                "description": "EURING ringing scheme identification codes",
                "values": [
                    {"code": "IAB", "meaning": "Italian Ringing Centre (ISPRA)"},
                    {"code": "DEH", "meaning": "German Ringing Centre (Helgoland)"},
                    {"code": "FRA", "meaning": "French Ringing Centre (MNHN)"},
                    {"code": "GBR", "meaning": "British Trust for Ornithology"},
                    {"code": "NLD", "meaning": "Dutch Ringing Centre (Vogeltrekstation)"},
                    {"code": "ESP", "meaning": "Spanish Ringing Centre (SEO/BirdLife)"},
                    {"code": "SWE", "meaning": "Swedish Ringing Centre (NRM)"},
                    {"code": "NOR", "meaning": "Norwegian Ringing Centre (NINA)"},
                    {"code": "FIN", "meaning": "Finnish Ringing Centre (Luomus)"},
                    {"code": "POL", "meaning": "Polish Ringing Centre (RING)"}
                ]
            },
            "primary_identification_method": {
                "name": "Primary Identification Methods",
                "description": "Methods used to identify birds",
                "values": [
                    {"code": "A0", "meaning": "Metal ring only"},
                    {"code": "B0", "meaning": "Metal ring + colour ring(s)"},
                    {"code": "C0", "meaning": "Metal ring + colour mark(s)"},
                    {"code": "D0", "meaning": "Metal ring + flag(s)"},
                    {"code": "E0", "meaning": "Metal ring + neck collar"},
                    {"code": "F0", "meaning": "Metal ring + wing tag(s)"},
                    {"code": "G0", "meaning": "Metal ring + leg streamer(s)"},
                    {"code": "H0", "meaning": "Metal ring + radio transmitter"},
                    {"code": "K0", "meaning": "Metal ring + satellite transmitter"},
                    {"code": "L0", "meaning": "Metal ring + light level geolocator"},
                    {"code": "R0", "meaning": "Metal ring + GPS logger"},
                    {"code": "T0", "meaning": "Metal ring + other electronic device"}
                ]
            },
            "metal_ring_information": {
                "name": "Metal Ring Information",
                "description": "Status and type of metal ring",
                "values": [
                    {"code": "0", "meaning": "Ring not mentioned"},
                    {"code": "1", "meaning": "Ring confirmed present"},
                    {"code": "2", "meaning": "Ring confirmed absent"},
                    {"code": "3", "meaning": "Ring present but not readable"},
                    {"code": "4", "meaning": "Ring present, partially readable"},
                    {"code": "5", "meaning": "Ring present, fully readable"},
                    {"code": "6", "meaning": "Ring replaced"},
                    {"code": "7", "meaning": "Ring removed"}
                ]
            },
            "metal_ring_info": {
                "name": "Metal Ring Information",
                "description": "Status and type of metal ring",
                "values": [
                    {"code": "0", "meaning": "Ring not mentioned"},
                    {"code": "1", "meaning": "Ring confirmed present"},
                    {"code": "2", "meaning": "Ring confirmed absent"},
                    {"code": "3", "meaning": "Ring present but not readable"},
                    {"code": "4", "meaning": "Ring present, partially readable"},
                    {"code": "5", "meaning": "Ring present, fully readable"},
                    {"code": "6", "meaning": "Ring replaced"},
                    {"code": "7", "meaning": "Ring removed"}
                ]
            },
            "other_marks": {
                "name": "Other Marks Information",
                "description": "Information about marks other than metal ring",
                "values": [
                    {"code": "ZZ", "meaning": "No other marks"},
                    {"code": "OM", "meaning": "Other marks present"},
                    {"code": "OP", "meaning": "Other marks present, partially readable"},
                    {"code": "OT", "meaning": "Other marks present, fully readable"},
                    {"code": "MM", "meaning": "Multiple marks present"},
                    {"code": "B-", "meaning": "Colour ring(s) - unspecified"},
                    {"code": "BB", "meaning": "Colour ring(s) - both legs"},
                    {"code": "BC", "meaning": "Colour ring(s) - left leg only"},
                    {"code": "BD", "meaning": "Colour ring(s) - right leg only"},
                    {"code": "BE", "meaning": "Colour ring(s) - multiple positions"},
                    {"code": "C-", "meaning": "Colour mark(s) - unspecified"},
                    {"code": "CB", "meaning": "Colour mark(s) - both legs"},
                    {"code": "CC", "meaning": "Colour mark(s) - left leg only"},
                    {"code": "CD", "meaning": "Colour mark(s) - right leg only"},
                    {"code": "CE", "meaning": "Colour mark(s) - multiple positions"}
                ]
            },
            "age_reported": {
                "name": "Age Classification",
                "description": "Age as mentioned by person who handled the bird",
                "values": [
                    {"code": "0", "meaning": "Age unknown"},
                    {"code": "1", "meaning": "Pullus (nestling)"},
                    {"code": "2", "meaning": "Fully grown, year of hatching unknown"},
                    {"code": "3", "meaning": "First-year (hatched this calendar year)"},
                    {"code": "4", "meaning": "After first-year, exact age unknown"},
                    {"code": "5", "meaning": "Second-year"},
                    {"code": "6", "meaning": "After second-year, exact age unknown"},
                    {"code": "7", "meaning": "Third-year"},
                    {"code": "8", "meaning": "After third-year, exact age unknown"},
                    {"code": "9", "meaning": "Fourth-year"},
                    {"code": "A", "meaning": "After fourth-year"},
                    {"code": "B", "meaning": "Fifth-year"},
                    {"code": "C", "meaning": "Sixth-year"},
                    {"code": "D", "meaning": "Seventh-year"},
                    {"code": "E", "meaning": "Eighth-year"},
                    {"code": "F", "meaning": "Ninth-year"},
                    {"code": "G", "meaning": "Tenth-year"},
                    {"code": "H", "meaning": "After tenth-year"}
                ]
            },
            "sex_reported": {
                "name": "Sex Classification",
                "description": "Sex as mentioned by person who handled the bird",
                "values": [
                    {"code": "M", "meaning": "Male"},
                    {"code": "F", "meaning": "Female"},
                    {"code": "U", "meaning": "Unknown/Undetermined"}
                ]
            },
            "manipulation": {
                "name": "Manipulation Codes",
                "description": "Type of manipulation performed on bird (priority order)",
                "values": [
                    {"code": "N", "meaning": "New - first capture and ringing"},
                    {"code": "H", "meaning": "Recapture in same season at same site"},
                    {"code": "K", "meaning": "Recapture in different season at same site"},
                    {"code": "C", "meaning": "Recapture at different site"},
                    {"code": "F", "meaning": "Recovery - bird found dead"},
                    {"code": "T", "meaning": "Recovery - bird found injured/sick"},
                    {"code": "M", "meaning": "Recovery - bird found and released"},
                    {"code": "R", "meaning": "Recovery - ring only found"},
                    {"code": "E", "meaning": "Recovery - bird escaped before examination"},
                    {"code": "P", "meaning": "Recovery - bird photographed/observed only"},
                    {"code": "U", "meaning": "Recovery - circumstances unknown"}
                ]
            },
            "moved_before": {
                "name": "Movement Before Encounter",
                "description": "Movement status before capture/recovery",
                "values": [
                    {"code": "0", "meaning": "Not moved"},
                    {"code": "2", "meaning": "Probably not moved"},
                    {"code": "4", "meaning": "Probably moved"},
                    {"code": "6", "meaning": "Certainly moved"},
                    {"code": "9", "meaning": "Unknown"}
                ]
            },
            "catching_method": {
                "name": "Catching Methods",
                "description": "Method used for catching the bird",
                "values": [
                    {"code": "A", "meaning": "Mist net"},
                    {"code": "B", "meaning": "Clap net"},
                    {"code": "C", "meaning": "Cannon net"},
                    {"code": "D", "meaning": "Drop trap"},
                    {"code": "F", "meaning": "Funnel trap"},
                    {"code": "G", "meaning": "Ground trap"},
                    {"code": "H", "meaning": "Hand capture"},
                    {"code": "L", "meaning": "Ladder trap"},
                    {"code": "M", "meaning": "Multiple methods"},
                    {"code": "N", "meaning": "Nest trap"},
                    {"code": "O", "meaning": "Other method"},
                    {"code": "P", "meaning": "Potter trap"},
                    {"code": "R", "meaning": "Rocket net"},
                    {"code": "S", "meaning": "Spring trap"},
                    {"code": "T", "meaning": "Tape lure"},
                    {"code": "U", "meaning": "Unknown method"},
                    {"code": "V", "meaning": "Vertical net"},
                    {"code": "W", "meaning": "Walk-in trap"},
                    {"code": "Z", "meaning": "Other specified method"},
                    {"code": "-", "meaning": "Not applicable"}
                ]
            },
            "lures_used": {
                "name": "Lures Used",
                "description": "Type of lure used in capture",
                "values": [
                    {"code": "A", "meaning": "Audio playback"},
                    {"code": "B", "meaning": "Bait (food)"},
                    {"code": "C", "meaning": "Call imitation"},
                    {"code": "D", "meaning": "Decoy bird"},
                    {"code": "E", "meaning": "Electronic caller"},
                    {"code": "F", "meaning": "Flash/light"},
                    {"code": "G", "meaning": "Ground bait"},
                    {"code": "H", "meaning": "Hand feeding"},
                    {"code": "M", "meaning": "Multiple lures"},
                    {"code": "N", "meaning": "No lure used"},
                    {"code": "U", "meaning": "Unknown lure"},
                    {"code": "-", "meaning": "Not applicable"}
                ]
            },
            "verification_metal_ring": {
                "name": "Ring Verification Status",
                "description": "Whether ring was verified by scheme",
                "values": [
                    {"code": "0", "meaning": "Not verified"},
                    {"code": "1", "meaning": "Verified by scheme"},
                    {"code": "9", "meaning": "Verification status unknown"}
                ]
            }
        }
    
    async def get_field_lookup_table(self, field_name: str, version: str) -> Optional[Dict[str, Any]]:
        """Get lookup table for a specific field in a version"""
        try:
            # Load version data to get valid_values first (this includes any updates)
            await self.skos_manager.load_version_model()
            version_obj = await self.skos_manager.get_version_by_id(f"euring_{version}")
            
            if not version_obj:
                return None
            
            # Find the field
            field_def = None
            for field in version_obj.field_definitions:
                if field.name == field_name:
                    field_def = field
                    break
            
            # If field exists in version data and has valid_values, use that (updated data)
            if field_def and field_def.valid_values:
                # Create lookup table from valid_values
                lookup_table = {
                    "name": f"{field_name.replace('_', ' ').title()} Values",
                    "description": field_def.description or f"Valid values for {field_name}",
                    "values": []
                }
                
                # Convert valid_values to code-meaning pairs using custom meanings if available
                for value in field_def.valid_values:
                    lookup_table["values"].append({
                        "code": value,
                        "meaning": self._get_meaning_for_value(field_name, value, version)
                    })
                
                return lookup_table
            
            # Fallback to predefined lookup if no field data exists
            if field_name in self._predefined_lookups:
                return self._predefined_lookups[field_name]
            
            return None
            
        except Exception as e:
            print(f"Error getting lookup table for {field_name}: {e}")
            return None
    
    def _get_meaning_for_value(self, field_name: str, value: str, version: str = None) -> str:
        """Get human-readable meaning for a field value"""
        # Check for custom meanings first
        if version:
            cache_key = f"{field_name}_{version}"
            if cache_key in self._custom_meanings and value in self._custom_meanings[cache_key]:
                custom_meaning = self._custom_meanings[cache_key][value]
                print(f"🔍 Using custom meaning for {cache_key}[{value}]: {custom_meaning}")
                return custom_meaning
        
        # Fallback to generic descriptions
        if value in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return f"Code {value}"
        elif value in ["---", "...", "------", "--"]:
            return "Empty/Not applicable"
        elif value in ["+", "-"]:
            return "Present" if value == "+" else "Absent"
        else:
            return f"Value: {value}"
    
    async def get_all_field_lookups(self, version: str) -> Dict[str, Dict[str, Any]]:
        """Get all available lookup tables for a version"""
        lookups = {}
        
        try:
            # Load version data
            await self.skos_manager.load_version_model()
            version_obj = await self.skos_manager.get_version_by_id(f"euring_{version}")
            
            if not version_obj:
                return lookups
            
            # Check each field for lookup tables
            for field in version_obj.field_definitions:
                lookup = await self.get_field_lookup_table(field.name, version)
                if lookup:
                    lookups[field.name] = lookup
            
            return lookups
            
        except Exception as e:
            print(f"Error getting all lookups for version {version}: {e}")
            return lookups
    
    async def update_field_lookup_table(self, field_name: str, version: str, lookup_data: Dict[str, Any]) -> bool:
        """Update lookup table for a field"""
        try:
            # Load version data
            await self.skos_manager.load_version_model()
            version_obj = await self.skos_manager.get_version_by_id(f"euring_{version}")
            
            if not version_obj:
                return False
            
            # Find the field
            field_def = None
            for field in version_obj.field_definitions:
                if field.name == field_name:
                    field_def = field
                    break
            
            if not field_def:
                return False
            
            # Update valid_values from lookup data
            if "values" in lookup_data:
                # Save codes to valid_values
                field_def.valid_values = [item["code"] for item in lookup_data["values"]]
                
                # Save custom meanings to cache
                custom_meanings = {}
                for item in lookup_data["values"]:
                    if "meaning" in item:
                        custom_meanings[item["code"]] = item["meaning"]
                
                # Store custom meanings with field_name as key
                cache_key = f"{field_name}_{version}"
                self._custom_meanings[cache_key] = custom_meanings
                
                print(f"💾 Saved custom meanings for {cache_key}: {custom_meanings}")
                
                # Save the updated version
                await self.skos_manager.update_version(version_obj)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating lookup table for {field_name}: {e}")
            return False