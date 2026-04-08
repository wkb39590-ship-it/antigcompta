import os
import sys
import json

os.chdir("/app")
sys.path.append("/app")

from services.gemini_service import classify_product_pcm

def test_classification():
    descriptions = [
        "KONOUZ SILVER 01 20KG + GLITER",
        "SUPERSARAVINYL V10+ 30KG",
        "ENDUIT PATE SARA 2000 25KG",
        "VERNIS DIVA NACRE SILVER 100 G"
    ]
    
    print("Testing classification...\n")
    for desc in descriptions:
        result = classify_product_pcm(desc, amount=1000.0, invoice_type="ACHAT")
        print(f"Product: {desc}")
        print(f"Classification: {json.dumps(result, indent=2, ensure_ascii=False)}")
        print("-" * 50)

if __name__ == "__main__":
    test_classification()
