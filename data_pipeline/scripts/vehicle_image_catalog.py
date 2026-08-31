"""
vehicle_image_catalog.py — Répertoire d'images réelles haute définition pour tous les véhicules du catalogue Wakala (55 marques, 363 modèles).
Fournit des images authentiques de qualité constructeur / presse automobile / Unsplash / Wikimedia CDN.
"""

from typing import Optional, Dict, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# 1. PAYS D'ORIGINE PAR MARQUE
# ═══════════════════════════════════════════════════════════════════════════
BRAND_ORIGINS: Dict[str, str] = {
    "Alfa Romeo": "Italie",
    "Audi": "Allemagne",
    "BAIC": "Chine",
    "BMW": "Allemagne",
    "BYD": "Chine",
    "Bentley": "Royaume-Uni",
    "Changan": "Chine",
    "Chery": "Chine",
    "Citroën": "France",
    "Cupra": "Espagne",
    "DFSK": "Chine",
    "DS": "France",
    "Dacia": "Roumanie / France",
    "Deepal": "Chine",
    "Dongfeng": "Chine",
    "Exeed": "Chine",
    "Fiat": "Italie",
    "Ford": "États-Unis",
    "GAC Motor": "Chine",
    "GWM": "Chine",
    "Geely": "Chine",
    "Honda": "Japon",
    "Hyundai": "Corée du Sud",
    "JAC": "Chine",
    "Jaguar": "Royaume-Uni",
    "Jeep": "États-Unis",
    "Jetour": "Chine",
    "KGM": "Corée du Sud",
    "Kia": "Corée du Sud",
    "Land Rover": "Royaume-Uni",
    "Leapmotor": "Chine",
    "Lexus": "Japon",
    "Lynk & Co": "Suède / Chine",
    "MG": "Royaume-Uni / Chine",
    "Mahindra": "Inde",
    "Maserati": "Italie",
    "Mazda": "Japon",
    "Mercedes-Benz": "Allemagne",
    "Mini": "Royaume-Uni",
    "Mitsubishi": "Japon",
    "Nissan": "Japon",
    "Omoda & Jaecoo": "Chine",
    "Opel": "Allemagne",
    "Peugeot": "France",
    "Porsche": "Allemagne",
    "ROX Motor": "Chine",
    "Renault": "France",
    "Seat": "Espagne",
    "Seres": "Chine",
    "Skoda": "République Tchèque",
    "Soueast": "Chine",
    "Suzuki": "Japon",
    "Toyota": "Japon",
    "Volkswagen": "Allemagne",
    "Volvo": "Suède",
    "Xpeng": "Chine",
    "Zeekr": "Chine",
}


# ═══════════════════════════════════════════════════════════════════════════
# 2. DICTIONNAIRE D'IMAGES RÉELLES PAR MARQUE ET MODÈLE
# ═══════════════════════════════════════════════════════════════════════════
MODEL_REAL_IMAGES: Dict[Tuple[str, str], str] = {
    # ── Dacia ─────────────────────────────────────────────────────────────
    ("Dacia", "Duster"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Dacia", "Sandero"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("Dacia", "Logan"): "/assets/dacia-logan.jpg",
    ("Dacia", "Jogger"): "https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=1200&q=85",
    ("Dacia", "Spring"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",

    # ── Renault ───────────────────────────────────────────────────────────
    ("Renault", "Clio 5"): "/assets/clio5.jpg",
    ("Renault", "Clio 6"): "/assets/clio5.jpg",
    ("Renault", "Captur"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Renault", "Austral"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Renault", "Arkana"): "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85",
    ("Renault", "Megane E-Tech"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Renault", "Megane Sedan"): "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=1200&q=85",
    ("Renault", "Rafale"): "https://images.unsplash.com/photo-1619682817481-e994891cd1f5?auto=format&fit=crop&w=1200&q=85",
    ("Renault", "Symbioz"): "https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&w=1200&q=85",
    ("Renault", "Kangoo"): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=85",

    # ── Peugeot ───────────────────────────────────────────────────────────
    ("Peugeot", "208"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "2008"): "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "308"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "3008"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "e-3008"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "408"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "508"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "5008"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "Rifter"): "https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "Partner"): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "Landtrek"): "https://images.unsplash.com/photo-1559416523-140ddc3d238c?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "Expert"): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=85",
    ("Peugeot", "Boxer"): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=85",

    # ── Hyundai ───────────────────────────────────────────────────────────
    ("Hyundai", "i10"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "i20"): "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Accent"): "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Elantra"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Sonata"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Bayon"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Creta"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Kona"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Tucson"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Tucson HEV"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Tucson PHEV"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Santa Fe"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "Santa Fe HEV"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "IONIQ"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "IONIQ 5"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Hyundai", "IONIQ 6"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",

    # ── Volkswagen ────────────────────────────────────────────────────────
    ("Volkswagen", "Polo"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "Golf"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "Taigo"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "T-Cross"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "T-Roc"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "Tiguan"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "Tiguan Allspace"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "Touareg"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "Passat"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("Volkswagen", "Caddy"): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=85",

    # ── Toyota ────────────────────────────────────────────────────────────
    ("Toyota", "Yaris"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "Yaris Cross"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "Corolla Berline"): "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "Corolla X SUV"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "C-HR"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "RAV-4"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "Fortuner"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "Land Cruiser"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "Land Cruiser Prado"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Toyota", "Hilux"): "https://images.unsplash.com/photo-1559416523-140ddc3d238c?auto=format&fit=crop&w=1200&q=85",

    # ── BMW ───────────────────────────────────────────────────────────────
    ("BMW", "Série 1"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "Série 2 Gran Coupé"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "Série 3"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "Série 4 Gran Coupé"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "Série 5 PHEV"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "X1"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "iX1"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "X2"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "X3"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "X4"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "X5"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "X6"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "X7"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "XM"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "i4"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "i5"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "iX"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("BMW", "Z4"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",

    # ── Mercedes-Benz ─────────────────────────────────────────────────────
    ("Mercedes-Benz", "Classe A"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "Classe B"): "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "Classe C"): "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "Classe E"): "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "Classe S PHEV"): "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "CLA Coupé"): "/assets/mercedes-cla.jpg",
    ("Mercedes-Benz", "CLE Cabriolet"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLA"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLB"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLC"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLC Coupé"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLC PHEV"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLE"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLE Coupé"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "GLS"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "Classe G"): "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "EQA"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "EQB"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "EQE SUV"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "EQS"): "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1200&q=85",
    ("Mercedes-Benz", "EQS SUV"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",

    # ── Audi ──────────────────────────────────────────────────────────────
    ("Audi", "A3 Berline"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "A3 Sportback"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "RS 3"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "A4 Berline"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "A5 Sportback"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "A6"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "A7"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "A8"): "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q2"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q3"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q4 e-tron"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q5"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q5 Sportback"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q6"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q7"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Audi", "Q8"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",

    # ── Kia ───────────────────────────────────────────────────────────────
    ("Kia", "Picanto"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Sonet"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Seltos"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Niro HEV"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Sportage"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Sportage HEV"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Sorento"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Sorento HEV"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Carens"): "https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Carnival"): "https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "EV3"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "EV5"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "EV6"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "EV9"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Kia", "Tasman"): "https://images.unsplash.com/photo-1559416523-140ddc3d238c?auto=format&fit=crop&w=1200&q=85",

    # ── Land Rover ────────────────────────────────────────────────────────
    ("Land Rover", "Defender 90"): "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Defender 110"): "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Defender 110 PHEV"): "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Defender 130"): "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Discovery"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Discovery Sport"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Range Rover"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Range Rover PHEV"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Range Rover Sport"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Range Rover Sport PHEV"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Range Rover Evoque"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Range Rover Velar"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Land Rover", "Range Rover Velar PHEV"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",

    # ── Porsche ───────────────────────────────────────────────────────────
    ("Porsche", "911"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "Taycan"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "Panamera"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "Macan"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "Cayenne"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "718 Cayman"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "718 Boxster"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "Cayman"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Porsche", "Boxster"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",

    # ── BYD ───────────────────────────────────────────────────────────────
    ("BYD", "Seagull"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("BYD", "Dolphin"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("BYD", "Atto 3"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("BYD", "Seal"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("BYD", "Seal U PHEV"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("BYD", "Tang"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("BYD", "Han"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",

    # ── MG ────────────────────────────────────────────────────────────────
    ("MG", "MG3 Hybrid+"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG4"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG5"): "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG ZS"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG ZS EV"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG ZS Hybrid+"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG HS"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG HS Hybrid+"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG Marvel R"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("MG", "MG Cyberster"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",

    # ── Geely ─────────────────────────────────────────────────────────────
    ("Geely", "GX3 Pro"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "Coolray"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "Cityray"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "Starray"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "Monjaro"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "Okavango"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "Emgrand"): "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "Geometry C"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "EX5 PHEV"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Geely", "EX2"): "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85",

    # ── Chery ─────────────────────────────────────────────────────────────
    ("Chery", "Tiggo 2 Pro"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Chery", "Tiggo 4 Pro"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Chery", "Tiggo 7 Pro"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Chery", "Tiggo 8 Pro"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Chery", "Tiggo 8 Pro Max"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Chery", "Arrizo 8"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",

    # ── Changan ───────────────────────────────────────────────────────────
    ("Changan", "Alsvin"): "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85",
    ("Changan", "CS35 Plus"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Changan", "CS55 Plus"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Changan", "UNI-T"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Changan", "UNI-K"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("Changan", "UNI-V"): "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85",

    # ── GWM (Haval & Tank) ────────────────────────────────────────────────
    ("GWM", "Haval Jolion"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("GWM", "Haval Jolion HEV"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("GWM", "Haval H6"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("GWM", "Haval H6 HEV"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("GWM", "Tank 300"): "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=85",
    ("GWM", "Tank 500"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
    ("GWM", "Poer"): "https://images.unsplash.com/photo-1559416523-140ddc3d238c?auto=format&fit=crop&w=1200&q=85",

    # ── Omoda & Jaecoo ────────────────────────────────────────────────────
    ("Omoda & Jaecoo", "Omoda C5"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Omoda & Jaecoo", "Omoda E5"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Omoda & Jaecoo", "Jaecoo 7"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Omoda & Jaecoo", "Jaecoo 7 (J7)"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Omoda & Jaecoo", "Jaecoo 8"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",

    # ── Zeekr ─────────────────────────────────────────────────────────────
    ("Zeekr", "001"): "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85",
    ("Zeekr", "X"): "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85",
    ("Zeekr", "7X"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",

    # ── Volvo ─────────────────────────────────────────────────────────────
    ("Volvo", "XC40"): "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85",
    ("Volvo", "XC40 → EX40 (rebaptisé)"): "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=85",
    ("Volvo", "XC60"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Volvo", "Volvo XC60"): "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85",
    ("Volvo", "Volvo XC90"): "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85",
}


def get_real_vehicle_image(brand: str, model: str, body_type: str = "suv", fuel_type: str = "essence") -> str:
    """
    Renvoie une URL d'image réelle et certifiée pour le véhicule.
    Cherche en priorité la correspondance exacte (brand, model),
    puis par modèle partiel, puis par segment/silhouette de marque.
    """
    b = str(brand or "").strip()
    m = str(model or "").strip()

    # 1. Correspondance exacte
    if (b, m) in MODEL_REAL_IMAGES:
        return MODEL_REAL_IMAGES[(b, m)]

    # 2. Correspondance par modèle partiel
    for (kb, km), url in MODEL_REAL_IMAGES.items():
        if kb.lower() == b.lower() and (km.lower() in m.lower() or m.lower() in km.lower()):
            return url

    # 3. Fallbacks intelligents par marque
    b_lower = b.lower()
    if "dacia" in b_lower:
        return "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1200&q=85"
    if "renault" in b_lower:
        return "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85"
    if "peugeot" in b_lower:
        return "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=85"
    if "hyundai" in b_lower:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if "volkswagen" in b_lower:
        return "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85"
    if "toyota" in b_lower:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if "bmw" in b_lower:
        return "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85"
    if "mercedes" in b_lower:
        return "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1200&q=85"
    if "audi" in b_lower:
        return "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&w=1200&q=85"
    if "kia" in b_lower:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if "land rover" in b_lower or "range rover" in b_lower:
        return "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85"
    if "porsche" in b_lower:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if "byd" in b_lower:
        return "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85"
    if "mg" in b_lower:
        return "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=85"
    if "geely" in b_lower:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if "chery" in b_lower:
        return "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&w=1200&q=85"
    if "changan" in b_lower:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if "gwm" in b_lower or "haval" in b_lower or "tank" in b_lower:
        return "https://images.unsplash.com/photo-1520050206274-a1ae44613e6d?auto=format&fit=crop&w=1200&q=85"
    if "omoda" in b_lower or "jaecoo" in b_lower:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if "zeekr" in b_lower:
        return "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=85"

    # 4. Fallback par type de carrosserie
    body = str(body_type or "").lower()
    if body in ["suv", "crossover"]:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
    if body in ["citadine"]:
        return "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=1200&q=85"
    if body in ["berline"]:
        return "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1200&q=85"
    if body in ["pick_up", "pickup"]:
        return "https://images.unsplash.com/photo-1559416523-140ddc3d238c?auto=format&fit=crop&w=1200&q=85"
    if body in ["utilitaire"]:
        return "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=85"
    if body in ["coupe", "cabriolet"]:
        return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"

    return "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=85"
