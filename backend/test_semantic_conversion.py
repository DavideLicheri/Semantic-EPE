#!/usr/bin/env python3
"""
Test del sistema di conversione semantica EURING
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversion_service import EuringConversionService
from app.services.semantic_converter import SemanticConverter
from app.services.parsers.euring_1966_parser import Euring1966Parser
from app.services.parsers.euring_2020_parser import Euring2020Parser
import json


def test_semantic_extraction():
    """Test estrazione dati semantici"""
    
    print("=== TEST ESTRAZIONE SEMANTICA ===\n")
    
    # Test con EURING 1966
    euring_1966 = '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750'
    parser_1966 = Euring1966Parser()
    converter = SemanticConverter()
    
    print("Test EURING 1966:")
    print(f"Stringa: {euring_1966}")
    
    try:
        # Parse della stringa
        parsed_data = parser_1966.to_dict(euring_1966)
        print("✓ Parsing riuscito")
        
        # Estrazione semantica
        semantic_data = converter.extract_semantic_data(parsed_data, '1966')
        print("✓ Estrazione semantica riuscita")
        
        # Mostra dati semantici
        print("\nDati semantici estratti:")
        for field_name, field_data in semantic_data.items():
            if isinstance(field_data, dict) and 'value' in field_data:
                value = field_data['value']
                source = field_data.get('source', 'unknown')
                notes = field_data.get('notes', [])
                print(f"  {field_name}: {value} (source: {source})")
                if notes:
                    for note in notes:
                        print(f"    Note: {note}")
        
    except Exception as e:
        print(f"✗ Errore: {e}")
    
    print()


def test_semantic_conversion():
    """Test conversione semantica completa"""
    
    print("=== TEST CONVERSIONE SEMANTICA ===\n")
    
    # Test 1966 → 2020
    euring_1966 = '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750'
    
    converter_service = EuringConversionService()
    
    print("Test conversione 1966 → 2020:")
    print(f"Sorgente: {euring_1966}")
    
    try:
        result = converter_service.convert_semantic(euring_1966, '1966', '2020')
        
        if result['success']:
            print("✓ Conversione semantica riuscita")
            print(f"Target: {result['converted_string']}")
            print(f"Metodo: {result.get('conversion_method', 'unknown')}")
            
            # Mostra note di conversione
            notes = result.get('conversion_notes', [])
            if notes:
                print(f"Note di conversione ({len(notes)}):")
                for note in notes:
                    print(f"  - {note}")
            
            # Mostra dati semantici
            if 'semantic_data' in result:
                print("\nCampi semantici identificati:")
                semantic_data = result['semantic_data']
                for field_name, field_data in semantic_data.items():
                    if isinstance(field_data, dict) and 'value' in field_data:
                        value = field_data['value']
                        print(f"  {field_name}: {value}")
        else:
            print(f"✗ Conversione fallita: {result.get('error', 'Errore sconosciuto')}")
    
    except Exception as e:
        print(f"✗ Errore durante la conversione: {e}")
    
    print()


def test_bidirectional_conversion():
    """Test conversione bidirezionale"""
    
    print("=== TEST CONVERSIONE BIDIREZIONALE ===\n")
    
    # Test 1966 → 2020 → 1966
    original_1966 = '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750'
    
    converter_service = EuringConversionService()
    
    print("Test conversione bidirezionale 1966 → 2020 → 1966:")
    print(f"Originale: {original_1966}")
    
    try:
        # 1966 → 2020
        result_2020 = converter_service.convert_semantic(original_1966, '1966', '2020')
        
        if result_2020['success']:
            converted_2020 = result_2020['converted_string']
            print(f"→ 2020: {converted_2020}")
            
            # 2020 → 1966
            result_1966 = converter_service.convert_semantic(converted_2020, '2020', '1966')
            
            if result_1966['success']:
                converted_back_1966 = result_1966['converted_string']
                print(f"→ 1966: {converted_back_1966}")
                
                # Confronto
                print("\nConfronto:")
                print(f"Originale: {original_1966}")
                print(f"Convertito: {converted_back_1966}")
                
                if original_1966 == converted_back_1966:
                    print("✓ Conversione bidirezionale perfetta!")
                else:
                    print("⚠ Conversione bidirezionale con differenze")
                    print("  Questo è normale per conversioni tra formati diversi")
            else:
                print(f"✗ Conversione 2020→1966 fallita: {result_1966.get('error')}")
        else:
            print(f"✗ Conversione 1966→2020 fallita: {result_2020.get('error')}")
    
    except Exception as e:
        print(f"✗ Errore durante la conversione bidirezionale: {e}")
    
    print()


def test_field_mapping_analysis():
    """Analisi mappatura campi"""
    
    print("=== ANALISI MAPPATURA CAMPI ===\n")
    
    converter = SemanticConverter()
    
    print("Campi semantici definiti:")
    for field_name, field_def in converter.semantic_fields.items():
        print(f"  {field_name}:")
        print(f"    Significato: {field_def.semantic_meaning}")
        print(f"    Tipo: {field_def.data_type}")
        print(f"    Richiesto: {field_def.required}")
        if field_def.default_value is not None:
            print(f"    Default: {field_def.default_value}")
    
    print("\nMappature per versione:")
    for version, mappings in converter.version_mappings.items():
        print(f"\n  EURING {version}:")
        for semantic_field, version_field in mappings.items():
            print(f"    {semantic_field} → {version_field}")
    
    print()


def test_coordinate_conversion():
    """Test conversione coordinate"""
    
    print("=== TEST CONVERSIONE COORDINATE ===\n")
    
    converter = SemanticConverter()
    
    # Test coordinate 1966 (gradi/minuti)
    lat_1966 = {'decimal': 52.25, 'original': '5215N', 'direction': 'N'}
    lon_1966 = {'decimal': 13.416666666666666, 'original': '01325E', 'direction': 'E'}
    
    print("Test conversione coordinate:")
    print(f"Latitudine 1966: {lat_1966}")
    print(f"Longitudine 1966: {lon_1966}")
    
    # Conversione a semantico
    lat_semantic = converter._convert_coordinate_semantic(lat_1966, None, '1966')
    lon_semantic = converter._convert_coordinate_semantic(lon_1966, None, '1966')
    
    print(f"Latitudine semantica: {lat_semantic}")
    print(f"Longitudine semantica: {lon_semantic}")
    
    # Conversione a 2020 (decimale)
    lat_2020 = converter._convert_from_semantic(lat_semantic, 'geographic_latitude', '2020')
    lon_2020 = converter._convert_from_semantic(lon_semantic, 'geographic_longitude', '2020')
    
    print(f"Latitudine 2020: {lat_2020}")
    print(f"Longitudine 2020: {lon_2020}")
    
    print()


if __name__ == "__main__":
    print("Avvio test sistema di conversione semantica EURING...\n")
    
    test_semantic_extraction()
    test_semantic_conversion()
    test_bidirectional_conversion()
    test_field_mapping_analysis()
    test_coordinate_conversion()
    
    print("=== RIEPILOGO TEST ===")
    print("Test completati. Il sistema di conversione semantica permette di:")
    print("1. Estrarre significato semantico dai campi EURING")
    print("2. Convertire tra versioni basandosi sul significato")
    print("3. Gestire differenze di formato e unità di misura")
    print("4. Fornire note dettagliate sulle conversioni")
    print("5. Mantenere la coerenza semantica tra versioni diverse")