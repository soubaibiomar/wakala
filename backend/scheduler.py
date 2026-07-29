import time
import subprocess
from datetime import datetime

def run_job():
    print(f"\n[{datetime.now()}] 🚀 Démarrage du cycle de scraping...")
    
    scripts = [
        "seed_real_moteur.py",
        "seed_real_otoclic.py",
        "seed_real_avito.py",
        "seed_real_kifal.py",
        "seed_real_wandaloo.py",
    ]
    
    sync_scripts = [
        "sync_postgres_to_neo4j.py",
        "sync_postgres_to_qdrant.py"
    ]
    
    for script in scripts:
        print(f"[{datetime.now()}] Lancement de {script}...")
        subprocess.run(["python", script])
        
    for script in sync_scripts:
        print(f"[{datetime.now()}] Lancement de la synchro {script}...")
        subprocess.run(["python", script])
        
    print(f"[{datetime.now()}] ✅ Cycle terminé.")

if __name__ == "__main__":
    interval_minutes = 60
    print(f"🕒 Planificateur démarré. Exécution toutes les {interval_minutes} minutes.")
    
    while True:
        try:
            run_job()
        except Exception as e:
            print(f"Erreur lors de l'exécution du batch : {e}")
            
        print(f"💤 En attente de {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)
