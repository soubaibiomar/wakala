import json
import re

files = [
    r"d:\Projet automobile\vente-auto-platform\Livrables\Wakala_Architecture.excalidraw",
    r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_architecture_complete_explique.excalidraw",
    r"d:\Projet automobile\vente-auto-platform\Livrables\wakala_architecture_complete_technique.excalidraw"
]

replacements = [
    (r"(?i)\bGPT-4\b", "OpenRouter cloud model"),
    (r"(?i)\bGPT 4\b", "OpenRouter cloud model"),
    (r"(?i)\bLlama 3\.3\b", "OpenRouter fallback model"),
    (r"(?i)\bLlama\b", "OpenRouter model"),
    (r"(?i)\bGroq\b", "OpenRouter"),
    (r"(?i)\bOpenAI\b", "OpenRouter")
]

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        modified = False
        for element in data.get("elements", []):
            if element.get("type") == "text":
                original_text = element.get("text", "")
                new_text = original_text
                for pattern, repl in replacements:
                    new_text = re.sub(pattern, repl, new_text)
                
                if new_text != original_text:
                    element["text"] = new_text
                    element["originalText"] = new_text # Some versions of excalidraw use this
                    modified = True
                    print(f"[{filepath}] Replaced:\n  '{original_text}'\n  -> '{new_text}'")
                    
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved {filepath}")
        else:
            print(f"No changes in {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
