#!/usr/bin/env python3
"""
Analisi del file ASP di EPE (Euring Protocol Engine)
Estrazione della logica di parsing per validazione del nostro sistema
"""

def analyze_epe_parsing():
    """
    Analizza la logica di parsing di EPE dal file ASP
    """
    
    # Mappatura dei campi EURING 2000 secondo EPE
    epe_field_mapping = {
        # Posizione: (start, end, nome_campo, descrizione)
        (1, 3): ("SCHEME", "Osservatorio"),
        (4, 5): ("PRIMARYIDENTIFICATIONMETHOD", "Metodo di identificazione primaria"),
        (6, 15): ("IDENTIFICATIONNUMBER", "Anello (10 caratteri)"),
        (16, 16): ("VERIFICATIONMETALRING", "Verifica dell'anello metallico"),
        (17, 17): ("METALRINGINFORMATION", "Informazioni sull'anello metallico"),
        (18, 19): ("OTHERMARKS", "Altri marcaggi"),
        (20, 24): ("SPECIESREPORTED", "Specie riportata"),
        (25, 29): ("SPECIESCONCLUDED", "Specie conclusa"),
        (30, 30): ("MANIPULATION", "Manipolazione"),
        (31, 31): ("MOVEDBEFORE", "Traslocazione prima della cattura"),
        (32, 32): ("CATCHINGMETHOD", "Metodo di cattura"),
        (33, 33): ("LURESUSED", "Richiamo"),
        (34, 34): ("SEXREPORTED", "Sesso riportato"),
        (35, 35): ("SEXCONCLUDED", "Sesso concluso"),
        (36, 36): ("AGEREPORTED", "Età riportata"),
        (37, 37): ("AGECONCLUDED", "Età conclusa"),
        (38, 38): ("STATUS", "Status"),
        (39, 40): ("BROODSIZE", "Dimensione della covata"),
        (41, 42): ("PULLUSAGE", "Età dei pulcini"),
        (43, 43): ("ACCURACYPULLUSAGE", "Accuratezza età dei pulcini"),
        (44, 45): ("DAY", "Giorno"),
        (46, 47): ("MONTH", "Mese"),
        (48, 51): ("YEAR", "Anno"),
        (52, 52): ("ACCURACYDATE", "Accuratezza data"),
        (53, 56): ("TIME", "Ora"),
        (57, 60): ("AREACODEEDB", "Codice area Euring"),
        (61, 67): ("LATITUDE", "Latitudine"),
        (68, 75): ("LONGITUDE", "Longitudine"),
        (76, 76): ("ACCURACYCOORDINATES", "Accuratezza coordinate"),
        (77, 77): ("CONDITIONCODE", "Condizioni"),
        (78, 79): ("CIRCUMSTANCESCODE", "Circostanze"),
        (80, 80): ("CIRCUMSTANCESPRESUMED", "Circostanze presunte"),
        (81, 81): ("EURINGCODEIDENTIFIER", "Identificatore codice Euring"),
        (82, 86): ("DISTANCE", "Distanza"),
        (87, 89): ("DIRECTION", "Direzione"),
        (90, 94): ("ELAPSEDTIME", "Tempo trascorso")
    }
    
    return epe_field_mapping

def parse_euring_2000_epe_style(euring_string):
    """
    Parsa una stringa EURING 2000 usando la logica di EPE
    """
    if len(euring_string) < 94:
        raise ValueError(f"Stringa EURING troppo corta: {len(euring_string)} caratteri, richiesti almeno 94")
    
    # Parsing secondo EPE (posizioni 1-based nel codice ASP)
    parsed_data = {
        "SCHEME": euring_string[0:3],  # Mid(string, 1, 3) -> [0:3]
        "PRIMARYIDENTIFICATIONMETHOD": euring_string[3:5],  # Mid(string, 4, 2) -> [3:5]
        "IDENTIFICATIONNUMBER": euring_string[5:15],  # Mid(string, 6, 10) -> [5:15]
        "VERIFICATIONMETALRING": euring_string[15:16],  # Mid(string, 16, 1) -> [15:16]
        "METALRINGINFORMATION": euring_string[16:17],  # Mid(string, 17, 1) -> [16:17]
        "OTHERMARKS": euring_string[17:19],  # Mid(string, 18, 2) -> [17:19]
        "SPECIESREPORTED": euring_string[19:24],  # Mid(string, 20, 5) -> [19:24]
        "SPECIESCONCLUDED": euring_string[24:29],  # Mid(string, 25, 5) -> [24:29]
        "MANIPULATION": euring_string[29:30],  # Mid(string, 30, 1) -> [29:30]
        "MOVEDBEFORE": euring_string[30:31],  # Mid(string, 31, 1) -> [30:31]
        "CATCHINGMETHOD": euring_string[31:32],  # Mid(string, 32, 1) -> [31:32]
        "LURESUSED": euring_string[32:33],  # Mid(string, 33, 1) -> [32:33]
        "SEXREPORTED": euring_string[33:34],  # Mid(string, 34, 1) -> [33:34]
        "SEXCONCLUDED": euring_string[34:35],  # Mid(string, 35, 1) -> [34:35]
        "AGEREPORTED": euring_string[35:36],  # Mid(string, 36, 1) -> [35:36]
        "AGECONCLUDED": euring_string[36:37],  # Mid(string, 37, 1) -> [36:37]
        "STATUS": euring_string[37:38],  # Mid(string, 38, 1) -> [37:38]
        "BROODSIZE": euring_string[38:40],  # Mid(string, 39, 2) -> [38:40]
        "PULLUSAGE": euring_string[40:42],  # Mid(string, 41, 2) -> [40:42]
        "ACCURACYPULLUSAGE": euring_string[42:43],  # Mid(string, 43, 1) -> [42:43]
        "DAY": euring_string[43:45],  # Mid(string, 44, 2) -> [43:45]
        "MONTH": euring_string[45:47],  # Mid(string, 46, 2) -> [45:47]
        "YEAR": euring_string[47:51],  # Mid(string, 48, 4) -> [47:51]
        "ACCURACYDATE": euring_string[51:52],  # Mid(string, 52, 1) -> [51:52]
        "TIME": euring_string[52:56],  # Mid(string, 53, 4) -> [52:56]
        "AREACODEEDB": euring_string[56:60],  # Mid(string, 57, 4) -> [56:60]
        "LATITUDE": euring_string[60:67],  # Mid(string, 61, 7) -> [60:67]
        "LONGITUDE": euring_string[67:75],  # Mid(string, 68, 8) -> [67:75]
        "ACCURACYCOORDINATES": euring_string[75:76],  # Mid(string, 76, 1) -> [75:76]
        "CONDITIONCODE": euring_string[76:77],  # Mid(string, 77, 1) -> [76:77]
        "CIRCUMSTANCESCODE": euring_string[77:79],  # Mid(string, 78, 2) -> [77:79]
        "CIRCUMSTANCESPRESUMED": euring_string[79:80],  # Mid(string, 80, 1) -> [79:80]
        "EURINGCODEIDENTIFIER": euring_string[80:81],  # Mid(string, 81, 1) -> [80:81]
        "DISTANCE": euring_string[81:86],  # Mid(string, 82, 5) -> [81:86]
        "DIRECTION": euring_string[86:89],  # Mid(string, 87, 3) -> [86:89]
        "ELAPSEDTIME": euring_string[89:94],  # Mid(string, 90, 5) -> [89:94]
    }
    
    return parsed_data

def format_epe_output(parsed_data):
    """
    Formatta l'output nello stile di EPE per confronto
    """
    output = []
    output.append(f"Stringa Euring 2000: {parsed_data.get('_original_string', 'N/A')}")
    output.append("")
    output.append("Dato\t\tValore\tTranscodifica")
    output.append("-" * 60)
    
    field_descriptions = {
        "SCHEME": "Osservatorio",
        "PRIMARYIDENTIFICATIONMETHOD": "Metodo di identificazione primaria",
        "IDENTIFICATIONNUMBER": "Anello",
        "VERIFICATIONMETALRING": "Verifica dell'anello metallico",
        "METALRINGINFORMATION": "Informazioni sull'anello metallico",
        "OTHERMARKS": "Altri marcaggi",
        "SPECIESREPORTED": "Specie riportata",
        "SPECIESCONCLUDED": "Specie conclusa",
        "MANIPULATION": "Manipolazione",
        "MOVEDBEFORE": "Traslocazione prima della cattura",
        "CATCHINGMETHOD": "Metodo di cattura",
        "LURESUSED": "Richiamo",
        "SEXREPORTED": "Sesso riportato",
        "SEXCONCLUDED": "Sesso concluso",
        "AGEREPORTED": "Età riportata",
        "AGECONCLUDED": "Età conclusa",
        "STATUS": "Status",
        "BROODSIZE": "Dimensione della covata",
        "PULLUSAGE": "Età dei pulcini",
        "ACCURACYPULLUSAGE": "Accuratezza età dei pulcini",
        "DAY": "Giorno",
        "MONTH": "Mese",
        "YEAR": "Anno",
        "ACCURACYDATE": "Accuratezza data",
        "TIME": "Ora",
        "AREACODEEDB": "Codice area Euring",
        "LATITUDE": "Latitudine",
        "LONGITUDE": "Longitudine",
        "ACCURACYCOORDINATES": "Accuratezza coordinate",
        "CONDITIONCODE": "Condizioni",
        "CIRCUMSTANCESCODE": "Circostanze",
        "CIRCUMSTANCESPRESUMED": "Circostanze presunte",
        "EURINGCODEIDENTIFIER": "Identificatore codice Euring",
        "DISTANCE": "Distanza",
        "DIRECTION": "Direzione",
        "ELAPSEDTIME": "Tempo trascorso"
    }
    
    for field, value in parsed_data.items():
        if field.startswith('_'):
            continue
        desc = field_descriptions.get(field, field)
        output.append(f"{desc:<35}\t{value}\t[Transcodifica richiesta]")
    
    return "\n".join(output)

def validate_against_epe(euring_string):
    """
    Valida una stringa EURING usando la logica di EPE
    """
    try:
        parsed = parse_euring_2000_epe_style(euring_string)
        parsed['_original_string'] = euring_string
        
        # Validazioni specifiche di EPE
        validations = []
        
        # Controllo lunghezza
        if len(euring_string) != 94:
            validations.append(f"⚠️  Lunghezza non standard: {len(euring_string)} (attesa: 94)")
        
        # Controllo scheme
        scheme = parsed['SCHEME']
        if scheme.startswith('IA'):
            validations.append(f"✓ Scheme riconosciuto: {scheme}")
        else:
            validations.append(f"⚠️  Scheme non riconosciuto: {scheme}")
        
        # Controllo sesso
        sex_reported = parsed['SEXREPORTED']
        sex_concluded = parsed['SEXCONCLUDED']
        if sex_reported in ['M', 'F']:
            validations.append(f"✓ Sesso riportato valido: {sex_reported}")
        if sex_concluded in ['M', 'F']:
            validations.append(f"✓ Sesso concluso valido: {sex_concluded}")
        
        # Controllo date
        day = parsed['DAY']
        month = parsed['MONTH']
        year = parsed['YEAR']
        if day.isdigit() and 1 <= int(day) <= 31:
            validations.append(f"✓ Giorno valido: {day}")
        if month.isdigit() and 1 <= int(month) <= 12:
            validations.append(f"✓ Mese valido: {month}")
        if year.isdigit() and 1900 <= int(year) <= 2030:
            validations.append(f"✓ Anno valido: {year}")
        
        return {
            'success': True,
            'parsed_data': parsed,
            'validations': validations,
            'formatted_output': format_epe_output(parsed)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'validations': [f"❌ Errore di parsing: {e}"]
        }

if __name__ == "__main__":
    # Test con una stringa di esempio (94 caratteri esatti)
    # Costruiamo una stringa EURING 2000 valida campo per campo
    test_string = (
        "IAB" +           # SCHEME (3)
        "01" +            # PRIMARYIDENTIFICATIONMETHOD (2) 
        "ABC1234567" +    # IDENTIFICATIONNUMBER (10)
        "0" +             # VERIFICATIONMETALRING (1)
        "1" +             # METALRINGINFORMATION (1)
        "ZZ" +            # OTHERMARKS (2)
        "12345" +         # SPECIESREPORTED (5)
        "12345" +         # SPECIESCONCLUDED (5)
        "0" +             # MANIPULATION (1)
        "0" +             # MOVEDBEFORE (1)
        "1" +             # CATCHINGMETHOD (1)
        "0" +             # LURESUSED (1)
        "M" +             # SEXREPORTED (1)
        "M" +             # SEXCONCLUDED (1)
        "1" +             # AGEREPORTED (1)
        "1" +             # AGECONCLUDED (1)
        "3" +             # STATUS (1)
        "00" +            # BROODSIZE (2)
        "99" +            # PULLUSAGE (2)
        "0" +             # ACCURACYPULLUSAGE (1)
        "15" +            # DAY (2)
        "06" +            # MONTH (2)
        "2023" +          # YEAR (4)
        "1" +             # ACCURACYDATE (1)
        "1200" +          # TIME (4)
        "1234" +          # AREACODEEDB (4)
        "4512345" +       # LATITUDE (7)
        "01234567" +      # LONGITUDE (8)
        "1" +             # ACCURACYCOORDINATES (1)
        "0" +             # CONDITIONCODE (1)
        "00" +            # CIRCUMSTANCESCODE (2)
        "0" +             # CIRCUMSTANCESPRESUMED (1)
        "1" +             # EURINGCODEIDENTIFIER (1)
        "00000" +         # DISTANCE (5)
        "000" +           # DIRECTION (3)
        "00000"           # ELAPSEDTIME (5)
    )
    
    print("=== Analisi EPE - Parsing EURING 2000 ===")
    print(f"Stringa di test: {test_string}")
    print(f"Lunghezza: {len(test_string)} caratteri")
    print()
    
    result = validate_against_epe(test_string)
    
    if result['success']:
        print("✅ Parsing completato con successo")
        print()
        print("Validazioni:")
        for validation in result['validations']:
            print(f"  {validation}")
        print()
        print("Campi principali estratti:")
        parsed = result['parsed_data']
        print(f"  Osservatorio: {parsed['SCHEME']}")
        print(f"  Anello: {parsed['IDENTIFICATIONNUMBER']}")
        print(f"  Specie: {parsed['SPECIESREPORTED']}")
        print(f"  Sesso: {parsed['SEXREPORTED']}")
        print(f"  Data: {parsed['DAY']}/{parsed['MONTH']}/{parsed['YEAR']}")
        print(f"  Coordinate: {parsed['LATITUDE']}, {parsed['LONGITUDE']}")
    else:
        print("❌ Errore nel parsing:")
        print(f"  {result['error']}")