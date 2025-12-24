#!/usr/bin/env python3
"""
Test conversioni verso formati 1979 e 2000
"""
import sys
import os
sys.path.append('.')

from app.services.conversion_service import EuringConversionService

def test_conversions():
    """Test conversioni verso tutti i formati"""
    
    service = EuringConversionService()
    
    # Stringa di test 1966
    test_1966 = "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750"
    
    print("🧪 Test conversioni da EURING 1966")
    print(f"Sorgente: {test_1966}")
    print()
    
    # Test conversioni verso tutti i formati
    targets = ['1979', '2000', '2020']
    
    for target in targets:
        print(f"📋 Conversione 1966 → {target}:")
        try:
            result = service.convert_semantic(test_1966, '1966', target)
            
            if result['success']:
                converted = result['converted_string']
                print(f"✅ Successo!")
                print(f"   Risultato: {converted}")
                print(f"   Lunghezza: {len(converted)} caratteri")
                
                # Verifica lunghezza attesa
                expected_lengths = {'1979': 78, '2000': 96, '2020': None}
                expected = expected_lengths.get(target)
                if expected and len(converted) != expected:
                    print(f"⚠️  Attenzione: lunghezza {len(converted)}, attesa {expected}")
                
            else:
                print(f"❌ Errore: {result.get('error', 'Sconosciuto')}")
                
        except Exception as e:
            print(f"💥 Eccezione: {e}")
        
        print()

if __name__ == "__main__":
    test_conversions()