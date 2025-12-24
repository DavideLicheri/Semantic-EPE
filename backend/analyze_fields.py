#!/usr/bin/env python3
"""
Strumento per analizzare campo per campo le stringhe EURING
"""

def analyze_character_by_character():
    """Analizza ogni carattere delle stringhe EURING"""
    
    strings = {
        '1966': '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
        '1979': '05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------',
        '2000': 'IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086',
        '2020': '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2'
    }
    
    print("=== ANALISI CARATTERE PER CARATTERE ===\n")
    
    for version, string in strings.items():
        print(f"EURING {version} ({len(string)} caratteri):")
        print(f"Stringa: {string}")
        print("Posizioni:")
        
        # Mostra posizioni ogni 10 caratteri
        positions = ""
        for i in range(0, len(string), 10):
            positions += f"{i:10d}"
        print(f"         {positions}")
        
        # Mostra numeri di posizione
        numbers = ""
        for i in range(len(string)):
            numbers += str(i % 10)
        print(f"         {numbers}")
        
        print(f"Caratteri: {string}")
        print()


def analyze_1966_fields():
    """Analisi dettagliata EURING 1966"""
    string = '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750'
    fields = string.split(' ')
    
    print("=== ANALISI DETTAGLIATA EURING 1966 ===")
    print(f"Stringa completa: {string}")
    print(f"Lunghezza: {len(string)} caratteri")
    print(f"Numero campi: {len(fields)}")
    print()
    
    field_names = [
        'species_code', 'ring_number', 'age_code', 'date_code',
        'latitude', 'longitude', 'condition_code', 'method_code',
        'wing_length', 'weight', 'bill_length'
    ]
    
    for i, (name, value) in enumerate(zip(field_names, fields)):
        print(f"Campo {i+1:2d}: {name:15s} = '{value}' ({len(value)} caratteri)")
    
    print()


def analyze_1979_fields():
    """Analisi dettagliata EURING 1979"""
    string = '05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------'
    
    print("=== ANALISI DETTAGLIATA EURING 1979 ===")
    print(f"Stringa completa: {string}")
    print(f"Lunghezza: {len(string)} caratteri")
    print()
    
    # Analisi basata su lunghezze fisse ipotizzate
    fields = [
        ('species_code', 0, 5),
        ('scheme_country', 5, 7),
        ('ring_number', 7, 14),
        ('age_code', 14, 15),
        ('sex_code', 15, 16),
        ('status_code', 16, 17),
        ('date_first', 17, 23),
        ('date_current', 23, 29),
        ('latitude', 29, 35),
        ('longitude', 35, 41),
        ('condition_code', 41, 43),
        ('method_code', 43, 44),
        ('accuracy_code', 44, 46),
        ('empty_1', 46, 48),
        ('wing_length', 48, 51),
        ('weight', 51, 55),
        ('empty_2', 55, 57),
        ('bill_length', 57, 61),
        ('tarsus_length', 61, 63),
        ('empty_3', 63, 65),
        ('additional_1', 65, 68),
        ('additional_2', 68, 71),
        ('padding', 71, 78)
    ]
    
    for name, start, end in fields:
        value = string[start:end]
        print(f"Pos {start:2d}-{end:2d}: {name:15s} = '{value}' ({len(value)} caratteri)")
    
    print()


def analyze_2000_fields():
    """Analisi dettagliata EURING 2000"""
    string = 'IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086'
    
    print("=== ANALISI DETTAGLIATA EURING 2000 ===")
    print(f"Stringa completa: {string}")
    print(f"Lunghezza: {len(string)} caratteri")
    print()
    
    # Analisi basata su pattern visibili
    print("Analisi pattern visibili:")
    print(f"Inizio: {string[:20]} (primi 20 caratteri)")
    print(f"Separatori '...': posizione {string.find('...')}")
    print(f"Separatori '-----': posizione {string.find('-----')}")
    print(f"Separatori '---': posizione {string.find('---')}")
    print(f"Coordinate '+': posizioni {[i for i, c in enumerate(string) if c == '+']}")
    print()
    
    # Tentativo di scomposizione
    fields = [
        ('scheme_code', 0, 4),
        ('ring_prefix', 4, 7),
        ('separator', 7, 10),
        ('ring_number', 10, 17),
        ('ring_suffix', 17, 19),
        ('date_first', 19, 24),
        ('date_current', 24, 29),
        ('status_code', 29, 30),
        ('age_code', 30, 31),
        ('location_code', 31, 36),
        ('accuracy_code', 36, 38),
        ('empty_1', 38, 43),
        ('measurements', 43, 56),
        ('region_code', 56, 60),
        ('coordinates', 60, 74),
        ('additional_codes', 74, 86),
        ('empty_2', 86, 89),
        ('final_code', 89, 94)
    ]
    
    for name, start, end in fields:
        if end <= len(string):
            value = string[start:end]
            print(f"Pos {start:2d}-{end:2d}: {name:15s} = '{value}' ({len(value)} caratteri)")
    
    print()


def analyze_2020_fields():
    """Analisi dettagliata EURING 2020"""
    string = '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2'
    fields = string.split('|')
    
    print("=== ANALISI DETTAGLIATA EURING 2020 ===")
    print(f"Stringa completa: {string}")
    print(f"Lunghezza: {len(string)} caratteri")
    print(f"Numero campi: {len(fields)}")
    print()
    
    field_names = [
        'species_code', 'ring_number', 'metal_ring_info', 'other_marks_info',
        'age_code', 'sex_code', 'date_code', 'time_code', 'latitude_decimal',
        'longitude_decimal', 'condition_code', 'method_code', 'accuracy_code',
        'status_info', 'verification_code', 'wing_length', 'weight',
        'bill_length', 'tarsus_length', 'fat_score', 'muscle_score', 'moult_code'
    ]
    
    for i, (name, value) in enumerate(zip(field_names, fields)):
        print(f"Campo {i+1:2d}: {name:18s} = '{value}' ({len(value)} caratteri)")
    
    print()


def compare_common_fields():
    """Confronta i campi comuni tra le versioni"""
    
    print("=== CONFRONTO CAMPI COMUNI ===\n")
    
    # Dati estratti dalle analisi precedenti
    data = {
        '1966': {
            'species_code': '5320',
            'ring_number': 'TA12345',
            'age_code': '3',
            'date': '11022023',
            'latitude': '5215N',
            'longitude': '01325E',
            'wing_length': '050',
            'weight': '0115',
            'bill_length': '0750'
        },
        '1979': {
            'species_code': '05320',
            'ring_number': 'ISA12345',  # Posizione 7-14
            'age_code': '0',  # Posizione 14-15
            'sex_code': '9',  # Posizione 15-16
            'date_first': '050119',  # Posizione 17-23
            'date_current': '950521',  # Posizione 23-29
            'latitude': '5215N',  # Posizione 29-35 (approssimato)
            'longitude': '01325E',  # Posizione 35-41 (approssimato)
            'wing_length': '050',  # Posizione 48-51
            'weight': '0115',  # Posizione 51-55
            'bill_length': '0750'  # Posizione 57-61
        },
        '2020': {
            'species_code': '05320',
            'ring_number': 'ISA12345',
            'age_code': '3',
            'sex_code': '2',
            'date': '20230521',
            'time': '1430',
            'latitude': '52.25412',
            'longitude': '-1.34521',
            'wing_length': '135.5',
            'weight': '19.5'
        }
    }
    
    common_fields = ['species_code', 'ring_number', 'age_code', 'wing_length', 'weight']
    
    for field in common_fields:
        print(f"Campo: {field}")
        for version in ['1966', '1979', '2020']:
            if field in data[version]:
                value = data[version][field]
                print(f"  {version}: '{value}'")
        print()


if __name__ == "__main__":
    analyze_character_by_character()
    analyze_1966_fields()
    analyze_1979_fields()
    analyze_2000_fields()
    analyze_2020_fields()
    compare_common_fields()