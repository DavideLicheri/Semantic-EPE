"""
EURING 2000 Parser - EPE Compatible
Replica ESATTAMENTE la logica di parsing dell'applicativo EPE
che ha funzionato correttamente per 10 anni
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from ...models.euring_models import EuringVersion


class Euring2000EpeCompatibleParser:
    """
    Parser for EURING 2000 format strings - EPE Compatible
    
    Replica ESATTAMENTE le posizioni e la logica di parsing
    dell'applicativo EPE (Euring Protocol Engine) che ha
    funzionato correttamente per una decina di anni.
    
    IMPORTANTE: Non modificare le posizioni dei campi senza
    verificare la compatibilità con EPE!
    """
    
    def __init__(self):
        # Definizioni dei campi ESATTAMENTE come in EPE
        # Posizioni basate su Mid(string, start, length) di VBScript (1-based)
        # Convertite in slice Python (0-based)
        self.field_definitions = {
            # Campo: (start_0based, end_0based, nome_epe, descrizione)
            'scheme': (0, 3, 'SCHEME', 'Osservatorio'),
            'primary_identification_method': (3, 5, 'PRIMARYIDENTIFICATIONMETHOD', 'Metodo di identificazione primaria'),
            'identification_number': (5, 15, 'IDENTIFICATIONNUMBER', 'Anello (10 caratteri)'),
            'verification_metal_ring': (15, 16, 'VERIFICATIONMETALRING', 'Verifica dell\'anello metallico'),
            'metal_ring_information': (16, 17, 'METALRINGINFORMATION', 'Informazioni sull\'anello metallico'),
            'other_marks': (17, 19, 'OTHERMARKS', 'Altri marcaggi'),
            'species_reported': (19, 24, 'SPECIESREPORTED', 'Specie riportata'),
            'species_concluded': (24, 29, 'SPECIESCONCLUDED', 'Specie conclusa'),
            'manipulation': (29, 30, 'MANIPULATION', 'Manipolazione'),
            'moved_before': (30, 31, 'MOVEDBEFORE', 'Traslocazione prima della cattura'),
            'catching_method': (31, 32, 'CATCHINGMETHOD', 'Metodo di cattura'),
            'lures_used': (32, 33, 'LURESUSED', 'Richiamo'),
            'sex_reported': (33, 34, 'SEXREPORTED', 'Sesso riportato'),
            'sex_concluded': (34, 35, 'SEXCONCLUDED', 'Sesso concluso'),
            'age_reported': (35, 36, 'AGEREPORTED', 'Età riportata'),
            'age_concluded': (36, 37, 'AGECONCLUDED', 'Età conclusa'),
            'status': (37, 38, 'STATUS', 'Status'),
            'brood_size': (38, 40, 'BROODSIZE', 'Dimensione della covata'),
            'pullus_age': (40, 42, 'PULLUSAGE', 'Età dei pulcini'),
            'accuracy_pullus_age': (42, 43, 'ACCURACYPULLUSAGE', 'Accuratezza età dei pulcini'),
            'day': (43, 45, 'DAY', 'Giorno'),
            'month': (45, 47, 'MONTH', 'Mese'),
            'year': (47, 51, 'YEAR', 'Anno'),
            'accuracy_date': (51, 52, 'ACCURACYDATE', 'Accuratezza data'),
            'time': (52, 56, 'TIME', 'Ora'),
            'area_code_edb': (56, 60, 'AREACODEEDB', 'Codice area Euring'),
            'latitude': (60, 67, 'LATITUDE', 'Latitudine'),
            'longitude': (67, 75, 'LONGITUDE', 'Longitudine'),
            'accuracy_coordinates': (75, 76, 'ACCURACYCOORDINATES', 'Accuratezza coordinate'),
            'condition_code': (76, 77, 'CONDITIONCODE', 'Condizioni'),
            'circumstances_code': (77, 79, 'CIRCUMSTANCESCODE', 'Circostanze'),
            'circumstances_presumed': (79, 80, 'CIRCUMSTANCESPRESUMED', 'Circostanze presunte'),
            'euring_code_identifier': (80, 81, 'EURINGCODEIDENTIFIER', 'Identificatore codice Euring'),
            'distance': (81, 86, 'DISTANCE', 'Distanza'),
            'direction': (86, 89, 'DIRECTION', 'Direzione'),
            'elapsed_time': (89, 94, 'ELAPSEDTIME', 'Tempo trascorso')
        }
    
    def parse(self, euring_string: str) -> Dict[str, Any]:
        """
        Parse EURING 2000 string usando la logica EPE
        
        Args:
            euring_string: Stringa EURING 2000 (94 caratteri)
            
        Returns:
            Dict con i campi parsati secondo EPE (solo descrizioni italiane leggibili)
            
        Raises:
            ValueError: Se la stringa non è valida
        """
        if not euring_string or not euring_string.strip():
            raise ValueError("EURING string cannot be empty")
        
        # Rimuovi spazi e valida lunghezza (ESATTAMENTE come EPE)
        euring_string = euring_string.strip()
        if len(euring_string) != 94:
            raise ValueError(f"EURING 2000 format requires exactly 94 characters, got {len(euring_string)}")
        
        parsed_data = {}
        
        # Parse ogni campo usando le posizioni EPE - SOLO descrizioni italiane per leggibilità
        for field_name, (start, end, epe_name, description) in self.field_definitions.items():
            field_value = euring_string[start:end]
            # Usa la descrizione italiana per massima leggibilità
            parsed_data[description] = field_value
        
        # Aggiungi metadati
        parsed_data['_original_string'] = euring_string
        parsed_data['_parser_type'] = 'epe_compatible'
        parsed_data['_euring_version'] = 'euring_2000'
        
        return parsed_data
    
    def validate_epe_style(self, parsed_data: Dict[str, Any]) -> List[str]:
        """
        Validazione nello stile EPE
        
        Replica le validazioni che faceva EPE per garantire
        compatibilità al 100%
        """
        validations = []
        
        # Controllo scheme (come in EPE)
        scheme = parsed_data.get('SCHEME', '')
        if scheme.startswith('IA'):
            # EPE convertiva "IA" in "IAB"
            if scheme == 'IAB':
                validations.append(f"✓ Scheme riconosciuto: {scheme}")
            else:
                validations.append(f"⚠️ Scheme IA rilevato, EPE lo convertirebbe in IAB")
        else:
            validations.append(f"⚠️ Scheme non riconosciuto: {scheme}")
        
        # Controllo sesso (come in EPE)
        sex_reported = parsed_data.get('SEXREPORTED', '')
        sex_concluded = parsed_data.get('SEXCONCLUDED', '')
        
        if sex_reported == 'M':
            validations.append("✓ Sesso riportato: Maschio")
        elif sex_reported == 'F':
            validations.append("✓ Sesso riportato: Femmina")
        else:
            validations.append("✓ Sesso riportato: Sconosciuto")
        
        if sex_concluded == 'M':
            validations.append("✓ Sesso concluso: Maschio")
        elif sex_concluded == 'F':
            validations.append("✓ Sesso concluso: Femmina")
        else:
            validations.append("✓ Sesso concluso: Sconosciuto")
        
        # Controllo date (come in EPE)
        day = parsed_data.get('DAY', '')
        month = parsed_data.get('MONTH', '')
        year = parsed_data.get('YEAR', '')
        
        if day.isdigit() and 1 <= int(day) <= 31:
            validations.append(f"✓ Giorno valido: {day}")
        else:
            validations.append(f"⚠️ Giorno non valido: {day}")
        
        if month.isdigit() and 1 <= int(month) <= 12:
            validations.append(f"✓ Mese valido: {month}")
        else:
            validations.append(f"⚠️ Mese non valido: {month}")
        
        if year.isdigit() and 1900 <= int(year) <= 2030:
            validations.append(f"✓ Anno valido: {year}")
        else:
            validations.append(f"⚠️ Anno non valido: {year}")
        
        # Controllo verifica anello metallico (come in EPE)
        verification = parsed_data.get('VERIFICATIONMETALRING', '')
        if verification == '0':
            validations.append("✓ Anello metallico non pervenuto")
        elif verification == '1':
            validations.append("✓ Anello metallico pervenuto")
        else:
            validations.append(f"⚠️ Verifica anello non valida: {verification}")
        
        # Controllo circostanze presunte (come in EPE)
        circumstances_presumed = parsed_data.get('CIRCUMSTANCESPRESUMED', '')
        if circumstances_presumed == '0':
            validations.append("✓ Circostanze presunte: No")
        elif circumstances_presumed == '1':
            validations.append("✓ Circostanze presunte: Sì")
        else:
            validations.append(f"⚠️ Circostanze presunte non valide: {circumstances_presumed}")
        
        return validations
    
    def format_epe_style(self, parsed_data: Dict[str, Any]) -> str:
        """
        Formatta l'output nello stile EPE per confronto diretto
        """
        output = []
        output.append(f"Stringa Euring 2000: {parsed_data.get('_original_string', 'N/A')}")
        output.append("")
        output.append("Dato\t\t\t\tValore\tTranscodifica")
        output.append("-" * 80)
        
        # Campi principali nello stesso ordine di EPE
        epe_fields = [
            ('SCHEME', 'Osservatorio'),
            ('PRIMARYIDENTIFICATIONMETHOD', 'Metodo di identificazione primaria'),
            ('IDENTIFICATIONNUMBER', 'Anello'),
            ('VERIFICATIONMETALRING', 'Verifica dell\'anello metallico'),
            ('METALRINGINFORMATION', 'Informazioni sull\'anello metallico'),
            ('OTHERMARKS', 'Altri marcaggi'),
            ('SPECIESREPORTED', 'Specie riportata'),
            ('SPECIESCONCLUDED', 'Specie conclusa'),
            ('MANIPULATION', 'Manipolazione'),
            ('MOVEDBEFORE', 'Traslocazione prima della cattura'),
            ('CATCHINGMETHOD', 'Metodo di cattura'),
            ('LURESUSED', 'Richiamo'),
            ('SEXREPORTED', 'Sesso riportato'),
            ('SEXCONCLUDED', 'Sesso concluso'),
            ('AGEREPORTED', 'Età riportata'),
            ('AGECONCLUDED', 'Età conclusa'),
            ('STATUS', 'Status'),
            ('BROODSIZE', 'Dimensione della covata'),
            ('PULLUSAGE', 'Età dei pulcini'),
            ('ACCURACYPULLUSAGE', 'Accuratezza età dei pulcini'),
            ('DAY', 'Giorno'),
            ('MONTH', 'Mese'),
            ('YEAR', 'Anno'),
            ('ACCURACYDATE', 'Accuratezza data'),
            ('TIME', 'Ora'),
            ('AREACODEEDB', 'Codice area Euring'),
            ('LATITUDE', 'Latitudine'),
            ('LONGITUDE', 'Longitudine'),
            ('ACCURACYCOORDINATES', 'Accuratezza coordinate'),
            ('CONDITIONCODE', 'Condizioni'),
            ('CIRCUMSTANCESCODE', 'Circostanze'),
            ('CIRCUMSTANCESPRESUMED', 'Circostanze presunte'),
            ('EURINGCODEIDENTIFIER', 'Identificatore codice Euring'),
            ('DISTANCE', 'Distanza'),
            ('DIRECTION', 'Direzione'),
            ('ELAPSEDTIME', 'Tempo trascorso')
        ]
        
        for field_code, description in epe_fields:
            value = parsed_data.get(field_code, '')
            output.append(f"{description:<35}\t{value}\t[Richiede transcodifica DB]")
        
        return "\n".join(output)
    
    def to_dict(self, euring_string: str) -> Dict[str, Any]:
        """
        Parse completo con validazione EPE-style
        
        Returns:
            Dict con:
            - Tutti i campi parsati
            - Validazioni EPE-style
            - Output formattato EPE-style
            - Metadati di compatibilità
        """
        parsed_data = self.parse(euring_string)
        
        # Aggiungi validazioni EPE-style
        validations = self.validate_epe_style(parsed_data)
        parsed_data['_epe_validations'] = validations
        
        # Aggiungi output formattato EPE-style
        formatted_output = self.format_epe_style(parsed_data)
        parsed_data['_epe_formatted_output'] = formatted_output
        
        # Metadati di compatibilità
        parsed_data['_epe_compatible'] = True
        parsed_data['_parser_version'] = '1.0_epe_compatible'
        parsed_data['_validation_timestamp'] = datetime.now().isoformat()
        
        return parsed_data


def test_epe_compatibility():
    """Test di compatibilità con EPE"""
    parser = Euring2000EpeCompatibleParser()
    
    # Stringa di test (94 caratteri)
    test_string = "IAB01ABC123456701ZZ12345123450010MM11300990150620231120012344512345012345671000010000000000000"
    
    print("=== Test Compatibilità EPE ===")
    print(f"Stringa: {test_string}")
    print(f"Lunghezza: {len(test_string)}")
    print()
    
    try:
        result = parser.to_dict(test_string)
        
        print("✅ Parsing riuscito!")
        print()
        print("Campi principali:")
        print(f"  Osservatorio: {result['SCHEME']}")
        print(f"  Anello: {result['IDENTIFICATIONNUMBER']}")
        print(f"  Specie riportata: {result['SPECIESREPORTED']}")
        print(f"  Sesso: {result['SEXREPORTED']}")
        print(f"  Data: {result['DAY']}/{result['MONTH']}/{result['YEAR']}")
        print()
        
        print("Validazioni EPE:")
        for validation in result['_epe_validations']:
            print(f"  {validation}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False


if __name__ == "__main__":
    test_epe_compatibility()