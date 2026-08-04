import asyncio
import json
import os
from app.ml.nlp_pipeline.llm_extractor import extract_search_criteria

async def test_dataset():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "tests", "dataset_test.json")
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    errors = 0
    for item in dataset:
        texte = item["texte"]
        expected = item["expected"]
        
        result = await extract_search_criteria(texte)
        
        print(f"Phrase: {texte}")
        print(f"Attendu: langue_principale={expected.get('langue_principale')}, melange={expected.get('melange_langues')}")
        print(f"Obtenu:  langue_principale={result.langue_principale}, melange={result.melange_langues}")
        
        if result.langue_principale != expected.get("langue_principale"):
            print("ERREUR: langue_principale incorrecte!")
            errors += 1
            
        print("-" * 40)
        
    if errors > 0:
        print(f"Tests échoués: {errors} erreurs.")
        exit(1)
    else:
        print("Tous les tests passent avec succès !")
        exit(0)

if __name__ == "__main__":
    asyncio.run(test_dataset())
