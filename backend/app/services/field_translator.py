"""
Field Translation Service
Translates EURING field names and values based on language preference
"""
from typing import Dict, Any, Optional


class FieldTranslator:
    """Service for translating EURING field names and values"""
    
    def __init__(self):
        self.field_translations = {
            'en': {
                # Observatory and identification
                'Osservatorio': 'Observatory',
                'Metodo di identificazione primaria': 'Primary identification method',
                'Anello (10 caratteri)': 'Ring (10 characters)',
                'Anello': 'Ring',
                'Verifica dell\'anello metallico': 'Metal ring verification',
                'Informazioni sull\'anello metallico': 'Metal ring information',
                'Altri marcaggi': 'Other markings',
                'Identificatore codice Euring': 'Euring code identifier',
                
                # Species
                'Specie riportata': 'Reported species',
                'Specie conclusa': 'Concluded species',
                
                # Demographics
                'Sesso riportato': 'Reported sex',
                'Sesso concluso': 'Concluded sex',
                'Età riportata': 'Reported age',
                'Età conclusa': 'Concluded age',
                'Status': 'Status',
                'Dimensione della covata': 'Brood size',
                'Età dei pulcini': 'Chick age',
                'Accuratezza età dei pulcini': 'Chick age accuracy',
                
                # Temporal
                'Giorno': 'Day',
                'Mese': 'Month',
                'Anno': 'Year',
                'Accuratezza data': 'Date accuracy',
                'Ora': 'Time',
                'Tempo trascorso': 'Elapsed time',
                
                # Spatial
                'Codice area Euring': 'Euring area code',
                'Latitudine': 'Latitude',
                'Longitudine': 'Longitude',
                'Accuratezza coordinate': 'Coordinate accuracy',
                
                # Methodology
                'Manipolazione': 'Manipulation',
                'Traslocazione prima della cattura': 'Translocation before capture',
                'Metodo di cattura': 'Capture method',
                'Richiamo': 'Lure',
                'Condizioni': 'Conditions',
                'Circostanze': 'Circumstances',
                'Circostanze presunte': 'Presumed circumstances',
                'Distanza': 'Distance',
                'Direzione': 'Direction',
                
                # System fields
                'version': 'version',
                'original_string': 'original_string',
                'note': 'note',
                'epe_error': 'epe_error',
            }
        }
        
        self.value_translations = {
            'en': {
                # Sex values
                'M (Maschio)': 'M (Male)',
                'F (Femmina)': 'F (Female)',
                'U (Sconosciuto)': 'U (Unknown)',
                
                # Age values
                '1 (Pullus)': '1 (Pullus)',
                '2 (Primo anno)': '2 (First year)',
                '3 (Secondo anno)': '3 (Second year)',
                '4 (Terzo anno)': '4 (Third year)',
                '5 (Quarto anno)': '5 (Fourth year)',
                '6 (Quinto anno)': '6 (Fifth year)',
                '7 (Sesto anno)': '7 (Sixth year)',
                '8 (Settimo anno)': '8 (Seventh year)',
                '9 (Ottavo anno o più)': '9 (Eighth year or older)',
                
                # Status values
                '1 (Normale)': '1 (Normal)',
                '2 (Ferito)': '2 (Injured)',
                '3 (Morto)': '3 (Dead)',
                
                # Manipulation values
                '0 (Non manipolato)': '0 (Not handled)',
                '1 (Manipolato)': '1 (Handled)',
                
                # Ring verification
                '0 (Non pervenuto)': '0 (Not received)',
                '1 (Pervenuto)': '1 (Received)',
                
                # Yes/No values
                '0 (No)': '0 (No)',
                '1 (Sì)': '1 (Yes)',
                
                # Accuracy values
                '0 (Esatta)': '0 (Exact)',
                '1 (Approssimativa)': '1 (Approximate)',
                '2 (Approssimativa)': '2 (Approximate)',
                '1 (Esatta)': '1 (Exact)',
                '0 (Non specificata)': '0 (Not specified)',
                
                # Not specified values
                '00 (Non specificato)': '00 (Not specified)',
                '0000 (Non specificato)': '0000 (Not specified)',
                '0000 (Non specificata)': '0000 (Not specified)',
                '0 (Non specificato)': '0 (Not specified)',
                
                # System messages
                'Detailed parsing for euring_2020 not yet implemented': 'Detailed parsing for EURING 2020 not yet implemented',
                'EPE parsing failed, using basic parsing for euring_2020': 'EPE parsing failed, using basic parsing for EURING 2020',
                'Detailed parsing for euring_1966 not yet implemented': 'Detailed parsing for EURING 1966 not yet implemented',
                'Detailed parsing for euring_1979 not yet implemented': 'Detailed parsing for EURING 1979 not yet implemented',
                'Detailed parsing for euring_2020_official not yet implemented': 'Detailed parsing for EURING 2020 official not yet implemented',
            }
        }
    
    def translate_field_name(self, field_name: str, language: str = 'it') -> str:
        """
        Translate a field name to the specified language
        
        Args:
            field_name: Original field name (usually in Italian)
            language: Target language ('it' or 'en')
            
        Returns:
            Translated field name or original if translation not found
        """
        if language == 'it' or language not in self.field_translations:
            return field_name
            
        return self.field_translations[language].get(field_name, field_name)
    
    def translate_field_value(self, field_name: str, field_value: Any, language: str = 'it') -> str:
        """
        Translate a field value based on field name and language
        
        Args:
            field_name: Name of the field
            field_value: Value to translate
            language: Target language ('it' or 'en')
            
        Returns:
            Translated value or formatted original value
        """
        if field_value is None or field_value == '':
            return '-'
            
        str_value = str(field_value).strip()
        if not str_value:
            return '-'
        
        # Handle special formatting based on field type
        formatted_value = self._format_field_value(field_name, str_value, language)
        
        # Apply translations if available
        if language in self.value_translations:
            return self.value_translations[language].get(formatted_value, formatted_value)
        
        return formatted_value
    
    def _format_field_value(self, field_name: str, value: str, language: str) -> str:
        """Format field values with appropriate interpretations"""
        
        # Sex fields
        if field_name in ['Sesso riportato', 'Sesso concluso', 'Reported sex', 'Concluded sex']:
            if value == 'M':
                return 'M (Maschio)' if language == 'it' else 'M (Male)'
            elif value == 'F':
                return 'F (Femmina)' if language == 'it' else 'F (Female)'
            elif value == 'U':
                return 'U (Sconosciuto)' if language == 'it' else 'U (Unknown)'
        
        # Age fields - add interpretations for common age codes
        elif field_name in ['Età riportata', 'Età conclusa', 'Reported age', 'Concluded age']:
            if value == '1':
                return '1 (Pullus)' if language == 'it' else '1 (Pullus)'
            elif value == '2':
                return '2 (Primo anno)' if language == 'it' else '2 (First year)'
            elif value == '3':
                return '3 (Secondo anno)' if language == 'it' else '3 (Second year)'
            elif value == '4':
                return '4 (Terzo anno)' if language == 'it' else '4 (Third year)'
            elif value == '5':
                return '5 (Quarto anno)' if language == 'it' else '5 (Fourth year)'
            elif value == '6':
                return '6 (Quinto anno)' if language == 'it' else '6 (Fifth year)'
            elif value == '7':
                return '7 (Sesto anno)' if language == 'it' else '7 (Sixth year)'
            elif value == '8':
                return '8 (Settimo anno)' if language == 'it' else '8 (Seventh year)'
            elif value == '9':
                return '9 (Ottavo anno o più)' if language == 'it' else '9 (Eighth year or older)'
            elif value == '0':
                return '0 (Non specificato)' if language == 'it' else '0 (Not specified)'
        
        # Status field
        elif field_name in ['Status']:
            if value == '0':
                return '0 (Non specificato)' if language == 'it' else '0 (Not specified)'
            elif value == '1':
                return '1 (Normale)' if language == 'it' else '1 (Normal)'
            elif value == '2':
                return '2 (Ferito)' if language == 'it' else '2 (Injured)'
            elif value == '3':
                return '3 (Morto)' if language == 'it' else '3 (Dead)'
        
        # Ring verification
        elif field_name in ['Verifica dell\'anello metallico', 'Metal ring verification']:
            if value == '0':
                return '0 (Non pervenuto)' if language == 'it' else '0 (Not received)'
            elif value == '1':
                return '1 (Pervenuto)' if language == 'it' else '1 (Received)'
        
        # Presumed circumstances
        elif field_name in ['Circostanze presunte', 'Presumed circumstances']:
            if value == '0':
                return '0 (No)' if language == 'it' else '0 (No)'
            elif value == '1':
                return '1 (Sì)' if language == 'it' else '1 (Yes)'
        
        # Manipulation codes
        elif field_name in ['Manipolazione', 'Manipulation']:
            if value == '0':
                return '0 (Non manipolato)' if language == 'it' else '0 (Not handled)'
            elif value == '1':
                return '1 (Manipolato)' if language == 'it' else '1 (Handled)'
        
        # Day/Month not specified
        elif field_name in ['Giorno', 'Mese', 'Day', 'Month']:
            if value == '00':
                return '00 (Non specificato)' if language == 'it' else '00 (Not specified)'
        
        # Year not specified
        elif field_name in ['Anno', 'Year']:
            if value == '0000':
                return '0000 (Non specificato)' if language == 'it' else '0000 (Not specified)'
        
        # Time formatting
        elif field_name in ['Ora', 'Time']:
            if value == '0000':
                return '0000 (Non specificata)' if language == 'it' else '0000 (Not specified)'
            elif len(value) == 4 and value.isdigit():
                hours = value[:2]
                minutes = value[2:]
                return f"{hours}:{minutes}"
        
        # Coordinate accuracy
        elif field_name in ['Accuratezza coordinate', 'Coordinate accuracy']:
            if value == '0':
                return '0 (Non specificata)' if language == 'it' else '0 (Not specified)'
            elif value == '1':
                return '1 (Esatta)' if language == 'it' else '1 (Exact)'
            elif value == '2':
                return '2 (Approssimativa)' if language == 'it' else '2 (Approximate)'
        
        # Date accuracy
        elif field_name in ['Accuratezza data', 'Date accuracy']:
            if value == '0':
                return '0 (Esatta)' if language == 'it' else '0 (Exact)'
            elif value == '1':
                return '1 (Approssimativa)' if language == 'it' else '1 (Approximate)'
        
        return value
    
    def translate_parsed_fields(self, parsed_fields: Dict[str, Any], language: str = 'it') -> Dict[str, Any]:
        """
        Translate all field names and values in a parsed fields dictionary
        
        Args:
            parsed_fields: Dictionary of field names and values
            language: Target language ('it' or 'en')
            
        Returns:
            Dictionary with translated field names and values
        """
        if language == 'it':
            return parsed_fields
        
        translated_fields = {}
        
        for field_name, field_value in parsed_fields.items():
            # Skip internal fields
            if field_name.startswith('_'):
                translated_fields[field_name] = field_value
                continue
            
            # Translate field name
            translated_name = self.translate_field_name(field_name, language)
            
            # Translate field value
            translated_value = self.translate_field_value(field_name, field_value, language)
            
            translated_fields[translated_name] = translated_value
        
        return translated_fields


# Global instance
field_translator = FieldTranslator()