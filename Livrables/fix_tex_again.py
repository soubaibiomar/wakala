import os

filepath = "D:/Projet automobile/vente-auto-platform/Livrables/idees-fonctionnelles.tex"
if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("\\usepackage{hyperref}", "% \\usepackage{hyperref}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Removed hyperref from idees-fonctionnelles.tex")
