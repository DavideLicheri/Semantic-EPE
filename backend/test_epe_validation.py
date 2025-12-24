#!/usr/bin/env python3
"""
Test di validazione del nostro sistema contro la logica di EPE
"""
import asyncio
import sys
sys.path.append('.')

from epe_analysis import parse_euring_2000_epe_style, validate_against_epe
from app.services.recognition_engine import RecognitionEngineImpl
from app.services.skos_manager import SKOSManagerImpl

async def compare_with_epe(euring_string):
    """
    Confronta il parsing del nostro sistema con quello di EPE
    """
    print(f"🔍 Testando stringa: {euring_string}")
    print(f"📏 Lunghezza: {len(euring_string)} caratteri")
    print()
    
    # 1. Parsing con EPE
    print("=== PARSING EPE ===")
    epe_result = validate_against_epe(euring_string)
    
    if epe_result['success']:
        print("✅ EPE parsing riuscito")
        epe_data = epe_result['parsed_data']
        
        # Mostra alcuni campi chiave
        print(f"  Scheme: {epe_data['SCHEME']}")
        print(f"  Ring: {epe_data['IDENTIFICATIONNUMBER']}")
        print(f"  Species Reported: {epe_data['SPECIESREPORTED']}")
        print(f"  Date: {epe_data['DAY']}/{epe_data['MONTH']}/{epe_data['YEAR']}")
        print(f"  Coordinates: {epe_data['LATITUDE']}, {epe_data['LONGITUDE']}")
    else:
        print("❌ EPE parsing fallito")
        print(f"  Errore: {epe_result['error']}")
        return False
    
    print()
    
    # 2. Parsing con il nostro sistema
    print("=== PARSING NOSTRO SISTEMA ===")
    try:
        # Inizializza i servizi
        recognition_engine = RecognitionEngineImpl()
        skos_manager = SKOSManagerImpl()
        await skos_manager.load_version_model()
        
        # Riconoscimento versione
        recognition_result = await recognition_engine.recognize_version(euring_string)
        
        if recognition_result and recognition_result.detected_version:
            print(f"✅ Riconoscimento riuscito: {recognition_result.detected_version.id}")
            print(f"  Confidenza: {recognition_result.confidence:.2%}")
            
            # Se riconosciuto come EURING 2000, confronta i campi
            if recognition_result.detected_version.id == "euring_2000":
                print("  🎯 Versione corretta riconosciuta!")
                print("  📊 Confronto dettagliato dei campi non ancora implementato")
                print("  ✅ Test di riconoscimento versione: PASSATO")
                
            else:
                print(f"  ⚠️  Versione riconosciuta diversa: {recognition_result.detected_version.id}")
                print("  ❌ Test di riconoscimento versione: FALLITO")
                return False
        else:
            print("❌ Riconoscimento fallito")
            print("  Nessuna versione rilevata")
            return False
            
    except Exception as e:
        print(f"❌ Errore nel nostro sistema: {e}")
        return False
    
    print()
    return True

async def test_multiple_strings():
    """
    Testa multiple stringhe EURING
    """
    # Stringhe di test (quando arriveranno quelle reali, le sostituiremo)
    test_strings = [
        # Stringa EURING 2000 valida (94 caratteri)
        "IAB01ABC123456701ZZ12345123450010MM11300990150620231120012344512345012345671000010000000000000"
    ]
    
    print("🧪 Test di validazione EPE vs Sistema EURING")
    print("=" * 60)
    print()
    
    total_tests = len(test_strings)
    passed_tests = 0
    
    for i, test_string in enumerate(test_strings, 1):
        print(f"📋 Test {i}/{total_tests}")
        print("-" * 40)
        
        success = await compare_with_epe(test_string)
        if success:
            passed_tests += 1
        
        print()
    
    print("=" * 60)
    print(f"🏁 Risultati finali: {passed_tests}/{total_tests} test passati")
    
    if passed_tests == total_tests:
        print("🎉 Tutti i test sono passati!")
    else:
        print(f"⚠️  {total_tests - passed_tests} test falliti")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Esegui i test
    success = asyncio.run(test_multiple_strings())
    sys.exit(0 if success else 1)