
import sys
import os
from datetime import date
from decimal import Decimal

# Add backend to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def test_avoir_classification():
    print("--- Testing Avoir Classification Logic ---")
    
    def _clean_name(name: str) -> str:
        import re
        if not name: return ""
        cleaned = name.strip().upper()
        # Same regex as in pipeline.py
        cleaned = re.sub(r'\b(STE|SARL|S\.A\.R\.L|SA|S\.A|EURL|E\.U\.R\.L|SPRL|S\.P\.R\.L|LLC|CORP|INC|LTD|SRL)\b', '', cleaned)
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()

    # Society Context
    societe_ice = "002012861000010"
    societe_nom = "STE Comptoire Arrahma S.A.R.L"
    raison_social_clean = _clean_name(societe_nom)

    # Test Case: User's Avoir
    # Supplier is Comptoire Arrahma (US)
    # Client is BTP Atlas (THEM)
    # This should be AVOIR_VENTE
    print("Case 1: User Credit Note (We are the supplier)")
    supplier_ice = "002012861000010"
    supplier_name = "STE Comptoire Arrahma S.A.R.L"
    client_name = "Société BTP Atlas"
    client_ice = "999999999999999"
    
    gemini_type = "AVOIR"
    client_name_clean = _clean_name(client_name)
    supplier_name_clean = _clean_name(supplier_name)

    res_type = "UNKNOWN"
    if gemini_type == "AVOIR":
        if (societe_ice and client_ice and societe_ice == client_ice) or \
           (client_name_clean and raison_social_clean and raison_social_clean in client_name_clean):
            res_type = "AVOIR_ACHAT"
        elif (societe_ice and supplier_ice and societe_ice == supplier_ice) or \
             (supplier_name_clean and raison_social_clean and raison_social_clean in supplier_name_clean):
            res_type = "AVOIR_VENTE"
    
    print(f"Result: {res_type} (Expected: AVOIR_VENTE)")
    assert res_type == "AVOIR_VENTE"

    # Test Case 2: Purchase Avoir
    # Supplier is someone else
    # Client is US
    print("\nCase 2: Purchase Credit Note (We are the client)")
    supplier_ice = "111111111111111"
    supplier_name = "Fournisseur X"
    client_name = "STE Comptoire Arrahma S.A.R.L"
    client_ice = "002012861000010"
    
    client_name_clean = _clean_name(client_name)
    supplier_name_clean = _clean_name(supplier_name)

    res_type = "UNKNOWN"
    if gemini_type == "AVOIR":
        if (societe_ice and client_ice and societe_ice == client_ice) or \
           (client_name_clean and raison_social_clean and raison_social_clean in client_name_clean):
            res_type = "AVOIR_ACHAT"
        elif (societe_ice and supplier_ice and societe_ice == supplier_ice) or \
             (supplier_name_clean and raison_social_clean and raison_social_clean in supplier_name_clean):
            res_type = "AVOIR_VENTE"
            
    print(f"Result: {res_type} (Expected: AVOIR_ACHAT)")
    assert res_type == "AVOIR_ACHAT"
    print("✅ Classification Logic Tests Passed!")

if __name__ == "__main__":
    try:
        test_avoir_classification()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
