import os

files = [
    "D:/Projet automobile/vente-auto-platform/Livrables/idees-fonctionnelles.tex",
    "D:/Projet automobile/vente-auto-platform/Livrables/benchmark-concurrentiel.tex",
    "D:/Projet automobile/vente-auto-platform/Livrables/wakala_etude_utilisateurs.tex",
    "D:/Projet automobile/vente-auto-platform/Livrables/wakala_usability_report.tex"
]

for fpath in files:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace("\\usepackage[french]{babel}", "% \\usepackage[french]{babel}")
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Removed babel from {fpath}")
