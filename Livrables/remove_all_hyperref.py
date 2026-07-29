import os
import glob

directory = "D:/Projet automobile/vente-auto-platform/Livrables/"
tex_files = glob.glob(os.path.join(directory, "*.tex"))

for filepath in tex_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "\\usepackage{hyperref}" in content:
        content = content.replace("\\usepackage{hyperref}", "% \\usepackage{hyperref}")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Removed hyperref from {filepath}")
