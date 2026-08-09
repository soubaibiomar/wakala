import json, uuid, random

def rid():
    return uuid.uuid4().hex[:20]

els = []

def nonce():
    return random.randint(100000000, 2147483647)

def R(eid, x, y, w, h, stroke="#495057", bg="#e9ecef", sw=1, ss="solid"):
    els.append({"id":eid,"type":"rectangle","x":x,"y":y,"width":w,"height":h,
        "angle":0,"strokeColor":stroke,"backgroundColor":bg,
        "fillStyle":"solid","strokeWidth":sw,"strokeStyle":ss,
        "roughness":1,"opacity":100,"groupIds":[],"roundness":{"type":3},
        "seed":random.randint(1,999999),"version":2,"versionNonce":nonce(),
        "isDeleted":False,"boundElements":[],"updated":1785264572634,
        "link":None,"locked":False,"frameId":None})

def T(eid, x, y, text, fs=16, color="#343a40", ta="left", w=None, h=None):
    lines=text.split("\n")
    cw=w or max(len(l)*fs*0.6 for l in lines)
    ch=h or len(lines)*fs*1.25
    els.append({"id":eid,"type":"text","x":x,"y":y,"width":cw,"height":ch,
        "angle":0,"strokeColor":color,"backgroundColor":"transparent",
        "fillStyle":"solid","strokeWidth":1,"strokeStyle":"solid",
        "roughness":1,"opacity":100,"groupIds":[],"roundness":None,
        "seed":random.randint(1,999999),"version":2,"versionNonce":nonce(),
        "isDeleted":False,"boundElements":[],"updated":1785264572634,
        "link":None,"locked":False,"text":text,"fontSize":fs,"fontFamily":1,
        "textAlign":ta,"verticalAlign":"top","baseline":int(fs*0.87),
        "containerId":None,"originalText":text,"frameId":None,
        "autoResize":True,"lineHeight":1.25})

def A(eid, x1, y1, x2, y2, color="#495057", ss="solid", sw=1):
    els.append({"id":eid,"type":"arrow","x":x1,"y":y1,
        "width":abs(x2-x1),"height":abs(y2-y1),
        "angle":0,"strokeColor":color,"backgroundColor":"transparent",
        "fillStyle":"solid","strokeWidth":sw,"strokeStyle":ss,
        "roughness":1,"opacity":100,"groupIds":[],"roundness":{"type":2},
        "seed":random.randint(1,999999),"version":2,"versionNonce":nonce(),
        "isDeleted":False,"boundElements":[],"updated":1785264572634,
        "link":None,"locked":False,"startBinding":None,"endBinding":None,
        "lastCommittedPoint":None,"startArrowhead":None,"endArrowhead":"arrow",
        "points":[[0,0],[x2-x1,y2-y1]],"frameId":None})

def L(eid, x1, y1, x2, y2, color="#495057", ss="solid", sw=1):
    """Line without arrowhead — for tree branches."""
    els.append({"id":eid,"type":"line","x":x1,"y":y1,
        "width":abs(x2-x1) or 1,"height":abs(y2-y1) or 1,
        "angle":0,"strokeColor":color,"backgroundColor":"transparent",
        "fillStyle":"solid","strokeWidth":sw,"strokeStyle":ss,
        "roughness":1,"opacity":100,"groupIds":[],"roundness":{"type":2},
        "seed":random.randint(1,999999),"version":2,"versionNonce":nonce(),
        "isDeleted":False,"boundElements":[],"updated":1785264572634,
        "link":None,"locked":False,
        "lastCommittedPoint":None,"startArrowhead":None,"endArrowhead":None,
        "points":[[0,0],[x2-x1,y2-y1]],"frameId":None})

def E(eid, x, y, w, h, stroke="#495057", bg="#e9ecef", sw=1):
    """Ellipse / circle shape for illustrations."""
    els.append({"id":eid,"type":"ellipse","x":x,"y":y,"width":w,"height":h,
        "angle":0,"strokeColor":stroke,"backgroundColor":bg,
        "fillStyle":"solid","strokeWidth":sw,"strokeStyle":"solid",
        "roughness":1,"opacity":100,"groupIds":[],"roundness":{"type":2},
        "seed":random.randint(1,999999),"version":2,"versionNonce":nonce(),
        "isDeleted":False,"boundElements":[],"updated":1785264572634,
        "link":None,"locked":False,"frameId":None})

def D(eid, x, y, w, h, stroke="#495057", bg="#e9ecef", sw=1):
    """Diamond shape — rotated rectangle for illustrations."""
    els.append({"id":eid,"type":"diamond","x":x,"y":y,"width":w,"height":h,
        "angle":0,"strokeColor":stroke,"backgroundColor":bg,
        "fillStyle":"solid","strokeWidth":sw,"strokeStyle":"solid",
        "roughness":1,"opacity":100,"groupIds":[],"roundness":{"type":2},
        "seed":random.randint(1,999999),"version":2,"versionNonce":nonce(),
        "isDeleted":False,"boundElements":[],"updated":1785264572634,
        "link":None,"locked":False,"frameId":None})

# ── Illustration helpers ──────────────────────────────────────
# Small composed-shape visuals that replace emoji icons.

def illus_antenna(pfx, x, y, color="#e8590c"):
    """Satellite / signal illustration (3 arcs + base dot)."""
    E(f"{pfx}_dot", x+12, y+22, 8, 8, stroke=color, bg=color, sw=1)
    E(f"{pfx}_a1", x+4, y+10, 24, 18, stroke=color, bg="transparent", sw=1)
    E(f"{pfx}_a2", x-4, y+2, 40, 26, stroke=color, bg="transparent", sw=1)
    E(f"{pfx}_a3", x-10, y-4, 52, 32, stroke=color, bg="transparent", sw=1)

def illus_shield(pfx, x, y, color="#c92a2a"):
    """Shield illustration."""
    D(f"{pfx}_d", x, y, 32, 38, stroke=color, bg="#ffe3e3", sw=2)
    R(f"{pfx}_bar", x+13, y+14, 6, 12, stroke=color, bg=color, sw=1)

def illus_spider(pfx, x, y, color="#c2255c"):
    """Spider / web crawler illustration."""
    E(f"{pfx}_body", x+8, y+8, 16, 16, stroke=color, bg="#f3d9e4", sw=2)
    L(f"{pfx}_l1", x, y, x+8, y+8, color=color, sw=1)
    L(f"{pfx}_l2", x+32, y, x+24, y+8, color=color, sw=1)
    L(f"{pfx}_l3", x, y+32, x+8, y+24, color=color, sw=1)
    L(f"{pfx}_l4", x+32, y+32, x+24, y+24, color=color, sw=1)
    L(f"{pfx}_l5", x+16, y, x+16, y+8, color=color, sw=1)
    L(f"{pfx}_l6", x+16, y+32, x+16, y+24, color=color, sw=1)

def illus_funnel(pfx, x, y, color="#c2255c"):
    """Funnel / filter illustration."""
    L(f"{pfx}_lt", x, y, x+14, y+18, color=color, sw=2)
    L(f"{pfx}_rt", x+30, y, x+16, y+18, color=color, sw=2)
    L(f"{pfx}_ls", x+14, y+18, x+14, y+32, color=color, sw=2)
    L(f"{pfx}_rs", x+16, y+18, x+16, y+32, color=color, sw=2)
    L(f"{pfx}_top", x, y, x+30, y, color=color, sw=2)

def illus_brain(pfx, x, y, color="#5f3dc4"):
    """Brain / AI illustration (overlapping circles)."""
    E(f"{pfx}_c1", x, y+4, 18, 20, stroke=color, bg="#e5dbff", sw=1)
    E(f"{pfx}_c2", x+12, y+4, 18, 20, stroke=color, bg="#e5dbff", sw=1)
    E(f"{pfx}_c3", x+4, y, 22, 14, stroke=color, bg="#d0bfff", sw=1)
    L(f"{pfx}_s1", x+15, y+10, x+15, y+32, color=color, sw=1)

def illus_cylinder(pfx, x, y, color="#f08c00"):
    """Database cylinder illustration."""
    R(f"{pfx}_body", x+2, y+8, 28, 22, stroke=color, bg="#fff9db", sw=1)
    E(f"{pfx}_top", x+2, y, 28, 16, stroke=color, bg="#fff9db", sw=2)
    E(f"{pfx}_bot", x+2, y+22, 28, 16, stroke=color, bg="#fff9db", sw=1)

def illus_monitor(pfx, x, y, color="#2b8a3e"):
    """Monitor / screen illustration."""
    R(f"{pfx}_scr", x, y, 32, 22, stroke=color, bg="#d3f9d8", sw=2)
    R(f"{pfx}_st", x+12, y+22, 8, 6, stroke=color, bg="#adb5bd", sw=1)
    R(f"{pfx}_bs", x+6, y+28, 20, 4, stroke=color, bg="#adb5bd", sw=1)

def illus_gear(pfx, x, y, color="#1864ab"):
    """Gear / settings illustration."""
    E(f"{pfx}_outer", x, y, 32, 32, stroke=color, bg="#d0ebff", sw=2)
    E(f"{pfx}_inner", x+10, y+10, 12, 12, stroke=color, bg="#ffffff", sw=2)
    R(f"{pfx}_t1", x+13, y-2, 6, 8, stroke=color, bg=color, sw=1)
    R(f"{pfx}_t2", x+13, y+26, 6, 8, stroke=color, bg=color, sw=1)
    R(f"{pfx}_t3", x-2, y+13, 8, 6, stroke=color, bg=color, sw=1)
    R(f"{pfx}_t4", x+26, y+13, 8, 6, stroke=color, bg=color, sw=1)

def illus_lock(pfx, x, y, color="#343a40"):
    """Padlock illustration."""
    R(f"{pfx}_body", x+4, y+14, 24, 18, stroke=color, bg="#e9ecef", sw=2)
    E(f"{pfx}_shackle", x+8, y, 16, 18, stroke=color, bg="transparent", sw=2)
    E(f"{pfx}_hole", x+13, y+19, 6, 6, stroke=color, bg=color, sw=1)

def illus_chat(pfx, x, y, color="#a61e4d"):
    """Chat bubble illustration."""
    R(f"{pfx}_bbl", x, y, 30, 22, stroke=color, bg="#fff0f6", sw=2)
    L(f"{pfx}_t1", x+6, y+22, x+4, y+30, color=color, sw=2)
    L(f"{pfx}_t2", x+4, y+30, x+14, y+22, color=color, sw=2)
    R(f"{pfx}_d1", x+6, y+8, 18, 3, stroke=color, bg=color, sw=1)
    R(f"{pfx}_d2", x+6, y+14, 12, 3, stroke=color, bg=color, sw=1)

def illus_tree_icon(pfx, x, y, color="#2b8a3e"):
    """Small tree / hierarchy illustration."""
    E(f"{pfx}_root", x+10, y, 12, 12, stroke=color, bg=color, sw=1)
    L(f"{pfx}_s", x+16, y+12, x+16, y+18, color=color, sw=2)
    L(f"{pfx}_bar", x+2, y+18, x+30, y+18, color=color, sw=2)
    L(f"{pfx}_d1", x+2, y+18, x+2, y+26, color=color, sw=1)
    L(f"{pfx}_d2", x+16, y+18, x+16, y+26, color=color, sw=1)
    L(f"{pfx}_d3", x+30, y+18, x+30, y+26, color=color, sw=1)
    E(f"{pfx}_n1", x-2, y+26, 8, 8, stroke=color, bg=color, sw=1)
    E(f"{pfx}_n2", x+12, y+26, 8, 8, stroke=color, bg=color, sw=1)
    E(f"{pfx}_n3", x+26, y+26, 8, 8, stroke=color, bg=color, sw=1)

def illus_doc(pfx, x, y, color="#868e96"):
    """Document / schema illustration."""
    R(f"{pfx}_pg", x, y, 26, 32, stroke=color, bg="#f8f9fa", sw=2)
    R(f"{pfx}_ln1", x+5, y+6, 16, 3, stroke=color, bg=color, sw=1)
    R(f"{pfx}_ln2", x+5, y+12, 14, 3, stroke=color, bg=color, sw=1)
    R(f"{pfx}_ln3", x+5, y+18, 16, 3, stroke=color, bg=color, sw=1)
    R(f"{pfx}_ln4", x+5, y+24, 10, 3, stroke=color, bg=color, sw=1)

def illus_component(pfx, x, y, color="#862e9c"):
    """Component / puzzle piece illustration."""
    R(f"{pfx}_bx", x, y+6, 28, 22, stroke=color, bg="#f8f0fc", sw=2)
    R(f"{pfx}_tab", x+8, y, 12, 10, stroke=color, bg="#e5dbff", sw=1)

def illus_state(pfx, x, y, color="#0c8599"):
    """State / data flow illustration."""
    E(f"{pfx}_c", x+4, y+4, 24, 24, stroke=color, bg="#e3fafc", sw=2)
    A(f"{pfx}_arr", x+10, y+16, x+24, y+16, color=color, sw=1)
    R(f"{pfx}_dot", x+14, y+12, 4, 8, stroke=color, bg=color, sw=1)


# ══════════════════════════════════════════════════════════════
# Layout: 4 major sections stacked vertically, wide canvas
# Section 1: SCRAPING   Y: 100-1650
# Section 2: BACKEND    Y: 1750-3800
# Section 3: DATABASE   Y: 3900-4600
# Section 4: FRONTEND   Y: 4700-7000
# ══════════════════════════════════════════════════════════════

CX = 100   # Canvas left margin
CW = 2200  # Canvas width


# ══════════════════════════════════════════════════════════════
# MAIN TITLE
# ══════════════════════════════════════════════════════════════
T("t0", CX, 20, "WAKALA -- Architecture Complete : Deep Dive", fs=36, color="#1e1e1e")
T("t0b", CX, 65, "Schema detaille du flux complet : Scraping -> Backend -> Database -> Interface Acheteur", fs=16, color="#868e96")
T("t0c", CX+1400, 65, "Plateforme : vente-auto-platform   |   Stack : FastAPI + React + PostgreSQL + Qdrant + Neo4j", fs=12, color="#adb5bd")


# ══════════════════════════════════════════════════════════════
# SECTION 1 — SCRAPING & DATA INGESTION
# ══════════════════════════════════════════════════════════════
R("s1_bg", CX-20, 100, CW+40, 1550, stroke="#e8590c", bg="#fffef5", sw=2, ss="dashed")
T("s1_title", CX+40, 110, "PARTIE 1 -- SCRAPING & DATA INGESTION", fs=26, color="#e8590c")
T("s1_desc", CX, 145, "En bref : Nos robots parcourent internet pour rassembler toutes les voitures a vendre au Maroc au meme endroit.\nTechnique : Collecte automatisee (Scraping) depuis 7 plateformes. Chaque scraper gere l'extraction, le nettoyage, et l'envoi vers notre serveur.", fs=13, color="#495057")

# [illustration] antenna before sub-section title
illus_antenna("ill_src", CX+10, 220, color="#d9480f")

# --- Sources Web (7 platforms) ---
T("s1a_label", CX+50, 228, "SOURCES WEB (7 plateformes)", fs=18, color="#d9480f")
T("s1a_label_desc", CX+50, 248, "Ce sont les sites d'ou proviennent les annonces de voitures (neuves et occasions).", fs=12, color="#d9480f")

R("src1", CX+20, 270, 280, 110, stroke="#f08c00", bg="#fff9db")
T("ts1", CX+30, 280, "Wandaloo (Neuf + Occasion)", fs=14, color="#5c3c00")
T("ts1b", CX+30, 305, "URL: /neuf/prix-voiture-neuve-maroc.html\nSelecteur: h3.titre > a + p.prix\n117 modeles neufs + annonces occasion\nPas de pagination (page unique)", fs=11, color="#495057")

R("src2", CX+320, 270, 280, 110, stroke="#f08c00", bg="#fff9db")
T("ts2", CX+330, 280, "Moteur.ma (Neuf + Occasion)", fs=14, color="#5c3c00")
T("ts2b", CX+330, 305, "Selecteur: div.card-listing\nPagination: ?page=N\nDonnees structurees par carte\nPrix en DH directement", fs=11, color="#495057")

R("src3", CX+620, 270, 280, 110, stroke="#f08c00", bg="#fff9db")
T("ts3", CX+630, 280, "Avito.ma (Occasion)", fs=14, color="#5c3c00")
T("ts3b", CX+630, 305, "React SSR partiel (classes sc-xxx)\nAnti-bot: Datadome/Cloudflare\nSelecteur: a[data-testid^=ad-card-v2]\nImages: content.avito.ma/classifieds/", fs=11, color="#495057")

R("src4", CX+920, 270, 280, 110, stroke="#f08c00", bg="#fff9db")
T("ts4", CX+930, 280, "Kifal Auto (Occasion)", fs=14, color="#5c3c00")
T("ts4b", CX+930, 305, "Marketplace automobile certifiee\nDonnees vendeur structurees\nPhotos professionnelles\nFlag certifie: True", fs=11, color="#495057")

R("src5", CX+1220, 270, 280, 110, stroke="#f08c00", bg="#fff9db")
T("ts5", CX+1230, 280, "Otoclic (Neuf)", fs=14, color="#5c3c00")
T("ts5b", CX+1230, 305, "Catalogue constructeur neuf\nFiches techniques completes\nPrix TTC catalogue officiel\nConfigurateur options", fs=11, color="#495057")

R("src6", CX+1520, 270, 280, 110, stroke="#f08c00", bg="#fff9db")
T("ts6", CX+1530, 280, "Spoticar (Occasion Certifie)", fs=14, color="#5c3c00")
T("ts6b", CX+1530, 305, "Vehicules d'occasion certifies\nGarantie constructeur\nPhotos standardisees\ncertifie=True par defaut", fs=11, color="#495057")

R("src7", CX+1820, 270, 280, 110, stroke="#f08c00", bg="#fff9db")
T("ts7", CX+1830, 280, "Global Occaz", fs=14, color="#5c3c00")
T("ts7b", CX+1830, 305, "Agregateur d'annonces occasion\nMulti-source consolide\nHistorique de prix\nDetection doublons", fs=11, color="#495057")

A("a_src", CX+1100, 380, CX+1100, 420, color="#e8590c", sw=2)

# --- Anti-Detection Layer ---
illus_shield("ill_shield", CX+10, 418, color="#c92a2a")
T("s1b_label", CX+50, 425, "ANTI-DETECTION LAYER (Masquage)", fs=18, color="#c92a2a")
T("s1b_label_desc", CX+50, 445, "Techniques pour ne pas se faire bloquer par les sites web (comme changer de navigateur virtuel).", fs=12, color="#c92a2a")

R("anti_bg", CX+20, 460, 2100, 100, stroke="#c92a2a", bg="#fff5f5")
T("anti_body", CX+30, 470,
  "anti_detection.py -> AntiDetectionSession\n"
  "User-Agent fixe Chrome 115 (Windows 10 x64)  |  Accept-Language: fr-FR,fr;q=0.9,en  |  Accept: text/html,xhtml+xml\n"
  "Delai aleatoire par requete: delay + random.uniform(0.5, 1.5) secondes  |  Timeout: 15s  |  Session persistante (cookies)", fs=12, color="#495057")

A("a_anti", CX+1100, 560, CX+1100, 600, color="#e8590c", sw=2)

# --- BaseScraper Abstract Class ---
illus_spider("ill_spider", CX+10, 595, color="#c2255c")
T("s1c_label", CX+50, 600, "BASE SCRAPER (Classe Abstraite)", fs=18, color="#c2255c")

R("bs_bg", CX+20, 640, 1050, 180, stroke="#e8590c", bg="#fff3e0")
T("bs_title", CX+30, 650, "class BaseScraper(ABC)", fs=16, color="#c2255c")
T("bs_body", CX+30, 680,
  "Attributs de classe:\n"
  "  platform_name: str    # ex: 'wandaloo', 'avito'\n"
  "  listing_type: str     # 'neuf' ou 'occasion'\n"
  "  base_url: str         # ex: 'https://www.wandaloo.com'\n\n"
  "Methodes abstraites:\n"
  "  @abstractmethod get_listing_urls(page: int) -> list[str]\n"
  "  @abstractmethod parse_listing(html: str, url: str) -> dict", fs=12, color="#495057")

R("bs_helpers", CX+1100, 640, 1020, 180, stroke="#e8590c", bg="#fff3e0")
T("bsh_title", CX+1110, 650, "Helpers Partages (anti-duplication)", fs=16, color="#c2255c")
T("bsh_body", CX+1110, 680,
  "_make_soup(html) -> BeautifulSoup\n"
  "  Cree un parser HTML5 a partir du HTML brut\n\n"
  "_absolute_url(href) -> str\n"
  "  Convertit les liens relatifs en URLs absolues\n\n"
  "_extract_text(soup, selectors[], default) -> str\n"
  "  Essaie N selecteurs CSS, retourne le 1er match\n\n"
  "_extract_images(soup, selectors[]) -> list[str]\n"
  "  Cherche src, data-src, data-lazy-src, deduplique\n\n"
  "_build_raw_listing(titre, prix, ...) -> dict\n"
  "  Construit le schema de sortie standardise", fs=11, color="#495057")

A("a_bs", CX+1100, 820, CX+1100, 870, color="#e8590c", sw=2)

# --- Data Cleaning ---
illus_funnel("ill_funnel", CX+10, 864, color="#c2255c")
T("s1d_label", CX+50, 870, "DATA CLEANING PIPELINE (Nettoyage)", fs=18, color="#c2255c")
T("s1d_label_desc", CX+50, 890, "L'usine de tri : On nettoie les prix, on supprime les annonces en double et on uniformise le texte.", fs=12, color="#c2255c")

R("cl_bg", CX+20, 910, 2100, 130, stroke="#e8590c", bg="#fff3e0")
T("cl_body", CX+30, 920,
  "Etape 1: Nettoyage Prix                                   Etape 2: Dedoublonnage                                    Etape 3: Normalisation\n"
  "'90.900 DH' -> re.sub(r'(\\d+)\\.(\\d{3})', '\\1 \\2')        Hash(titre+prix+ville) cross-platform                     Marque -> BRAND_KEYWORDS (30+ marques)\n"
  "'189 900 DH' -> float(189900)                              Suppression doublons intra et inter-sources                Carburant -> FUEL_KEYWORDS (essence, diesel...)\n"
  "Gestion formats: DH, MAD, k, millions                     Priorite: Certifie > Pro > Particulier                     Carrosserie -> BODY_KEYWORDS (citadine, SUV...)\n"
  "                                                                                                                       Transmission -> manuelle/automatique/semi_auto",
  fs=11, color="#495057")

A("a_cl", CX+1100, 1040, CX+1100, 1090, color="#e8590c", sw=2)

# --- NLP Feature Extraction ---
illus_brain("ill_brain1", CX+10, 1082, color="#5f3dc4")
T("s1e_label", CX+50, 1085, "NLP & FEATURE EXTRACTION", fs=18, color="#c2255c")
T("s1e_label_desc", CX+50, 1105, "L'IA lit le texte brut des annonces pour en extraire proprement la marque, le modele et le type de carburant.", fs=12, color="#c2255c")

R("nlp_bg", CX+20, 1120, 1050, 200, stroke="#7048e8", bg="#f3f0ff")
T("nlp_title", CX+30, 1130, "feature_extraction.py", fs=16, color="#5f3dc4")
T("nlp_body", CX+30, 1160,
  "Extraction d'entites depuis le texte brut:\n\n"
  "extract_brand(text)  -> Regex sur 30+ marques\n"
  "  'renault'->Renault, 'vw'->Volkswagen, 'mercedes'->Mercedes-Benz\n\n"
  "extract_fuel_type(text) -> Multilingue (FR+Darija)\n"
  "  'mazot'->diesel, 'lisans'->essence, 'ev'->electrique\n\n"
  "extract_body_type(text) -> Inclut Darija\n"
  "  'sghira'->citadine, 'kbira'->SUV, '3aila'->monospace\n\n"
  "PRICE_PATTERNS (5 regex) -> Budget min/max\n"
  "YEAR_PATTERNS (4 regex) -> Annee min/max",
  fs=11, color="#495057")

R("nlp2_bg", CX+1100, 1120, 1020, 200, stroke="#7048e8", bg="#f3f0ff")
T("nlp2_title", CX+1110, 1130, "Vectorisation & Embeddings", fs=16, color="#5f3dc4")
T("nlp2_body", CX+1110, 1160,
  "content_based.py -> Feature Vector (7 dimensions)\n"
  "  FEATURE_COLUMNS = [\n"
  "    price_norm, year_norm, mileage_norm,\n"
  "    body_type_encoded, transmission_encoded,\n"
  "    fuel_encoded, engine_power_norm\n"
  "  ]\n"
  "  Encodage ordinal: BODY_TYPE_ORDER (9 categories)\n"
  "  TRANSMISSION_MAP: manuelle=0, semi_auto=0.5, auto=1\n"
  "  FUEL_ORDER: essence->diesel->hybride->...->hydrogene\n\n"
  "embeddings.py -> Sentence Transformers\n"
  "  Modele: all-MiniLM-L6-v2 (384 dimensions)\n"
  "  Input: titre + description concatenes",
  fs=11, color="#495057")

A("a_nlp", CX+1100, 1320, CX+1100, 1370, color="#e8590c", sw=2)

# --- Output Schema ---
illus_doc("ill_schema", CX+10, 1358, color="#868e96")
T("s1f_label", CX+50, 1365, "SCHEMA DE SORTIE STANDARDISE", fs=18, color="#c2255c")

R("schema_bg", CX+20, 1400, 1050, 200, stroke="#868e96", bg="#f8f9fa")
T("schema_body", CX+30, 1410,
  '{\n'
  '  "source_plateforme": "wandaloo" | "avito" | "moteur" | ...,\n'
  '  "type_annonce":      "neuf" | "occasion",\n'
  '  "titre_brut":        "Dacia Sandero Stepway 2025 Diesel",\n'
  '  "prix_brut":         "189 900 DH",\n'
  '  "description_brute": "Moteur 1.5 dCi 85cv | BVM6 | Climatisation",\n'
  '  "photos_urls":       ["https://cdn.wandaloo.com/...", ...],  // max 10\n'
  '  "vendeur_info":      { "nom": "Auto Pro Casablanca", "ville": "Casablanca" },\n'
  '  "date_publication":  "2025-07-15T10:30:00Z" | null,\n'
  '  "url_source":        "https://www.wandaloo.com/neuf/dacia/sandero/",\n'
  '  "certifie":          false\n'
  '}',
  fs=12, color="#495057")

R("pipe_bg", CX+1100, 1400, 1020, 200, stroke="#e8590c", bg="#fff3e0")
T("pipe_title", CX+1110, 1410, "Pipeline d'Ingestion & Scheduling", fs=16, color="#c2255c")
T("pipe_body", CX+1110, 1440,
  "Ingestion vers le Backend:\n"
  "  POST /api/vehicles/batch  -> Insertion PostgreSQL\n"
  "  POST /api/v1/ai/embed     -> Generation embedding Qdrant\n\n"
  "Scheduler (Cron / APScheduler):\n"
  "  Frequence: toutes les 6 heures\n"
  "  Execution sequentielle par plateforme\n"
  "  Retry avec backoff exponentiel\n\n"
  "Health Checker (health_checker.py):\n"
  "  Verifie la disponibilite de chaque source\n"
  "  Logs dans scraper_health.log\n"
  "  Alerte si taux d'echec > 50%",
  fs=11, color="#495057")

# Big arrow: Scraping -> Backend
A("a_s2b", CX+1100, 1610, CX+1100, 1730, color="#e8590c", sw=3)
T("a_s2b_label", CX+1020, 1650, "POST /api/vehicles ->", fs=14, color="#e8590c")


# ══════════════════════════════════════════════════════════════
# SECTION 2 — BACKEND CORE
# ══════════════════════════════════════════════════════════════
R("s2_bg", CX-20, 1730, CW+40, 2050, stroke="#1971c2", bg="#f0f8ff", sw=2, ss="dashed")
illus_gear("ill_gear", CX+10, 1738, color="#1864ab")
T("s2_title", CX+50, 1740, "PARTIE 2 -- BACKEND CORE (FastAPI :8000)", fs=26, color="#1864ab")
T("s2_desc", CX, 1775, "En bref : C'est le cerveau du systeme. Il recoit les requetes de l'utilisateur, fait les calculs intelligents (IA), et gere la securite.\nTechnique : API REST FastAPI connectant nos bases de donnees, nos modules de Machine Learning et notre chatbot (RAG).", fs=13, color="#495057")


# ── ROUTES API — TREE LAYOUT ─────────────────────────────────
illus_tree_icon("ill_apitree", CX+10, 1840, color="#1864ab")
T("s2a_label", CX+50, 1845, "ROUTES API REST (18 Routers) -- Arbre Hierarchique", fs=18, color="#1864ab")
T("s2a_label_desc", CX+50, 1865, "Les differentes portes d'entree de notre serveur, classees par grandes categories.", fs=12, color="#1864ab")

# Root node
ROOT_X = CX + 850
ROOT_Y = 1890
ROOT_W = 360
ROOT_H = 38
R("rt_root", ROOT_X, ROOT_Y, ROOT_W, ROOT_H, stroke="#1864ab", bg="#1864ab", sw=2)
T("rt_root_t", ROOT_X+50, ROOT_Y+8, "FastAPI :8000 -- 18 API Routers", fs=16, color="#ffffff")

# Stem from root
ROOT_CX = ROOT_X + ROOT_W // 2
L("rt_stem", ROOT_CX, ROOT_Y + ROOT_H, ROOT_CX, ROOT_Y + ROOT_H + 25, color="#1864ab", sw=2)

# ── 3 main branches ──
B1_W = 660  # Donnees
B2_W = 700  # Intelligence
B3_W = 660  # Commerce
GAP_B = 30
TOTAL_BW = B1_W + B2_W + B3_W + 2 * GAP_B
B_START_X = CX + (CW - TOTAL_BW) // 2
B_Y = ROOT_Y + ROOT_H + 55

B1_X = B_START_X
B2_X = B1_X + B1_W + GAP_B
B3_X = B2_X + B2_W + GAP_B

BAR_Y = ROOT_Y + ROOT_H + 25
B1_CX = B1_X + B1_W // 2
B2_CX = B2_X + B2_W // 2
B3_CX = B3_X + B3_W // 2

# Horizontal bar
L("rt_bar", B1_CX, BAR_Y, B3_CX, BAR_Y, color="#1864ab", sw=2)
# Drop lines to branches
L("rt_d1", B1_CX, BAR_Y, B1_CX, B_Y, color="#1864ab", sw=2)
L("rt_d2", B2_CX, BAR_Y, B2_CX, B_Y, color="#1864ab", sw=2)
L("rt_d3", B3_CX, BAR_Y, B3_CX, B_Y, color="#1864ab", sw=2)

# Branch 1: DONNEES CORE
R("br1", B1_X, B_Y, B1_W, 32, stroke="#339af0", bg="#339af0", sw=2)
T("br1_t", B1_X + 200, B_Y+6, "DONNEES CORE (6)", fs=16, color="#ffffff")

# Branch 2: INTELLIGENCE IA
R("br2", B2_X, B_Y, B2_W, 32, stroke="#845ef7", bg="#845ef7", sw=2)
T("br2_t", B2_X + 200, B_Y+6, "INTELLIGENCE IA (5)", fs=16, color="#ffffff")

# Branch 3: COMMERCE
R("br3", B3_X, B_Y, B3_W, 32, stroke="#f06595", bg="#f06595", sw=2)
T("br3_t", B3_X + 210, B_Y+6, "COMMERCE (7)", fs=16, color="#ffffff")

# ── Leaf nodes — Branch 1: DONNEES CORE ──
LEAF_W = 200
LEAF_H = 75
LEAF_GAP = 10
LEAF_Y = B_Y + 32 + 30
LEAF_ROW2_Y = LEAF_Y + LEAF_H + 10

# Stem + bar from branch 1
L("br1_stem", B1_CX, B_Y+32, B1_CX, B_Y+32+15, color="#339af0", sw=1)

br1_routes = [
    ("auth",     "/api/auth",        "Inscription, Login\nJWT access+refresh"),
    ("users",    "/api/users",       "Profil, Preferences\nTrustBadge"),
    ("vehicles", "/api/vehicles",    "CRUD vehicules\nListe paginee + filtres"),
    ("listings", "/api/listings",    "Annonces actives\nPublication + statut"),
    ("search",   "/api/search",      "Recherche NLP\nParsing multilingue"),
    ("seo",      "/api/seo",         "Sitemap XML\nPages marques/modeles"),
]
n1 = len(br1_routes)
row1_count = 3
row2_count = n1 - row1_count

# Row 1
rw1_total = row1_count * LEAF_W + (row1_count - 1) * LEAF_GAP
rw1_start = B1_X + (B1_W - rw1_total) // 2
bar1_y = B_Y + 32 + 15
left1 = rw1_start + LEAF_W // 2
right1 = rw1_start + (row1_count - 1) * (LEAF_W + LEAF_GAP) + LEAF_W // 2
L("br1_bar1", left1, bar1_y, right1, bar1_y, color="#339af0", sw=1)

for i, (rid_name, path, desc) in enumerate(br1_routes[:row1_count]):
    lx = rw1_start + i * (LEAF_W + LEAF_GAP)
    lcx = lx + LEAF_W // 2
    L(f"br1_drop_{rid_name}", lcx, bar1_y, lcx, LEAF_Y, color="#339af0", sw=1)
    R(f"rt_{rid_name}", lx, LEAF_Y, LEAF_W, LEAF_H, stroke="#339af0", bg="#d0ebff")
    T(f"rt_{rid_name}_t", lx+8, LEAF_Y+5, path, fs=13, color="#1864ab")
    T(f"rt_{rid_name}_d", lx+8, LEAF_Y+25, desc, fs=10, color="#495057")

# Row 2
rw2_total = row2_count * LEAF_W + (row2_count - 1) * LEAF_GAP
rw2_start = B1_X + (B1_W - rw2_total) // 2
# Connect row 2 via stem from bar
L("br1_stem2", B1_CX, bar1_y, B1_CX, LEAF_ROW2_Y - 10, color="#339af0", sw=1, ss="dashed")
left2 = rw2_start + LEAF_W // 2
right2 = rw2_start + (row2_count - 1) * (LEAF_W + LEAF_GAP) + LEAF_W // 2
L("br1_bar2", left2, LEAF_ROW2_Y - 10, right2, LEAF_ROW2_Y - 10, color="#339af0", sw=1)

for i, (rid_name, path, desc) in enumerate(br1_routes[row1_count:]):
    lx = rw2_start + i * (LEAF_W + LEAF_GAP)
    lcx = lx + LEAF_W // 2
    L(f"br1_drop2_{rid_name}", lcx, LEAF_ROW2_Y - 10, lcx, LEAF_ROW2_Y, color="#339af0", sw=1)
    R(f"rt_{rid_name}", lx, LEAF_ROW2_Y, LEAF_W, LEAF_H, stroke="#339af0", bg="#d0ebff")
    T(f"rt_{rid_name}_t", lx+8, LEAF_ROW2_Y+5, path, fs=13, color="#1864ab")
    T(f"rt_{rid_name}_d", lx+8, LEAF_ROW2_Y+25, desc, fs=10, color="#495057")


# ── Leaf nodes — Branch 2: INTELLIGENCE IA ──
L("br2_stem", B2_CX, B_Y+32, B2_CX, B_Y+32+15, color="#845ef7", sw=1)

br2_routes = [
    ("chat",     "/api/chat",            "Chatbot RAG\nMultilingue FR/AR/Darija"),
    ("reco",     "/api/recommendation",  "Hybride CBF+CF\nA/B Testing"),
    ("pricing",  "/api/pricing",         "XGBoost prediction\nIntervalle confiance"),
    ("vision",   "/api/v1/vision",       "Classification photo\nDetection marque"),
    ("reviews",  "/api/reviews",         "Avis + Sentiment\nAnalyse NLP auto"),
]
n2 = len(br2_routes)
row1_count2 = 3
row2_count2 = n2 - row1_count2

rw1_total2 = row1_count2 * LEAF_W + (row1_count2 - 1) * LEAF_GAP
rw1_start2 = B2_X + (B2_W - rw1_total2) // 2
bar2_y = B_Y + 32 + 15
left2a = rw1_start2 + LEAF_W // 2
right2a = rw1_start2 + (row1_count2 - 1) * (LEAF_W + LEAF_GAP) + LEAF_W // 2
L("br2_bar1", left2a, bar2_y, right2a, bar2_y, color="#845ef7", sw=1)

for i, (rid_name, path, desc) in enumerate(br2_routes[:row1_count2]):
    lx = rw1_start2 + i * (LEAF_W + LEAF_GAP)
    lcx = lx + LEAF_W // 2
    L(f"br2_drop_{rid_name}", lcx, bar2_y, lcx, LEAF_Y, color="#845ef7", sw=1)
    R(f"rt_{rid_name}", lx, LEAF_Y, LEAF_W, LEAF_H, stroke="#845ef7", bg="#f3f0ff")
    T(f"rt_{rid_name}_t", lx+8, LEAF_Y+5, path, fs=13, color="#5f3dc4")
    T(f"rt_{rid_name}_d", lx+8, LEAF_Y+25, desc, fs=10, color="#495057")

rw2_total2 = row2_count2 * LEAF_W + (row2_count2 - 1) * LEAF_GAP
rw2_start2 = B2_X + (B2_W - rw2_total2) // 2
L("br2_stem2", B2_CX, bar2_y, B2_CX, LEAF_ROW2_Y - 10, color="#845ef7", sw=1, ss="dashed")
left2b = rw2_start2 + LEAF_W // 2
right2b = rw2_start2 + (row2_count2 - 1) * (LEAF_W + LEAF_GAP) + LEAF_W // 2
L("br2_bar2", left2b, LEAF_ROW2_Y - 10, right2b, LEAF_ROW2_Y - 10, color="#845ef7", sw=1)

for i, (rid_name, path, desc) in enumerate(br2_routes[row1_count2:]):
    lx = rw2_start2 + i * (LEAF_W + LEAF_GAP)
    lcx = lx + LEAF_W // 2
    L(f"br2_drop2_{rid_name}", lcx, LEAF_ROW2_Y - 10, lcx, LEAF_ROW2_Y, color="#845ef7", sw=1)
    R(f"rt_{rid_name}", lx, LEAF_ROW2_Y, LEAF_W, LEAF_H, stroke="#845ef7", bg="#f3f0ff")
    T(f"rt_{rid_name}_t", lx+8, LEAF_ROW2_Y+5, path, fs=13, color="#5f3dc4")
    T(f"rt_{rid_name}_d", lx+8, LEAF_ROW2_Y+25, desc, fs=10, color="#495057")


# ── Leaf nodes — Branch 3: COMMERCE ──
L("br3_stem", B3_CX, B_Y+32, B3_CX, B_Y+32+15, color="#f06595", sw=1)

br3_routes = [
    ("favorites",    "/api/favorites",    "Ajouter/retirer\nListe favoris user"),
    ("messages",     "/api/messages",     "Message prive\nConversations"),
    ("offers",       "/api/offers",       "Offre de prix\nNegociation"),
    ("transactions", "/api/transactions", "Transaction securisee\npending->paid->done"),
    ("customs",      "/api/v1/customs",   "Dedouanement\nBareme ADII Maroc"),
    ("maintenance",  "/api/maintenance",  "Carnet entretien\nRappels auto"),
    ("admin",        "/api/v1/admin",     "Moderation\nStats plateforme"),
]
n3 = len(br3_routes)
row1_count3 = 4
row2_count3 = n3 - row1_count3

rw1_total3 = row1_count3 * LEAF_W + (row1_count3 - 1) * LEAF_GAP
rw1_start3 = B3_X + (B3_W - rw1_total3) // 2
bar3_y = B_Y + 32 + 15
left3a = rw1_start3 + LEAF_W // 2
right3a = rw1_start3 + (row1_count3 - 1) * (LEAF_W + LEAF_GAP) + LEAF_W // 2
L("br3_bar1", left3a, bar3_y, right3a, bar3_y, color="#f06595", sw=1)

for i, (rid_name, path, desc) in enumerate(br3_routes[:row1_count3]):
    lx = rw1_start3 + i * (LEAF_W + LEAF_GAP)
    lcx = lx + LEAF_W // 2
    L(f"br3_drop_{rid_name}", lcx, bar3_y, lcx, LEAF_Y, color="#f06595", sw=1)
    R(f"rt_{rid_name}", lx, LEAF_Y, LEAF_W, LEAF_H, stroke="#f06595", bg="#fff0f6")
    T(f"rt_{rid_name}_t", lx+8, LEAF_Y+5, path, fs=13, color="#a61e4d")
    T(f"rt_{rid_name}_d", lx+8, LEAF_Y+25, desc, fs=10, color="#495057")

rw2_total3 = row2_count3 * LEAF_W + (row2_count3 - 1) * LEAF_GAP
rw2_start3 = B3_X + (B3_W - rw2_total3) // 2
L("br3_stem2", B3_CX, bar3_y, B3_CX, LEAF_ROW2_Y - 10, color="#f06595", sw=1, ss="dashed")
left3b = rw2_start3 + LEAF_W // 2
right3b = rw2_start3 + (row2_count3 - 1) * (LEAF_W + LEAF_GAP) + LEAF_W // 2
L("br3_bar2", left3b, LEAF_ROW2_Y - 10, right3b, LEAF_ROW2_Y - 10, color="#f06595", sw=1)

for i, (rid_name, path, desc) in enumerate(br3_routes[row1_count3:]):
    lx = rw2_start3 + i * (LEAF_W + LEAF_GAP)
    lcx = lx + LEAF_W // 2
    L(f"br3_drop2_{rid_name}", lcx, LEAF_ROW2_Y - 10, lcx, LEAF_ROW2_Y, color="#f06595", sw=1)
    R(f"rt_{rid_name}", lx, LEAF_ROW2_Y, LEAF_W, LEAF_H, stroke="#f06595", bg="#fff0f6")
    T(f"rt_{rid_name}_t", lx+8, LEAF_ROW2_Y+5, path, fs=13, color="#a61e4d")
    T(f"rt_{rid_name}_d", lx+8, LEAF_ROW2_Y+25, desc, fs=10, color="#495057")


A("a_r2ml", CX+1100, LEAF_ROW2_Y + LEAF_H + 20, CX+1100, LEAF_ROW2_Y + LEAF_H + 50, color="#1971c2", sw=2)


# ── ML Modules ────────────────────────────────────────────────
ML_Y = LEAF_ROW2_Y + LEAF_H + 60
illus_brain("ill_ml", CX+10, ML_Y - 4, color="#5f3dc4")
T("s2b_label", CX+50, ML_Y, "MODULES ML & IA (6 modules)", fs=18, color="#5f3dc4")
T("s2b_label_desc", CX+50, ML_Y+25, "L'intelligence du systeme : Predit les prix, trouve les meilleures voitures pour vous, et detecte les arnaques.", fs=13, color="#5f3dc4")

R("ml1", CX+20, ML_Y+40, 700, 180, stroke="#845ef7", bg="#f3f0ff")
T("ml1_t", CX+30, ML_Y+50, "Moteur de Recommandation Hybride", fs=16, color="#5f3dc4")
T("ml1_b", CX+30, ML_Y+80,
  "hybrid_engine.py -> HybridEngine(alpha=0.6)\n"
  "  Formule: final_score = a x content_score + (1-a) x collaborative_score\n\n"
  "  A/B Testing: hash(user_id) mod 2\n"
  "    Variant A: a = 0.8 (Content dominant)\n"
  "    Variant B: a = 0.2 (Collaborative dominant)\n\n"
  "  Cold Start: si interactions < 3 -> content_score uniquement\n"
  "  Methodes: 'hybrid' | 'content-based' | 'cold-start'",
  fs=11, color="#495057")

R("ml2", CX+740, ML_Y+40, 700, 180, stroke="#845ef7", bg="#f3f0ff")
T("ml2_t", CX+750, ML_Y+50, "Content-Based Filtering (CBF)", fs=16, color="#5f3dc4")
T("ml2_b", CX+750, ML_Y+80,
  "content_based.py -> vehicle_to_feature_vector()\n"
  "  7 features normalisees:\n"
  "    price_norm, year_norm, mileage_norm (StandardScaler)\n"
  "    body_type_encoded  -> ordinal 0-1 (9 categories)\n"
  "    transmission_encoded -> manuelle=0, semi=0.5, auto=1\n"
  "    fuel_encoded -> ordinal 0-1 (7 types)\n"
  "    engine_power_norm\n\n"
  "  Similarite: cosine_similarity (sklearn)\n"
  "  Scalers: StandardScaler + MinMaxScaler (cached lru)",
  fs=11, color="#495057")

R("ml3", CX+1460, ML_Y+40, 700, 180, stroke="#845ef7", bg="#f3f0ff")
T("ml3_t", CX+1470, ML_Y+50, "Collaborative Filtering (CF)", fs=16, color="#5f3dc4")
T("ml3_b", CX+1470, ML_Y+80,
  "collaborative.py -> Implicit Feedback\n"
  "  Poids par action:\n"
  "    view=0.1, click=0.2, favorite=0.5\n"
  "    unfavorite=-0.3, contact=0.8, share=0.3\n"
  "    recommendation_click=0.6\n\n"
  "  Cold Start Threshold: 3 interactions minimum\n"
  "  Requete SQL: GROUP BY vehicle_id, action\n"
  "  Score agrege: sum(weight x action_count)",
  fs=11, color="#495057")

R("ml4", CX+20, ML_Y+240, 700, 120, stroke="#845ef7", bg="#f3f0ff")
T("ml4_t", CX+30, ML_Y+250, "Pricing Engine (XGBoost)", fs=16, color="#5f3dc4")
T("ml4_b", CX+30, ML_Y+280,
  "Prediction de prix juste basee sur le marche\n"
  "Features: marque, modele, annee, km, fuel, city\n"
  "Output: predicted_price + price_confidence [0-1]\n"
  "Entraine sur les donnees scrapees historiques",
  fs=11, color="#495057")

R("ml5", CX+740, ML_Y+240, 700, 120, stroke="#845ef7", bg="#f3f0ff")
T("ml5_t", CX+750, ML_Y+250, "Anomaly & Fraud Detection", fs=16, color="#5f3dc4")
T("ml5_b", CX+750, ML_Y+280,
  "Isolation Forest pour detection d'annonces suspectes\n"
  "Pattern Analysis: prix trop bas, photos volees\n"
  "Flag automatique pour moderation admin\n"
  "Score d'anomalie attribue a chaque annonce",
  fs=11, color="#495057")

R("ml6", CX+1460, ML_Y+240, 700, 120, stroke="#845ef7", bg="#f3f0ff")
T("ml6_t", CX+1470, ML_Y+250, "Computer Vision & NLP Sentiment", fs=16, color="#5f3dc4")
T("ml6_b", CX+1470, ML_Y+280,
  "vision/ -> Classification de photos vehicules\n"
  "sentiment/ -> Analyse de sentiment des avis\n"
  "nlp_pipeline/llm_extractor.py -> LLM Extraction\n"
  "segmentation/ -> Segmentation acheteurs",
  fs=11, color="#495057")

A("a_ml2rag", CX+1100, ML_Y+370, CX+1100, ML_Y+410, color="#1971c2", sw=2)


# ── RAG Chain ─────────────────────────────────────────────────
RAG_Y = ML_Y + 420
illus_chat("ill_rag", CX+10, RAG_Y - 6, color="#a61e4d")
T("s2c_label", CX+50, RAG_Y, "RAG CHAIN (Chatbot IA)", fs=18, color="#a61e4d")
T("s2c_label_desc", CX+50, RAG_Y+25, "L'assistant virtuel : Il discute avec vous en Darija/Francais et cherche dans notre catalogue pour vous conseiller comme un vrai vendeur.", fs=13, color="#a61e4d")

R("rag_bg", CX+20, RAG_Y+40, 2100, 260, stroke="#d6336c", bg="#fff0f6")
T("rag_title", CX+30, RAG_Y+50, "chatbot_chain.py -- Orchestration LangChain + Qdrant + Neo4j", fs=16, color="#a61e4d")

R("rag1", CX+40, RAG_Y+85, 480, 190, stroke="#f06595", bg="#ffe3e3")
T("rag1_t", CX+50, RAG_Y+95, "1. Detection de Langue", fs=14, color="#a61e4d")
T("rag1_b", CX+50, RAG_Y+120,
  "_detect_language(message)\n"
  "Caracteres arabes -> 'arabe'\n"
  "Mots darija (bghit, tomobila,\n"
  "  chhal, mzyan) -> 'darija'\n"
  "Mots anglais -> 'anglais'\n"
  "Par defaut -> 'francais'\n\n"
  "Le bot repond EXACTEMENT dans\n"
  "la langue detectee de l'utilisateur",
  fs=11, color="#495057")

R("rag2", CX+540, RAG_Y+85, 500, 190, stroke="#f06595", bg="#ffe3e3")
T("rag2_t", CX+550, RAG_Y+95, "2. Retrieval (Vector + Graph)", fs=14, color="#a61e4d")
T("rag2_b", CX+550, RAG_Y+120,
  "vector_search.py:\n"
  "  search_vehicles(query, limit=5)\n"
  "  -> Embedding query -> Qdrant search\n"
  "  -> Seuil: score >= 0.35\n\n"
  "  search_reviews(query, limit=3)\n"
  "  -> Collection: review_embeddings\n\n"
  "graph_context.py:\n"
  "  enrich_with_graph(vehicle_ids)\n"
  "  -> Neo4j: vehicules similaires\n"
  "  get_popularity_scores(ids) -> score",
  fs=11, color="#495057")

R("rag3", CX+1060, RAG_Y+85, 500, 190, stroke="#f06595", bg="#ffe3e3")
T("rag3_t", CX+1070, RAG_Y+95, "3. System Prompt & Generation", fs=14, color="#a61e4d")
T("rag3_b", CX+1070, RAG_Y+120,
  "SYSTEM_PROMPT avec 7 variables:\n"
  "  {detected_language}\n"
  "  {vehicle_context} -> vehicules trouves\n"
  "  {graph_context} -> similaires Neo4j\n"
  "  {review_context} -> avis pertinents\n"
  "  {conversation_history} -> memoire\n"
  "  {style_instructions}\n\n"
  "LLM: ChatOpenAI (LangChain)\n"
  "Output: ChatResponse + SourceReference[]",
  fs=11, color="#495057")

R("rag4", CX+1580, RAG_Y+85, 520, 190, stroke="#f06595", bg="#ffe3e3")
T("rag4_t", CX+1590, RAG_Y+95, "4. Conformite & Securite", fs=14, color="#a61e4d")
T("rag4_b", CX+1590, RAG_Y+120,
  "Directive Loi 09-08:\n"
  "  Ne JAMAIS demander/stocker/exposer\n"
  "  des donnees personnelles sensibles\n\n"
  "conversation_memory.py:\n"
  "  Memoire par session (non persistee)\n"
  "  Historique limite aux N derniers tours\n\n"
  "style_detector.py:\n"
  "  Detecte le ton de l'utilisateur\n"
  "  Adapte le style de reponse",
  fs=11, color="#495057")


# ── Middlewares ────────────────────────────────────────────────
MID_Y = RAG_Y + 320
illus_lock("ill_lock", CX+10, MID_Y - 4, color="#343a40")
T("s2d_label", CX+50, MID_Y, "MIDDLEWARES & SECURITE", fs=18, color="#343a40")

R("mid_bg", CX+20, MID_Y+35, 2100, 80, stroke="#495057", bg="#e9ecef")
T("mid_body", CX+30, MID_Y+45,
  "CORSMiddleware (origins configurables)  |  SecurityHeadersMiddleware (X-Content-Type, X-Frame, HSTS)  |  AuditLogMiddleware (log toutes les requetes)\n"
  "SlowAPI Rate Limiter (user_or_ip_key_func)  |  JWT Bearer Auth (access_token + refresh_token)  |  RequestValidationError handler (422 detaille)",
  fs=12, color="#495057")


# ── Services ──────────────────────────────────────────────────
SVC_Y = MID_Y + 140
illus_gear("ill_svc", CX+10, SVC_Y - 4, color="#343a40")
T("s2e_label", CX+50, SVC_Y, "SERVICES BACKEND", fs=18, color="#343a40")

R("svc1", CX+20, SVC_Y+35, 340, 70, stroke="#495057", bg="#e9ecef")
T("svc1_t", CX+30, SVC_Y+45, "customs_service.py", fs=14, color="#343a40")
T("svc1_b", CX+30, SVC_Y+70, "Calcul des droits de douane + TVA\nBareme officiel ADII Maroc", fs=11, color="#495057")

R("svc2", CX+380, SVC_Y+35, 340, 70, stroke="#495057", bg="#e9ecef")
T("svc2_t", CX+390, SVC_Y+45, "health_checker.py", fs=14, color="#343a40")
T("svc2_b", CX+390, SVC_Y+70, "Verifie PostgreSQL + Qdrant au boot\nLogs dans scraper_health.log", fs=11, color="#495057")

R("svc3", CX+740, SVC_Y+35, 340, 70, stroke="#495057", bg="#e9ecef")
T("svc3_t", CX+750, SVC_Y+45, "mailer.py + payment_service.py", fs=14, color="#343a40")
T("svc3_b", CX+750, SVC_Y+70, "Notifications email + integration\npaiement securise pour transactions", fs=11, color="#495057")

R("svc4", CX+1100, SVC_Y+35, 340, 70, stroke="#495057", bg="#e9ecef")
T("svc4_t", CX+1110, SVC_Y+45, "voice_transcription.py", fs=14, color="#343a40")
T("svc4_b", CX+1110, SVC_Y+70, "Transcription vocale pour chatbot\nRecherche vocale mobile", fs=11, color="#495057")

R("svc5", CX+1460, SVC_Y+35, 340, 70, stroke="#495057", bg="#e9ecef")
T("svc5_t", CX+1470, SVC_Y+45, "sitemap_generator.py", fs=14, color="#343a40")
T("svc5_b", CX+1470, SVC_Y+70, "Generation dynamique du sitemap XML\nPages marques + modeles + annonces", fs=11, color="#495057")

A("a_b2db", CX+1100, SVC_Y+120, CX+1100, SVC_Y+200, color="#1971c2", sw=3)
T("a_b2db_label", CX+1020, SVC_Y+150, "SQLAlchemy ORM ->", fs=14, color="#1971c2")


# ══════════════════════════════════════════════════════════════
# SECTION 3 — DATABASE LAYER
# ══════════════════════════════════════════════════════════════
DB_Y = SVC_Y + 210
R("s3_bg", CX-20, DB_Y, CW+40, 950, stroke="#f08c00", bg="#fffcf0", sw=2, ss="dashed")
illus_cylinder("ill_db", CX+10, DB_Y+8, color="#e8590c")
T("s3_title", CX+55, DB_Y+10, "PARTIE 3 -- DATABASE LAYER (4 bases de donnees)", fs=26, color="#e8590c")
T("s3_desc", CX, DB_Y+45, "En bref : La memoire de notre plateforme. On utilise 4 technologies differentes car on a besoin de stocker des donnees simples, mais aussi des relations complexes et des vecteurs pour l'IA.\nTechnique : Architecture polyglotte, chaque base (SQL, Graphe, Vecteur, Cache) a un role specifique.", fs=13, color="#495057")

# PostgreSQL
R("db_pg", CX+20, DB_Y+90, 520, 400, stroke="#f08c00", bg="#fff9db")
illus_cylinder("ill_pg", CX+30, DB_Y+98, color="#5c3c00")
T("db_pg_t", CX+75, DB_Y+100, "PostgreSQL (Relationnelle)", fs=18, color="#5c3c00")
T("db_pg_desc", CX+75, DB_Y+120, "Stockage classique : Tableaux contenant les informations principales (Utilisateurs, Annonces).", fs=12, color="#d9480f")
T("db_pg_b", CX+30, DB_Y+140,
  "Table: vehicles (modele ORM Vehicle)\n"
  "  id (UUID PK), seller_id (FK->users)\n"
  "  brand, model, version, year, mileage\n"
  "  fuel_type (enum 7), body_type (enum 9)\n"
  "  transmission (enum 3), engine_power_hp\n"
  "  color, doors, seats\n"
  "  city, postal_code, latitude, longitude\n"
  "  price, predicted_price, price_confidence\n"
  "  condition_score, popularity_score\n"
  "  photos (JSON array), description (Text)\n"
  "  source_url, status (available|sold|deleted)\n\n"
  "Table: users\n"
  "  id, full_name, email, phone, hashed_password\n"
  "  role (buyer|seller|admin), is_verified, is_pro\n"
  "  preferences (JSONB), avatar_url\n\n"
  "Tables annexes:\n"
  "  saved_vehicles, reviews, interactions,\n"
  "  listings, transactions, messages, offers,\n"
  "  chat_history, maintenance, catalog",
  fs=11, color="#495057")

# Qdrant
R("db_qd", CX+560, DB_Y+90, 520, 400, stroke="#7048e8", bg="#f3f0ff")
illus_brain("ill_qd", CX+570, DB_Y+98, color="#5f3dc4")
T("db_qd_t", CX+610, DB_Y+100, "Qdrant (Vectorielle)", fs=18, color="#5f3dc4")
T("db_qd_desc", CX+610, DB_Y+120, "Base speciale pour l'IA : Stocke le sens des mots pour des recherches tres intelligentes.", fs=12, color="#845ef7")
T("db_qd_b", CX+570, DB_Y+140,
  "Collection: vehicle_embeddings\n"
  "  Dimension: 384 (all-MiniLM-L6-v2)\n"
  "  Distance: Cosine Similarity\n"
  "  Payload: {\n"
  "    vehicle_id, brand, model, year,\n"
  "    price, fuel_type, body_type,\n"
  "    mileage, city\n"
  "  }\n\n"
  "Collection: review_embeddings\n"
  "  Dimension: 384\n"
  "  Payload: {\n"
  "    review_id, vehicle_id,\n"
  "    comment, rating\n"
  "  }\n\n"
  "Seuil de similarite: 0.35\n"
  "Recherche: embed(query) -> top-K vecteurs\n"
  "Port: 6333 (gRPC) / 6334 (HTTP)",
  fs=11, color="#495057")

# Neo4j
R("db_neo", CX+1100, DB_Y+90, 520, 400, stroke="#40c057", bg="#ebfbee")
illus_tree_icon("ill_neo", CX+1110, DB_Y+98, color="#2b8a3e")
T("db_neo_t", CX+1150, DB_Y+100, "Neo4j (Graphe)", fs=18, color="#2b8a3e")
T("db_neo_desc", CX+1150, DB_Y+120, "Base de relations : Parfaite pour les recommandations et l'historique des interactions.", fs=12, color="#40c057")
T("db_neo_b", CX+1110, DB_Y+140,
  "Noeuds:\n"
  "  (:Vehicle {id, brand, model, year, price})\n"
  "  (:Brand {name})\n"
  "  (:Model {name})\n"
  "  (:User {id, role})\n"
  "  (:Category {name})  // SUV, Berline...\n\n"
  "Relations:\n"
  "  (:Vehicle)-[:BELONGS_TO]->(:Brand)\n"
  "  (:Vehicle)-[:IS_MODEL]->(:Model)\n"
  "  (:Vehicle)-[:SIMILAR_TO {score}]->(:Vehicle)\n"
  "  (:User)-[:VIEWED]->(:Vehicle)\n"
  "  (:User)-[:FAVORITED]->(:Vehicle)\n"
  "  (:Brand)-[:HAS_MODEL]->(:Model)\n\n"
  "Requetes Cypher:\n"
  "  MATCH (v:Vehicle {id: $vid})\n"
  "  RETURN v.popularity_score AS score\n\n"
  "Port: 7687 (bolt) / 7474 (HTTP)",
  fs=11, color="#495057")

# Redis
R("db_redis", CX+1640, DB_Y+90, 520, 400, stroke="#e03131", bg="#fff5f5")
E("ill_redis_dot", CX+1650, DB_Y+102, 28, 28, stroke="#c92a2a", bg="#ff6b6b", sw=2)
T("ill_redis_flash", CX+1656, DB_Y+104, "R", fs=18, color="#ffffff")
T("db_redis_t", CX+1690, DB_Y+100, "Redis (Cache)", fs=18, color="#c92a2a")
T("db_redis_desc", CX+1690, DB_Y+120, "Memoire eclair : Retient les donnees recentes pour un affichage instantane.", fs=12, color="#ff8787")
T("db_redis_b", CX+1650, DB_Y+140,
  "Sessions:\n"
  "  session:{user_id} -> JWT payload\n"
  "  TTL: 24h (access), 7j (refresh)\n\n"
  "Cache API:\n"
  "  vehicles:page:{n}:filters:{hash}\n"
  "  TTL: 5 minutes\n"
  "  Invalidation sur POST/PATCH/DELETE\n\n"
  "Rate Limiting:\n"
  "  ratelimit:{ip}:{endpoint}\n"
  "  Compteur glissant (SlowAPI)\n\n"
  "Recherches frequentes:\n"
  "  search:popular -> Top 10 requetes\n"
  "  Suggestions autocomplete\n\n"
  "Conversation Memory:\n"
  "  chat:{session_id} -> derniers N tours\n"
  "  TTL: 30 minutes\n\n"
  "Port: 6379",
  fs=11, color="#495057")

A("a_db2fe", CX+1100, DB_Y+900, CX+1100, DB_Y+1010, color="#f08c00", sw=3)
T("a_db2fe_label", CX+1020, DB_Y+940, "JSON Response ->", fs=14, color="#1971c2")


# ══════════════════════════════════════════════════════════════
# SECTION 4 — FRONTEND ACHETEUR
# ══════════════════════════════════════════════════════════════
FE_Y = DB_Y + 1020
R("s4_bg", CX-20, FE_Y, CW+40, 2100, stroke="#2f9e44", bg="#f0fff4", sw=2, ss="dashed")
illus_monitor("ill_fe", CX+10, FE_Y+8, color="#2b8a3e")
T("s4_title", CX+55, FE_Y+10, "PARTIE 4 -- INTERFACE CLIENT (ACHETEUR UNIQUEMENT)", fs=26, color="#2b8a3e")
T("s4_desc", CX, FE_Y+45, "En bref : Ce que l'acheteur voit et utilise (site web). Concu pour etre tres rapide, fluide et facile a utiliser.\nTechnique : Application React (Vite) structuree avec React Router, React Query (pour garder les donnees en memoire), et TypeScript.", fs=13, color="#495057")


# ── Providers ─────────────────────────────────────────────────
PROV_Y = FE_Y + 100
illus_component("ill_prov", CX+10, PROV_Y - 4, color="#2b8a3e")
T("s4a_label", CX+50, PROV_Y, "PROVIDERS (Wrappers React)", fs=18, color="#2b8a3e")

R("prov_bg", CX+20, PROV_Y+30, 2100, 80, stroke="#2f9e44", bg="#d3f9d8")
T("prov_body", CX+30, PROV_Y+40,
  "QueryClientProvider (React Query -- cache automatique des appels API)  ->  AuthProvider (contexte JWT session)  ->  CompareProvider (vehicules a comparer)\n"
  "-> BrowserRouter (React Router v6 -- gestion des routes client-side)  ->  MainLayout: <Navbar/> + <Outlet/> + <Footer/> + <ChatbotWidget/> + <CompareDrawer/>",
  fs=12, color="#495057")


# ── Services Layer ────────────────────────────────────────────
SVC_FE_Y = PROV_Y + 130
illus_antenna("ill_fesvc", CX+10, SVC_FE_Y - 6, color="#087f5b")
T("s4b_label", CX+50, SVC_FE_Y, "SERVICES LAYER (Axios -> Backend)", fs=18, color="#087f5b")

R("fe_svc_bg", CX+20, SVC_FE_Y+30, 2100, 160, stroke="#099268", bg="#e6fcf5")

fe_services = [
    ("vehicleService.ts",       "getVehicles, getById, getBySlug"),
    ("chatbotService.ts",       "sendMessage, getHistory"),
    ("authService.ts",          "login, register, refreshToken"),
    ("recommendationService.ts","getRecommendations(filters)"),
    ("pricingService.ts",       "getPrediction, getEstimate"),
    ("favoriteService.ts",      "toggle, getFavorites"),
    ("searchParseService.ts",   "parseNLPQuery -> filtres"),
    ("customsService.ts",       "calculateDuty, getTaxRates"),
    ("offerService.ts",         "makeOffer, acceptOffer"),
    ("messageService.ts",       "sendMessage, getConversations"),
    ("transactionService.ts",   "initiate, uploadReceipt"),
    ("visionService.ts",        "analyzePhoto -> marque/modele"),
    ("listingService.ts",       "create, getMyListings"),
    ("compareService.ts",       "compareVehicles(ids[])"),
]

COL_W = 250
COL_H = 50
COL_GAP = 20
COLS_PER_ROW = 7
for idx, (name, desc) in enumerate(fe_services):
    row = idx // COLS_PER_ROW
    col = idx % COLS_PER_ROW
    sx = CX + 40 + col * (COL_W + COL_GAP)
    sy = SVC_FE_Y + 50 + row * (COL_H + 10)
    R(f"fs{idx}", sx, sy, COL_W, COL_H, stroke="#20c997", bg="#c3fae8")
    T(f"fs{idx}_t", sx+10, sy+8, name, fs=13, color="#087f5b")
    T(f"fs{idx}_b", sx+10, sy+28, desc, fs=10, color="#495057")


# ── ROUTES FRONTEND — TREE LAYOUT ────────────────────────────
FE_TREE_Y = SVC_FE_Y + 220
illus_tree_icon("ill_fetree", CX+10, FE_TREE_Y - 4, color="#2b8a3e")
T("s4c_label", CX+50, FE_TREE_Y, "ROUTES & PAGES -- Arbre Hierarchique (React Router v6)", fs=18, color="#2b8a3e")
T("s4c_label_desc", CX+50, FE_TREE_Y+25, "L'organisation des ecrans de l'application, divises en pages publiques, features, et tableau de bord.", fs=12, color="#2b8a3e")

# Root node
FE_ROOT_X = CX + 850
FE_ROOT_Y = FE_TREE_Y + 40
FE_ROOT_W = 350
FE_ROOT_H = 38
R("fe_root", FE_ROOT_X, FE_ROOT_Y, FE_ROOT_W, FE_ROOT_H, stroke="#2b8a3e", bg="#2b8a3e", sw=2)
T("fe_root_t", FE_ROOT_X+60, FE_ROOT_Y+8, "React Router v6 -- Routes", fs=16, color="#ffffff")

FE_ROOT_CX = FE_ROOT_X + FE_ROOT_W // 2
L("fe_stem", FE_ROOT_CX, FE_ROOT_Y + FE_ROOT_H, FE_ROOT_CX, FE_ROOT_Y + FE_ROOT_H + 25, color="#2b8a3e", sw=2)

# 3 branches: Public, Features, Dashboard
FB1_W = 750   # Public
FB2_W = 700   # Features
FB3_W = 600   # Dashboard
FB_GAP = 25
FB_TOTAL = FB1_W + FB2_W + FB3_W + 2 * FB_GAP
FB_START = CX + (CW - FB_TOTAL) // 2
FB_Y = FE_ROOT_Y + FE_ROOT_H + 55

FB1_X = FB_START
FB2_X = FB1_X + FB1_W + FB_GAP
FB3_X = FB2_X + FB2_W + FB_GAP

FB1_CX = FB1_X + FB1_W // 2
FB2_CX = FB2_X + FB2_W // 2
FB3_CX = FB3_X + FB3_W // 2

FE_BAR_Y = FE_ROOT_Y + FE_ROOT_H + 25
L("fe_bar", FB1_CX, FE_BAR_Y, FB3_CX, FE_BAR_Y, color="#2b8a3e", sw=2)
L("fe_d1", FB1_CX, FE_BAR_Y, FB1_CX, FB_Y, color="#2b8a3e", sw=2)
L("fe_d2", FB2_CX, FE_BAR_Y, FB2_CX, FB_Y, color="#2b8a3e", sw=2)
L("fe_d3", FB3_CX, FE_BAR_Y, FB3_CX, FB_Y, color="#2b8a3e", sw=2)

R("fb1", FB1_X, FB_Y, FB1_W, 32, stroke="#40c057", bg="#40c057", sw=2)
T("fb1_t", FB1_X + 260, FB_Y+6, "PAGES PUBLIQUES (4)", fs=16, color="#ffffff")

R("fb2", FB2_X, FB_Y, FB2_W, 32, stroke="#f06595", bg="#f06595", sw=2)
T("fb2_t", FB2_X + 220, FB_Y+6, "PAGES FEATURES (4)", fs=16, color="#ffffff")

R("fb3", FB3_X, FB_Y, FB3_W, 32, stroke="#339af0", bg="#339af0", sw=2)
T("fb3_t", FB3_X + 180, FB_Y+6, "DASHBOARD (7)", fs=16, color="#ffffff")

# ── Frontend leaf nodes — Branch 1: PAGES PUBLIQUES ──
FE_LEAF_W = 170
FE_LEAF_H = 100
FE_LEAF_GAP = 10
FE_LEAF_Y = FB_Y + 32 + 30

fb1_pages = [
    ("home",    "/",                  "Home.tsx\nSearchBar NLP\nLogos marques\nCarousel arrivages"),
    ("catalog", "/catalogue",         "Catalogue.tsx\n12 vehicules/page\nFiltres + tri\nToggle Neuf/Occasion"),
    ("detail",  "/vehicule/:id",      "VehicleDetail.tsx\nGalerie photos\nPrix estime IA\nVehicules similaires"),
    ("brand",   "/marque/:brandName", "BrandPage.tsx\nSEO par marque\nModeles + stats\nBreadcrumb nav"),
]

L("fb1_stem", FB1_CX, FB_Y+32, FB1_CX, FB_Y+32+15, color="#40c057", sw=1)
fe_bar1_y = FB_Y + 32 + 15
n_fb1 = len(fb1_pages)
fe_rw1_total = n_fb1 * FE_LEAF_W + (n_fb1 - 1) * FE_LEAF_GAP
fe_rw1_start = FB1_X + (FB1_W - fe_rw1_total) // 2
fe_left1 = fe_rw1_start + FE_LEAF_W // 2
fe_right1 = fe_rw1_start + (n_fb1 - 1) * (FE_LEAF_W + FE_LEAF_GAP) + FE_LEAF_W // 2
L("fb1_bar", fe_left1, fe_bar1_y, fe_right1, fe_bar1_y, color="#40c057", sw=1)

for i, (rid_name, path, desc) in enumerate(fb1_pages):
    lx = fe_rw1_start + i * (FE_LEAF_W + FE_LEAF_GAP)
    lcx = lx + FE_LEAF_W // 2
    L(f"fb1_drop_{rid_name}", lcx, fe_bar1_y, lcx, FE_LEAF_Y, color="#40c057", sw=1)
    R(f"fe_{rid_name}", lx, FE_LEAF_Y, FE_LEAF_W, FE_LEAF_H, stroke="#40c057", bg="#d3f9d8")
    T(f"fe_{rid_name}_t", lx+8, FE_LEAF_Y+5, path, fs=12, color="#2b8a3e")
    T(f"fe_{rid_name}_d", lx+8, FE_LEAF_Y+22, desc, fs=10, color="#495057")

# ── Frontend leaf nodes — Branch 2: FEATURES ──
fb2_pages = [
    ("chat",     "/chat",             "ChatbotPage.tsx\nPlein ecran\nMultilingue\nSuggestions"),
    ("customs",  "/dedouanement",     "CustomsPage.tsx\nCalculateur\nDroits douane+TVA\nBareme ADII"),
    ("auth",     "/auth",             "AuthPage.tsx\nLogin/Register\nJWT memoire\nRedirection"),
    ("tx",       "/transaction/:id",  "TransactionPage.tsx\nSuivi securise\nUpload recu\nWorkflow"),
]

L("fb2_stem", FB2_CX, FB_Y+32, FB2_CX, FB_Y+32+15, color="#f06595", sw=1)
n_fb2 = len(fb2_pages)
fe_rw2_total = n_fb2 * FE_LEAF_W + (n_fb2 - 1) * FE_LEAF_GAP
fe_rw2_start = FB2_X + (FB2_W - fe_rw2_total) // 2
fe_left2 = fe_rw2_start + FE_LEAF_W // 2
fe_right2 = fe_rw2_start + (n_fb2 - 1) * (FE_LEAF_W + FE_LEAF_GAP) + FE_LEAF_W // 2
L("fb2_bar", fe_left2, fe_bar1_y, fe_right2, fe_bar1_y, color="#f06595", sw=1)

for i, (rid_name, path, desc) in enumerate(fb2_pages):
    lx = fe_rw2_start + i * (FE_LEAF_W + FE_LEAF_GAP)
    lcx = lx + FE_LEAF_W // 2
    L(f"fb2_drop_{rid_name}", lcx, fe_bar1_y, lcx, FE_LEAF_Y, color="#f06595", sw=1)
    R(f"fe_{rid_name}", lx, FE_LEAF_Y, FE_LEAF_W, FE_LEAF_H, stroke="#f06595", bg="#fff0f6")
    T(f"fe_{rid_name}_t", lx+8, FE_LEAF_Y+5, path, fs=12, color="#a61e4d")
    T(f"fe_{rid_name}_d", lx+8, FE_LEAF_Y+22, desc, fs=10, color="#495057")

# ── Frontend leaf nodes — Branch 3: DASHBOARD (sub-tree) ──
L("fb3_stem", FB3_CX, FB_Y+32, FB3_CX, FB_Y+32+15, color="#339af0", sw=1)

# Dashboard root node
DASH_NODE_W = 220
DASH_NODE_H = 32
DASH_NODE_X = FB3_CX - DASH_NODE_W // 2
DASH_NODE_Y = FE_LEAF_Y - 5
R("fe_dash_root", DASH_NODE_X, DASH_NODE_Y, DASH_NODE_W, DASH_NODE_H, stroke="#339af0", bg="#339af0", sw=2)
T("fe_dash_root_t", DASH_NODE_X+20, DASH_NODE_Y+6, "DashboardLayout.tsx", fs=14, color="#ffffff")

# Connect branch to dash root
L("fb3_drop_dash", FB3_CX, fe_bar1_y, FB3_CX, DASH_NODE_Y, color="#339af0", sw=1)

# Dashboard sub-routes
DASH_LEAF_W = 155
DASH_LEAF_H = 55
DASH_LEAF_GAP = 8
DASH_LEAF_Y = DASH_NODE_Y + DASH_NODE_H + 35

dash_routes = [
    ("dash_idx",  "/dashboard",               "Vue d'ensemble\nBento grid stats"),
    ("dash_fav",  "/dashboard/favorites",      "Vehicules sauvegardes\nAlertes prix"),
    ("dash_reco", "/dashboard/recommendations","Suggestions IA\nPersonnalisees"),
    ("dash_msg",  "/dashboard/messages",       "Conversations\nAvec vendeurs"),
    ("dash_off",  "/dashboard/offers",         "Offres envoyees\nNegociations"),
    ("dash_prof", "/dashboard/profile",        "Parametres\nPreferences JSONB"),
    ("dash_mnt",  "/dashboard/maintenance",    "Carnet entretien\nRappels"),
]

n_dash = len(dash_routes)
# 2 rows: 4 + 3
dash_row1_count = 4
dash_row2_count = n_dash - dash_row1_count

L("fb3_dash_stem", FB3_CX, DASH_NODE_Y + DASH_NODE_H, FB3_CX, DASH_NODE_Y + DASH_NODE_H + 15, color="#339af0", sw=1)
dash_bar_y = DASH_NODE_Y + DASH_NODE_H + 15

# Row 1
dash_rw1_total = dash_row1_count * DASH_LEAF_W + (dash_row1_count - 1) * DASH_LEAF_GAP
# Center under the wider available space (use a wider centering range)
dash_rw1_start = FB3_CX - dash_rw1_total // 2
dash_left1 = dash_rw1_start + DASH_LEAF_W // 2
dash_right1 = dash_rw1_start + (dash_row1_count - 1) * (DASH_LEAF_W + DASH_LEAF_GAP) + DASH_LEAF_W // 2
L("fb3_dash_bar1", dash_left1, dash_bar_y, dash_right1, dash_bar_y, color="#339af0", sw=1)

for i, (rid_name, path, desc) in enumerate(dash_routes[:dash_row1_count]):
    lx = dash_rw1_start + i * (DASH_LEAF_W + DASH_LEAF_GAP)
    lcx = lx + DASH_LEAF_W // 2
    L(f"fb3_drop_{rid_name}", lcx, dash_bar_y, lcx, DASH_LEAF_Y, color="#339af0", sw=1)
    R(f"fe_{rid_name}", lx, DASH_LEAF_Y, DASH_LEAF_W, DASH_LEAF_H, stroke="#339af0", bg="#d0ebff")
    T(f"fe_{rid_name}_t", lx+6, DASH_LEAF_Y+4, path, fs=10, color="#1864ab")
    T(f"fe_{rid_name}_d", lx+6, DASH_LEAF_Y+20, desc, fs=10, color="#495057")

# Row 2
DASH_LEAF_Y2 = DASH_LEAF_Y + DASH_LEAF_H + 15
dash_rw2_total = dash_row2_count * DASH_LEAF_W + (dash_row2_count - 1) * DASH_LEAF_GAP
dash_rw2_start = FB3_CX - dash_rw2_total // 2
L("fb3_dash_stem2", FB3_CX, dash_bar_y, FB3_CX, DASH_LEAF_Y2 - 10, color="#339af0", sw=1, ss="dashed")
dash_left2 = dash_rw2_start + DASH_LEAF_W // 2
dash_right2 = dash_rw2_start + (dash_row2_count - 1) * (DASH_LEAF_W + DASH_LEAF_GAP) + DASH_LEAF_W // 2
L("fb3_dash_bar2", dash_left2, DASH_LEAF_Y2 - 10, dash_right2, DASH_LEAF_Y2 - 10, color="#339af0", sw=1)

for i, (rid_name, path, desc) in enumerate(dash_routes[dash_row1_count:]):
    lx = dash_rw2_start + i * (DASH_LEAF_W + DASH_LEAF_GAP)
    lcx = lx + DASH_LEAF_W // 2
    L(f"fb3_drop2_{rid_name}", lcx, DASH_LEAF_Y2 - 10, lcx, DASH_LEAF_Y2, color="#339af0", sw=1)
    R(f"fe_{rid_name}", lx, DASH_LEAF_Y2, DASH_LEAF_W, DASH_LEAF_H, stroke="#339af0", bg="#d0ebff")
    T(f"fe_{rid_name}_t", lx+6, DASH_LEAF_Y2+4, path, fs=10, color="#1864ab")
    T(f"fe_{rid_name}_d", lx+6, DASH_LEAF_Y2+20, desc, fs=10, color="#495057")


# ── Global Components ────────────────────────────────────────
COMP_Y = DASH_LEAF_Y2 + DASH_LEAF_H + 40
illus_component("ill_comp", CX+10, COMP_Y - 4, color="#862e9c")
T("s4e_label", CX+50, COMP_Y, "COMPOSANTS GLOBAUX (sur toutes les pages)", fs=18, color="#862e9c")
T("s4e_label_desc", CX+50, COMP_Y+25, "Les elements communs que l'utilisateur voit tout le temps (Menu, Pied de page, Bulle Chatbot).", fs=12, color="#862e9c")

R("comp_bg", CX+20, COMP_Y+30, 2100, 250, stroke="#862e9c", bg="#f8f0fc")

R("c1", CX+40, COMP_Y+60, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c1_t", CX+50, COMP_Y+70, "Navbar (layout/Navbar.tsx)", fs=14, color="#5f3dc4")
T("c1_b", CX+50, COMP_Y+100,
  "Logo Wakala + liens navigation\nIcones: Home, Search, Calculator, User\nBouton Login/Logout (useAuth hook)",
  fs=11, color="#495057")

R("c2", CX+380, COMP_Y+60, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c2_t", CX+390, COMP_Y+70, "Footer (App.tsx integre)", fs=14, color="#5f3dc4")
T("c2_b", CX+390, COMP_Y+100,
  "Sections: Plateforme, Technologie, Entreprise\nLiens: Catalogue, Calculateur, API Docs\nWakala -- Propulse par l'IA",
  fs=11, color="#495057")

R("c3", CX+720, COMP_Y+60, 320, 90, stroke="#f06595", bg="#ffe3e3")
T("c3_t", CX+730, COMP_Y+70, "ChatbotWidget (flottant)", fs=14, color="#a61e4d")
T("c3_b", CX+730, COMP_Y+100,
  "Bulle flottante sur toutes les pages\nZ-index eleve (au-dessus de tout)\nMini-chat inline + redirection /chat",
  fs=11, color="#495057")

R("c4", CX+1060, COMP_Y+60, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c4_t", CX+1070, COMP_Y+70, "CompareDrawer", fs=14, color="#5f3dc4")
T("c4_b", CX+1070, COMP_Y+100,
  "Tiroir comparateur cote a cote\nMax 3 vehicules simultanement\nCompareContext global",
  fs=11, color="#495057")

R("c5", CX+1400, COMP_Y+60, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c5_t", CX+1410, COMP_Y+70, "VehicleCard", fs=14, color="#5f3dc4")
T("c5_b", CX+1410, COMP_Y+100,
  "Carte reutilisable dans grilles\nBadge IA match score, prix, photo\nBoutons: Favori, Comparer",
  fs=11, color="#495057")

R("c6", CX+1740, COMP_Y+60, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c6_t", CX+1750, COMP_Y+70, "FilterPanel (filters/)", fs=14, color="#5f3dc4")
T("c6_b", CX+1750, COMP_Y+100,
  "Filtres dynamiques par facettes\nCompteurs en temps reel\nSynchro URL params bi-directionnelle",
  fs=11, color="#495057")

R("c7", CX+40, COMP_Y+170, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c7_t", CX+50, COMP_Y+180, "SearchBar (hero/)", fs=14, color="#5f3dc4")
T("c7_b", CX+50, COMP_Y+210,
  "Barre de recherche intelligente NLP\nParsing en temps reel (Darija inclus)\nAutocompletion suggestions",
  fs=11, color="#495057")

R("c8", CX+380, COMP_Y+170, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c8_t", CX+390, COMP_Y+180, "RecommendationForm", fs=14, color="#5f3dc4")
T("c8_b", CX+390, COMP_Y+210,
  "Formulaire guide de recommandation\nParcours interactif (guided-journey/)\nResultat -> redirection /catalogue",
  fs=11, color="#495057")

R("c9", CX+720, COMP_Y+170, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c9_t", CX+730, COMP_Y+180, "PricingWidget", fs=14, color="#5f3dc4")
T("c9_b", CX+730, COMP_Y+210,
  "Affiche le prix estime IA\nJauge de confiance visuelle\nComparaison prix demande vs estime",
  fs=11, color="#495057")

R("c10", CX+1060, COMP_Y+170, 320, 90, stroke="#be4bdb", bg="#e5dbff")
T("c10_t", CX+1070, COMP_Y+180, "i18n (Internationalisation)", fs=14, color="#5f3dc4")
T("c10_b", CX+1070, COMP_Y+210,
  "Fichiers: i18n/fr.ts (Francais)\nSupport: Arabe\nLabels UI traduits",
  fs=11, color="#495057")


# ── State Management ──────────────────────────────────────────
STATE_Y = COMP_Y + 300
illus_state("ill_state", CX+10, STATE_Y - 4, color="#0c8599")
T("s4f_label", CX+50, STATE_Y, "STATE MANAGEMENT & CONTEXTES", fs=18, color="#0c8599")

R("state_bg", CX+20, STATE_Y+35, 2100, 100, stroke="#0c8599", bg="#e3fafc")
T("state_body", CX+30, STATE_Y+45,
  "AuthContext (context/AuthContext.tsx)  ->  Gere la session JWT, le role utilisateur (buyer|seller|admin), et la deconnexion\n"
  "CompareContext (context/CompareContext.tsx)  ->  Liste des vehicules ajoutes au comparateur (max 3), persiste en session\n"
  "React Query (QueryClientProvider)  ->  Cache automatique des reponses API, invalidation sur mutation, stale-while-revalidate\n"
  "URL Search Params  ->  Les filtres du catalogue sont synchronises bidirectionnellement avec l'URL (?fuel_type=diesel&brand=...)",
  fs=12, color="#495057")


# ══════════════════════════════════════════════════════════════
# LEGEND
# ══════════════════════════════════════════════════════════════
LEG_Y = STATE_Y + 160
R("leg_bg", CX-20, LEG_Y, CW+40, 100, stroke="#dee2e6", bg="#f8f9fa")
T("leg_title", CX, LEG_Y+10, "LEGENDE & FLUX GLOBAL", fs=18, color="#343a40")

R("l1", CX+20, LEG_Y+45, 20, 15, stroke="#f08c00", bg="#fff9db")
T("l1t", CX+50, LEG_Y+42, "Scraping", fs=12, color="#868e96")
R("l2", CX+160, LEG_Y+45, 20, 15, stroke="#339af0", bg="#d0ebff")
T("l2t", CX+190, LEG_Y+42, "Backend API", fs=12, color="#868e96")
R("l3", CX+330, LEG_Y+45, 20, 15, stroke="#845ef7", bg="#f3f0ff")
T("l3t", CX+360, LEG_Y+42, "ML / IA", fs=12, color="#868e96")
R("l4", CX+470, LEG_Y+45, 20, 15, stroke="#f06595", bg="#fff0f6")
T("l4t", CX+500, LEG_Y+42, "Chatbot RAG", fs=12, color="#868e96")
R("l5", CX+630, LEG_Y+45, 20, 15, stroke="#40c057", bg="#d3f9d8")
T("l5t", CX+660, LEG_Y+42, "Pages Acheteur", fs=12, color="#868e96")
R("l6", CX+800, LEG_Y+45, 20, 15, stroke="#be4bdb", bg="#e5dbff")
T("l6t", CX+830, LEG_Y+42, "Composants React", fs=12, color="#868e96")
R("l7", CX+980, LEG_Y+45, 20, 15, stroke="#c92a2a", bg="#fff5f5")
T("l7t", CX+1010, LEG_Y+42, "Securite", fs=12, color="#868e96")
R("l8", CX+1130, LEG_Y+45, 20, 15, stroke="#f08c00", bg="#fff9db")
T("l8t", CX+1160, LEG_Y+42, "Databases", fs=12, color="#868e96")

T("leg_flow", CX, LEG_Y+72,
  "FLUX -> Sources Web (7) -> AntiDetection -> BaseScraper -> Data Cleaning -> NLP Extraction -> POST /api -> PostgreSQL + Qdrant + Neo4j -> ML Hybride -> RAG Chain -> JSON Response -> Services TS -> React Pages -> DOM Acheteur",
  fs=13, color="#495057")


# ══════════════════════════════════════════════════════════════
# SECTION 5 — LOGIQUE D'AUTHENTIFICATION (UML)
# ══════════════════════════════════════════════════════════════
AUTH_Y = LEG_Y + 160
R("s5_bg", CX-20, AUTH_Y, CW+40, 1150, stroke="#c92a2a", bg="#fff5f5", sw=2, ss="dashed")
illus_lock("ill_auth", CX+10, AUTH_Y+8, color="#e03131")
T("s5_title", CX+55, AUTH_Y+10, "PARTIE 5 -- LOGIQUE D'AUTHENTIFICATION (UML)", fs=26, color="#e03131")
T("s5_desc", CX, AUTH_Y+45, "En bref : Comment le systeme gere les connexions, les roles et la securite.\nTechnique : Sequence de Login JWT, Modeles de classes (User/Session) et Use Cases d'authentification.", fs=13, color="#495057")

# --- 1. SEQUENCE DIAGRAM ---
SEQ_X = CX + 20
SEQ_Y = AUTH_Y + 100
R("seq_bg", SEQ_X, SEQ_Y, 700, 1020, stroke="#f03e3e", bg="#ffffff")
T("seq_title", SEQ_X+20, SEQ_Y+20, "1. DIAGRAMME DE SEQUENCE : Processus de Login", fs=16, color="#c92a2a")
T("seq_desc", SEQ_X+20, SEQ_Y+45,
  "En details (pas-a-pas) :\n"
  "1. Vous tapez votre email et mot de passe.\n"
  "2. L'ecran (Frontend) emballe l'information et l'envoie au serveur de facon securisee.\n"
  "3. Le serveur fouille dans la base de donnees pour retrouver votre profil.\n"
  "4. Si c'est faux (encadre rouge) : le serveur vous bloque avec une erreur 401.\n"
  "5. Si c'est juste (encadre vert) : le serveur vous cree des cles numeriques (Tokens).\n"
  "6. On stocke le fait que vous etes la dans une memoire tres rapide (Redis).\n"
  "7. Vous recevez vos cles et la porte s'ouvre !", fs=12, color="#495057")

lx_u = SEQ_X + 100
lx_f = SEQ_X + 280
lx_b = SEQ_X + 460
lx_d = SEQ_X + 620

T("seq_u", lx_u-40, SEQ_Y+180, "Utilisateur", fs=14, color="#343a40")
T("seq_f", lx_f-35, SEQ_Y+180, "Frontend", fs=14, color="#2b8a3e")
T("seq_b", lx_b-35, SEQ_Y+180, "Backend", fs=14, color="#1864ab")
T("seq_d", lx_d-35, SEQ_Y+180, "Database", fs=14, color="#e8590c")

# Lifelines
L("ll_u", lx_u, SEQ_Y+210, lx_u, SEQ_Y+980, color="#adb5bd", ss="dashed")
L("ll_f", lx_f, SEQ_Y+210, lx_f, SEQ_Y+980, color="#adb5bd", ss="dashed")
L("ll_b", lx_b, SEQ_Y+210, lx_b, SEQ_Y+980, color="#adb5bd", ss="dashed")
L("ll_d", lx_d, SEQ_Y+210, lx_d, SEQ_Y+980, color="#adb5bd", ss="dashed")

# Messages
cy = SEQ_Y + 250
A("m1", lx_u, cy, lx_f, cy, color="#495057")
T("mt1", lx_u+10, cy-15, "Saisit Email/Mdp", fs=11, color="#495057")

cy += 60
A("m2", lx_f, cy, lx_b, cy, color="#495057")
T("mt2", lx_f+10, cy-15, "POST /api/auth/login", fs=11, color="#495057")

cy += 60
A("m3", lx_b, cy, lx_d, cy, color="#495057")
T("mt3", lx_b+10, cy-15, "SELECT user WHERE email", fs=11, color="#495057")

cy += 60
A("m4", lx_d, cy, lx_b, cy, color="#e8590c")
T("mt4", lx_b+10, cy-15, "Retourne User (Hash)", fs=11, color="#e8590c")

cy += 60
L("m5a", lx_b, cy, lx_b+40, cy, color="#495057")
L("m5b", lx_b+40, cy, lx_b+40, cy+20, color="#495057")
A("m5c", lx_b+40, cy+20, lx_b, cy+20, color="#495057")
T("mt5", lx_b+45, cy+5, "Verifie hash password", fs=11, color="#495057")

cy += 80
R("alt_bg", lx_u-20, cy-20, 680, 200, stroke="#f03e3e", bg="transparent", ss="dashed")
T("alt_t", lx_u-15, cy-15, "ALT: Mot de passe incorrect", fs=11, color="#c92a2a")

cy += 20
A("m6", lx_b, cy, lx_f, cy, color="#c92a2a")
T("mt6", lx_f+10, cy-15, "401 Unauthorized", fs=11, color="#c92a2a")

cy += 40
A("m7", lx_f, cy, lx_u, cy, color="#c92a2a")
T("mt7", lx_u+10, cy-15, "Affiche Erreur", fs=11, color="#c92a2a")

cy += 40
L("alt_div", lx_u-20, cy, lx_d+60, cy, color="#f03e3e", ss="dashed")
T("alt_t2", lx_u-15, cy+5, "ELSE: Mot de passe correct", fs=11, color="#2b8a3e")

cy += 40
L("m8a", lx_b, cy, lx_b+40, cy, color="#2b8a3e")
L("m8b", lx_b+40, cy, lx_b+40, cy+20, color="#2b8a3e")
A("m8c", lx_b+40, cy+20, lx_b, cy+20, color="#2b8a3e")
T("mt8", lx_b+45, cy+5, "Genere Access+Refresh Token", fs=11, color="#2b8a3e")

cy += 60
A("m9", lx_b, cy, lx_d, cy, color="#2b8a3e")
T("mt9", lx_b+10, cy-15, "Stocke Session (Redis)", fs=11, color="#2b8a3e")

cy += 60
A("m10", lx_b, cy, lx_f, cy, color="#2b8a3e")
T("mt10", lx_f+10, cy-15, "200 OK {tokens}", fs=11, color="#2b8a3e")

cy += 60
A("m11", lx_f, cy, lx_u, cy, color="#2b8a3e")
T("mt11", lx_u+10, cy-15, "Redirige vers Dashboard", fs=11, color="#2b8a3e")


# --- 2. CLASS DIAGRAM ---
CLS_X = SEQ_X + 740
CLS_Y = AUTH_Y + 100
R("cls_bg", CLS_X, CLS_Y, 700, 1020, stroke="#1864ab", bg="#ffffff")
T("cls_title", CLS_X+20, CLS_Y+20, "2. DIAGRAMME DE CLASSES : Modeles Securite", fs=16, color="#1864ab")
T("cls_desc", CLS_X+20, CLS_Y+45,
  "En details (La structure du code invisible) :\n"
  "- User : Represente une personne stockee en base. Il a un identifiant unique (UUID),\n  un email et un 'hashed_password' (mot de passe brouille de facon irreversible pour la securite).\n"
  "- Role : C'est un statut (Acheteur, Vendeur, Admin) qui dit ce qu'on a le droit de faire.\n"
  "- Session : Represente le fait que vous soyez connecte en ce moment. Elle a une date d'expiration.\n"
  "- JWTToken : C'est le passeport numerique qui voyage entre votre telephone et le serveur.\n  Il contient une signature infalsifiable pour prouver que c'est bien vous.", fs=12, color="#495057")

cx_user = CLS_X + 50
cy_user = CLS_Y + 180
R("c_user", cx_user, cy_user, 260, 220, stroke="#1864ab", bg="#d0ebff")
T("c_user_t", cx_user+110, cy_user+10, "User", fs=14, color="#1864ab")
L("c_user_l", cx_user, cy_user+35, cx_user+260, cy_user+35, color="#1864ab")
T("c_user_b", cx_user+10, cy_user+45,
  "+ id: UUID\n"
  "+ email: String\n"
  "+ hashed_password: String\n"
  "+ is_verified: Boolean\n"
  "----------------------\n"
  "+ login()\n"
  "+ logout()\n"
  "+ resetPassword()", fs=11, color="#495057")

cx_role = CLS_X + 400
cy_role = CLS_Y + 180
R("c_role", cx_role, cy_role, 200, 140, stroke="#f08c00", bg="#fff9db")
T("c_role_t", cx_role+50, cy_role+10, "<<enum>> Role", fs=14, color="#f08c00")
L("c_role_l", cx_role, cy_role+35, cx_role+200, cy_role+35, color="#f08c00")
T("c_role_b", cx_role+10, cy_role+45,
  "BUYER\n"
  "SELLER\n"
  "ADMIN", fs=11, color="#495057")

A("rel_u_r", cx_user+260, cy_user+100, cx_role, cy_role+100, color="#495057")
T("rt_u_r", cx_user+280, cy_user+80, "possede", fs=11, color="#495057")

cx_sess = CLS_X + 50
cy_sess = CLS_Y + 500
R("c_sess", cx_sess, cy_sess, 260, 200, stroke="#1864ab", bg="#d0ebff")
T("c_sess_t", cx_sess+100, cy_sess+10, "Session", fs=14, color="#1864ab")
L("c_sess_l", cx_sess, cy_sess+35, cx_sess+260, cy_sess+35, color="#1864ab")
T("c_sess_b", cx_sess+10, cy_sess+45,
  "+ session_id: String\n"
  "+ user_id: UUID\n"
  "+ access_token: String\n"
  "+ expires_at: DateTime\n"
  "----------------------\n"
  "+ isValid()\n"
  "+ revoke()", fs=11, color="#495057")

A("rel_u_s", cx_user+130, cy_user+220, cx_sess+130, cy_sess, color="#495057")
T("rt_u_s", cx_user+140, cy_user+260, "cree (0..*)", fs=11, color="#495057")

cx_jwt = CLS_X + 400
cy_jwt = CLS_Y + 500
R("c_jwt", cx_jwt, cy_jwt, 260, 180, stroke="#1864ab", bg="#d0ebff")
T("c_jwt_t", cx_jwt+100, cy_jwt+10, "JWTToken", fs=14, color="#1864ab")
L("c_jwt_l", cx_jwt, cy_jwt+35, cx_jwt+260, cy_jwt+35, color="#1864ab")
T("c_jwt_b", cx_jwt+10, cy_jwt+45,
  "+ header: String\n"
  "+ payload: String\n"
  "+ signature: String\n"
  "----------------------\n"
  "+ verifySignature()\n"
  "+ decodePayload()", fs=11, color="#495057")

A("rel_s_j", cx_sess+260, cy_sess+100, cx_jwt, cy_jwt+100, color="#495057")
T("rt_s_j", cx_sess+280, cy_sess+80, "utilise (1)", fs=11, color="#495057")


# --- 3. USE CASE DIAGRAM ---
UC_X = CLS_X + 740
UC_Y = AUTH_Y + 100
R("uc_bg", UC_X, UC_Y, 620, 1020, stroke="#2b8a3e", bg="#ffffff")
T("uc_title", UC_X+20, UC_Y+20, "3. DIAGRAMME DE CAS D'UTILISATION", fs=16, color="#2b8a3e")
T("uc_desc", UC_X+20, UC_Y+45,
  "En details (Qui peut faire quoi dans le systeme ?) :\n"
  "- L'acteur Visiteur : C'est le grand public. Il a uniquement le droit de regarder\n  les annonces publiques, de s'inscrire ou de redemander un mot de passe.\n"
  "- L'acteur Client Connecte : C'est vous, apres connexion. En plus du visiteur, vous\n  pouvez modifier vos propres donnees et gerer vos connexions en cours.\n"
  "- L'acteur Administrateur : C'est le patron de l'application. En plus d'etre client,\n  il a le droit de bloquer un compte frauduleux et de donner des droits aux autres.", fs=12, color="#495057")

ax = UC_X + 50
ay_vis = UC_Y + 230
ay_cli = UC_Y + 480
ay_adm = UC_Y + 730

E("a_vis", ax, ay_vis, 40, 40, stroke="#343a40", bg="#dee2e6")
T("at_vis", ax-10, ay_vis+50, "Visiteur", fs=14, color="#343a40")

E("a_cli", ax, ay_cli, 40, 40, stroke="#343a40", bg="#dee2e6")
T("at_cli", ax-25, ay_cli+50, "Client Connecte", fs=14, color="#343a40")

E("a_adm", ax, ay_adm, 40, 40, stroke="#343a40", bg="#dee2e6")
T("at_adm", ax-15, ay_adm+50, "Administrateur", fs=14, color="#343a40")

R("uc_sys", UC_X + 200, UC_Y + 160, 360, 700, stroke="#adb5bd", bg="#f8f9fa", ss="dashed")
T("uc_sys_t", UC_X+220, UC_Y+170, "Systeme d'Authentification & Profil", fs=12, color="#495057")

def UC(id, x, y, text):
    R(id, x, y, 260, 50, stroke="#2b8a3e", bg="#d3f9d8")
    T(id+"_t", x+20, y+15, text, fs=12, color="#2b8a3e")

ucx = UC_X + 250
UC("uc1", ucx, UC_Y + 210, "S'inscrire")
UC("uc2", ucx, UC_Y + 300, "Se Connecter (Login)")
UC("uc3", ucx, UC_Y + 390, "Reinitialiser Mot de Passe")
UC("uc4", ucx, UC_Y + 480, "Gerer son Profil")
UC("uc5", ucx, UC_Y + 570, "Gerer ses sessions actives")
UC("uc6", ucx, UC_Y + 660, "Bannir / Bloquer un compte")
UC("uc7", ucx, UC_Y + 750, "Changer le role d'un User")

A("l_v1", ax+40, ay_vis+20, ucx, UC_Y+235, color="#495057")
A("l_v2", ax+40, ay_vis+20, ucx, UC_Y+325, color="#495057")
A("l_v3", ax+40, ay_vis+20, ucx, UC_Y+415, color="#495057")

A("l_c1", ax+40, ay_cli+20, ucx, UC_Y+325, color="#495057")
A("l_c2", ax+40, ay_cli+20, ucx, UC_Y+505, color="#495057")
A("l_c3", ax+40, ay_cli+20, ucx, UC_Y+595, color="#495057")

A("l_a1", ax+40, ay_adm+20, ucx, UC_Y+325, color="#495057")
A("l_a2", ax+40, ay_adm+20, ucx, UC_Y+685, color="#495057")
A("l_a3", ax+40, ay_adm+20, ucx, UC_Y+775, color="#495057")

L("l_a_c", ax+20, ay_adm-5, ax+20, ay_cli+45, color="#343a40", ss="dashed")


# ══════════════════════════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════════════════════════
data = {
    "type": "excalidraw",
    "version": 2,
    "source": "https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor",
    "elements": els,
    "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
    "files": {}
}

out = "d:/Projet automobile/vente-auto-platform/schema_interface_client.excalidraw"
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"OK - {len(els)} elements generes -> {out}")
