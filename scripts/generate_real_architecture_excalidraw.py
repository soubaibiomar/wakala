#!/usr/bin/env python3
"""
generate_real_architecture_excalidraw.py
=========================================
Generates a complete, professional, comprehensive Excalidraw diagram (.excalidraw)
representing the REAL physical architecture of the Wakala platform based on the
code on disk.

Follows the excalidraw-expert design standards:
- Professional style: roughness 0, fontFamily 2 (Normal), clean rounded boxes
- Dark theme background (#0a0e17)
- Clear layer grouping and spatial hierarchy
- Detailed explanatory texts ("Comment ça marche" & "Pourquoi ce choix")
- High-density bullet lists (8 dimensions, 6 milestones outreach, etc.)
- Explicit "Écarts Constatés" alert section
- Comprehensive legend & metadata
"""

import json
import random
import sys
from pathlib import Path

# ── Colors Palette ─────────────────────────────────────────────────────────────
BG_CANVAS = "#0a0e17"
BG_CARD_DEFAULT = "#111827"
STROKE_DEFAULT = "#374151"
TEXT_WHITE = "#f9fafb"
TEXT_MUTED = "#9ca3af"

# Semantic Layer Colors
C_FRONTEND = {"border": "#3b82f6", "bg": "#1e293b", "text": "#60a5fa", "fill": "#172554"}
C_GATEWAY = {"border": "#06b6d4", "bg": "#164e63", "text": "#67e8f9", "fill": "#083344"}
C_DETERMINISTIC = {"border": "#10b981", "bg": "#064e3b", "text": "#34d399", "fill": "#022c22"}
C_AI_RAG = {"border": "#8b5cf6", "bg": "#4c1d95", "text": "#a78bfa", "fill": "#2e1065"}
C_DATA_INGESTION = {"border": "#f59e0b", "bg": "#78350f", "text": "#fbbf24", "fill": "#451a03"}
C_STORAGE = {"border": "#6366f1", "bg": "#312e81", "text": "#818cf8", "fill": "#1e1b4b"}
C_OUTREACH = {"border": "#ec4899", "bg": "#831843", "text": "#f472b6", "fill": "#500724"}
C_ALERT = {"border": "#ef4444", "bg": "#7f1d1d", "text": "#fca5a5", "fill": "#450a0a"}
C_ANALYTICS = {"border": "#14b8a6", "bg": "#134e4a", "text": "#2dd4bf", "fill": "#042f2e"}

class ExcalidrawBuilder:
    def __init__(self):
        self.elements = []
        self._id_counter = 1

    def _gen_id(self):
        self._id_counter += 1
        return f"elem_{self._id_counter:04d}_{random.randint(1000, 9999)}"

    def add_rect(self, x, y, w, h, stroke, bg, stroke_width=2, radius=8, fill_style="solid", opacity=100):
        elem_id = self._gen_id()
        elem = {
            "id": elem_id,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": bg,
            "fillStyle": fill_style,
            "strokeWidth": stroke_width,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": opacity,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 3} if radius > 0 else None,
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": random.randint(10000, 99999),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False
        }
        self.elements.append(elem)
        return elem_id

    def add_text(self, x, y, text, color=TEXT_WHITE, font_size=16, font_family=2, text_align="left", vertical_align="top", container_id=None, line_height=1.35):
        elem_id = self._gen_id()
        # rough dimensions
        lines = text.split("\n")
        max_line_len = max(len(l) for l in lines) if lines else 1
        w = max(40, max_line_len * (font_size * 0.58))
        h = max(20, len(lines) * font_size * line_height)

        elem = {
            "id": elem_id,
            "type": "text",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": random.randint(10000, 99999),
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": font_family,
            "textAlign": text_align,
            "verticalAlign": vertical_align,
            "containerId": container_id,
            "originalText": text,
            "lineHeight": line_height
        }
        self.elements.append(elem)
        return elem_id

    def add_card(self, x, y, w, h, title, subtitle, bullets, comment_text, why_text, palette, font_size_title=18):
        """Creates a fully styled component card with title, badges, bullet lists, mechanisms, and rationale."""
        # Main card box
        box_id = self.add_rect(x, y, w, h, palette["border"], palette["bg"], stroke_width=2, radius=12)
        
        # Header background banner
        header_h = 44
        self.add_rect(x, y, w, header_h, palette["border"], palette["fill"], stroke_width=1, radius=12)
        self.add_text(x + 16, y + 12, title, color=palette["text"], font_size=font_size_title, font_family=2)
        
        cur_y = y + 54
        if subtitle:
            self.add_text(x + 16, cur_y, subtitle, color=TEXT_MUTED, font_size=13, font_family=2)
            cur_y += 24

        # Bullet list
        if bullets:
            bullets_formatted = "\n".join([f"• {b}" for b in bullets])
            self.add_text(x + 16, cur_y, bullets_formatted, color=TEXT_WHITE, font_size=13, font_family=2, line_height=1.4)
            cur_y += len(bullets) * 20 + 8

        # "Comment ça marche" block
        if comment_text:
            self.add_rect(x + 12, cur_y, w - 24, 60, palette["border"], "#0f172a", stroke_width=1, radius=6)
            self.add_text(x + 18, cur_y + 6, "⚙️ MÉCANISME RÉEL (Code) :", color=palette["text"], font_size=11, font_family=2)
            self.add_text(x + 18, cur_y + 24, comment_text, color=TEXT_MUTED, font_size=12, font_family=2, line_height=1.3)
            cur_y += 68

        # "Pourquoi ce choix" block
        if why_text:
            self.add_rect(x + 12, cur_y, w - 24, 52, STROKE_DEFAULT, "#0f172a", stroke_width=1, radius=6)
            self.add_text(x + 18, cur_y + 5, "💡 JUSTIFICATION ARCHITECTURALE :", color="#fbbf24", font_size=11, font_family=2)
            self.add_text(x + 18, cur_y + 22, why_text, color=TEXT_MUTED, font_size=12, font_family=2, line_height=1.3)

        return box_id

    def add_arrow(self, start_x, start_y, end_x, end_y, stroke="#60a5fa", stroke_width=2, label=""):
        elem_id = self._gen_id()
        dx = end_x - start_x
        dy = end_y - start_y
        elem = {
            "id": elem_id,
            "type": "arrow",
            "x": start_x,
            "y": start_y,
            "width": abs(dx),
            "height": abs(dy),
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": stroke_width,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 2},
            "seed": random.randint(10000, 99999),
            "version": 1,
            "versionNonce": random.randint(10000, 99999),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": "arrow"
        }
        self.elements.append(elem)
        if label:
            mid_x = start_x + dx/2
            mid_y = start_y + dy/2 - 14
            self.add_text(mid_x, mid_y, label, color=stroke, font_size=12, font_family=2)
        return elem_id

    def to_dict(self):
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {
                "viewBackgroundColor": BG_CANVAS,
                "gridSize": None
            },
            "files": {}
        }


def build_architecture_diagram():
    b = ExcalidrawBuilder()

    # ══════════════════════════════════════════════════════════════════════════
    # 0. HEADER & TITRE
    # ══════════════════════════════════════════════════════════════════════════
    b.add_rect(50, 30, 2500, 100, "#3b82f6", "#0f172a", stroke_width=2, radius=12)
    b.add_text(80, 48, "WAKALA — CARTOGRAPHIE DE L'ARCHITECTURE RÉELLE DU REPOSITORY", color="#60a5fa", font_size=28, font_family=2)
    b.add_text(80, 88, "Inspection physique du disque local (d:/Projet automobile/vente-auto-platform) • État vérifié du code source, connexions effectives & écarts constatés", color=TEXT_MUTED, font_size=14, font_family=2)

    # ══════════════════════════════════════════════════════════════════════════
    # 1. COUCHE CLIENTS & FRONTEND (X: 50 .. 2550, Y: 160 .. 580)
    # ══════════════════════════════════════════════════════════════════════════
    # Container Zone Frontend
    b.add_rect(50, 160, 2500, 420, C_FRONTEND["border"], "#0b132b", stroke_width=1, radius=16, opacity=50)
    b.add_text(70, 175, "🌐 COUCHE 1 — APPLICATIONS CLIENTES & INTERFACES UTILISATEURS (frontend/ & mobile/)", color=C_FRONTEND["text"], font_size=18, font_family=2)

    # Card 1.1: Web App React Vite
    b.add_card(
        x=70, y=210, w=580, h=350,
        title="Web App React 18 (SPA Vite)",
        subtitle="Chemin: frontend/src/ • 24 Pages • 17 Services API",
        bullets=[
            "Pages: Catalogue.tsx, VehicleDetail.tsx, ComparatorPage.tsx",
            "Chatbot: ChatbotPage.tsx (dialogue consultatif 2 phases)",
            "Configurateur & 3D: NewCarDetailPage.tsx, Viewer Three.js",
            "Dédouanement & Taxes: CustomsPage.tsx, TrustScorePage.tsx",
            "Authentification: AuthContext.tsx (JWT + OTP mailer)",
            "Services API: api.ts (Axios), newCatalogService, recommendationService"
        ],
        comment_text="Consomme l'API FastAPI via des services modulaires typés TypeScript.\nGère le state d'authentification et le multilingue (i18n).",
        why_text="Vite + React SPA offre une navigation ultra-rapide et un rendu\n3D fluide pour le configurateur de véhicules neufs.",
        palette=C_FRONTEND
    )

    # Card 1.2: 3D Visualizer Studio
    b.add_card(
        x=680, y=210, w=580, h=350,
        title="Configurateur 3D & Modèles glTF",
        subtitle="Chemin: frontend/public/models/ & scripts Three.js",
        bullets=[
            "Générateur: generate_dacia_sandero_stepway_3d.py (.glb 2.0)",
            "Visualisation interactive Three.js (Carrosserie, Jantes, Feux LED)",
            "Sélecteur de teintes & options constructeur en temps réel",
            "Calcul d'impact prix/finition déterministe immédiat",
            "Optimisation PBR: Rugosité, Métallisation, Normales calculées"
        ],
        comment_text="Génère programmatiquement un modèle 3D binaire (.glb) avec matériaux\net géométries paramétriques pour les modèles phares.",
        why_text="Élimine la dépendance à des assets 3D tiers lourds et permet\nune personnalisation 100% fidèle au catalogue marocain.",
        palette=C_FRONTEND
    )

    # Card 1.3: Mobile App React Native Expo
    b.add_card(
        x=1290, y=210, w=580, h=350,
        title="Application Mobile (React Native Expo)",
        subtitle="Chemin: mobile/src/ • 9 Écrans natifs complets",
        bullets=[
            "Navigation: Stack Navigation (Login, Register, Home, Catalogue)",
            "Chat: ChatScreen.tsx (interface conversationnelle mobile)",
            "Détail & Favoris: VehicleDetailScreen.tsx, SellerDashboardScreen.tsx",
            "Recherche: CatalogueScreen.tsx avec filtres prix/usage",
            "Services: Client HTTP vers backend local/distant"
        ],
        comment_text="Base de code React Native fonctionnelle avec typage complet,\nservices API calqués sur le web et gestion de tokens natifs.",
        why_text="Permet un déploiement iOS/Android instantané partageant\nles mêmes contrats d'API que la plateforme Web.",
        palette=C_FRONTEND
    )

    # Card 1.4: Dashboard Business Streamlit
    b.add_card(
        x=1900, y=210, w=620, h=350,
        title="Cockpit Analytique & Business",
        subtitle="Chemin: analytics/dashboards/business_dashboard.py",
        bullets=[
            "Visualisation Streamlit des KPIs d'inventaire et de prix",
            "Suivi de la distribution des prix par marque et segment",
            "Monitoring des flux de scraping et taux de conversion",
            "Intégration dbt: avg_price_by_brand.sql pour agrégats analytiques"
        ],
        comment_text="Tableau de bord interactif Python consommant directement la base\nPostgreSQL pour le pilotage commercial et technique.",
        why_text="Permet aux équipes métier d'analyser le marché sans surcharger\nl'API applicative principale.",
        palette=C_ANALYTICS
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 2. COUCHE GATEWAY & ROUTAGE BACKEND (X: 50 .. 2550, Y: 620 .. 1000)
    # ══════════════════════════════════════════════════════════════════════════
    b.add_rect(50, 620, 2500, 380, C_GATEWAY["border"], "#082f49", stroke_width=1, radius=16, opacity=50)
    b.add_text(70, 635, "⚡ COUCHE 2 — BACKEND FASTAPI & COEUR TRANSACTIONNEL (backend/app/api/ & core/)", color=C_GATEWAY["text"], font_size=18, font_family=2)

    # Card 2.1: FastAPI Main Gateway & Sécurité
    b.add_card(
        x=70, y=670, w=580, h=310,
        title="API Gateway & Sécurité (main.py)",
        subtitle="Middlewares: CORS, SecurityHeaders, AuditLog, RateLimiting",
        bullets=[
            "Routeurs enregistrés: 24 fichiers de routes spécialisés",
            "Rate Limiting: slowapi (protection brute-force sur auth)",
            "Audit Logging: log systématique des 401/403 avec IP & endpoint",
            "Gestion globale des exceptions: RequestValidationError custom",
            "Documentation automatique OpenAPI: /docs et /redoc"
        ],
        comment_text="FastAPI async orchestre l'ensemble des modules. Injecte la session\nSQLAlchemy async (get_db) et valide chaque payload via Pydantic.",
        why_text="L'asynchronisme natif (async/await) garantit un débit élevé\nsur les requêtes LLM, vectorielles et relationnelles simultanées.",
        palette=C_GATEWAY
    )

    # Card 2.2: Auth & Gestion Utilisateurs
    b.add_card(
        x=680, y=670, w=580, h=310,
        title="Auth, OTP & Confiance (routes_auth.py)",
        subtitle="Chemin: routes_auth.py, routes_users.py, otp_service.py",
        bullets=[
            "Inscription & OTP: Code à 6 chiffres envoyé via Mailer SMTP",
            "Tokens: JWT asymétrique (durée 60 min), hashage BCrypt",
            "Rôles: buyer, seller, admin + gestion permissions",
            "TrustScore: Vérification profil, badges vendeur & historique"
        ],
        comment_text="Gère le cycle de vie utilisateur avec vérification d'email par OTP\net génération de JWT sécurisé pour l'accès aux routes protégées.",
        why_text="Évite les faux comptes et le spam d'annonces sur la plateforme\nglobale marocaine.",
        palette=C_GATEWAY
    )

    # Card 2.3: Catalogue, Véhicules & Options
    b.add_card(
        x=1290, y=670, w=580, h=310,
        title="Catalogue Neuf & Comparateur Matrice",
        subtitle="Chemin: routes_new_catalog.py, routes_comparator.py",
        bullets=[
            "CRUD Véhicules Neufs: Finitions, prix remisés, packs",
            "Comparateur: Comparaison côte-à-côte de 2 à 4 véhicules",
            "Options & Packs: Équipements de série vs optionnels",
            "Réservation d'Essai: routes_test_drives.py lié aux showrooms"
        ],
        comment_text="Expose le catalogue certifié et calcule les deltas d'équipements\net de prix entre finitions concurrentes.",
        why_text="Fournit aux acheteurs une transparence totale sur les prix\nconcessionnaires réels négociés.",
        palette=C_GATEWAY
    )

    # Card 2.4: Fiscalité Marocaine & Dédouanement
    b.add_card(
        x=1900, y=670, w=620, h=310,
        title="Fiscalité Marocaine & Dédouanement",
        subtitle="Chemin: moroccan_taxes.py, customs_service.py",
        bullets=[
            "Taxe Dédouanement: Barème officiel douane marocaine (DI, TVA, TIC)",
            "Vignette Automobile: Barème CV fiscaux selon cylindrée & carburant",
            "Frais d'Immatriculation: Carte grise et frais de dossier réels",
            "Estimation TCO: Coût Total de Possession sur 3 à 5 ans"
        ],
        comment_text="Calculateur mathématique déterministe appliquant strictement les règles\nfiscales marocaines en vigueur.",
        why_text="Les acheteurs au Maroc exigent le prix 'clé en main' incluant taxes\net immatriculation avant toute décision.",
        palette=C_GATEWAY
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 3. COEUR DE L'INTELLIGENCE & RECOMMANDATION (X: 50 .. 2550, Y: 1040 .. 1560)
    # ══════════════════════════════════════════════════════════════════════════
    b.add_rect(50, 1040, 2500, 500, C_DETERMINISTIC["border"], "#022c22", stroke_width=1, radius=16, opacity=50)
    b.add_text(70, 1055, "🧠 COUCHE 3 — MOTEUR DÉTERMINISTE 8D & ASSISTANT CONSULTATIF (ml/recommendation/ & rag/)", color=C_DETERMINISTIC["text"], font_size=18, font_family=2)

    # Card 3.1: Assistant Consultatif 2 Phases (RAG)
    b.add_card(
        x=70, y=1090, w=580, h=430,
        title="Assistant Consultatif RAG 2 Phases",
        subtitle="Chemin: rag/consultative_flow.py, chatbot_chain.py",
        bullets=[
            "Phase 1 - Découverte: Pose 1-2 questions ciblées, pas de suggestion",
            "Accumulation incrémentale: Profil Pydantic (NeedsProfile) enrichi",
            "Support Multilingue: Français, Darija marocaine, Arabe, Anglais",
            "Phase 2 - Restitution: Déclenchée UNIQUEMENT si Budget + Usage validés",
            "Mémoire de session: conversation_memory.py (historique conversation)",
            "Règle d'or: Le LLM argumente, le moteur ML calcule et certifie"
        ],
        comment_text="Le flux extrait par regex/NLP les critères, refuse toute recommandation\nprématurée et délègue la sélection au moteur déterministe.",
        why_text="Empêche l'effet 'catalogue froid' et garantit un conseil personnalisé\nrespectant la psychologie d'achat automobile.",
        palette=C_AI_RAG
    )

    # Card 3.2: Moteur de Scoring 8 Dimensions
    b.add_card(
        x=680, y=1090, w=580, h=430,
        title="Moteur de Scoring Déterministe 8D",
        subtitle="Chemin: ml/recommendation/eight_dimension_scorer.py",
        bullets=[
            "1. Espace / Habitabilité: Volume coffre, 5/7 places, carrosserie",
            "2. Sécurité: Note Euro NCAP, ADAS, ancienneté du modèle",
            "3. Coût Réel (TCO): Consommation L/100km, électrique/hybride",
            "4. Prix d'Accès: Positionnement tarifaire vs marché marocain",
            "5. Praticité Urbaine: Longueur gabarit (<4m = 5/5), rayon braquage",
            "6. Performance: Puissance ch, couple moteur, dynamisme",
            "7. Écologie: Émissions CO2 g/km, vignette verte",
            "8. Motricité: Transmission intégrale 4x4, garde au sol SUV"
        ],
        comment_text="Score chaque véhicule de 1.0 à 5.0 selon des formules mathématiques\ncalibrées sur les specs réelles ou scores précalculés en base.",
        why_text="Garantit une objectivité absolue : aucune boîte noire, chaque score\nest traçable à une donnée technique vérifiable.",
        palette=C_DETERMINISTIC
    )

    # Card 3.3: Pondération Dynamique & Sélecteur Top 3
    b.add_card(
        x=1290, y=1090, w=580, h=430,
        title="Pondération Personas & Top 3 Certifié",
        subtitle="Chemin: dynamic_weighting.py, top3_selector.py",
        bullets=[
            "Personas: Famille (Espace+Sécu), Urbain (Praticité+Coût), Pro (TCO)",
            "Priorités utilisateur: Boost de +15% sur les critères choisis",
            "Filtres durs préalables: Budget max (+15% tolérance), carburant, boîte",
            "Cascade de relâchement ordonnée si < 3 candidats trouvés",
            "Diversité de marques: Max 2 véhicules d'une même marque dans le Top 3",
            "Compromis explicites: Extraction automatique des points faibles (<3/5)"
        ],
        comment_text="Combine les poids du persona et les filtres durs pour classer\nles candidats et générer les points forts / compromis.",
        why_text="L'honnêteté sur les compromis (faiblesses) renforce la confiance\nradicale de l'acheteur envers Wakala.",
        palette=C_DETERMINISTIC
    )

    # Card 3.4: Garde-Fou de Conformité Anti-Hallucination
    b.add_card(
        x=1900, y=1090, w=620, h=430,
        title="Garde-Fou Anti-Hallucination",
        subtitle="Chemin: ml/recommendation/compliance_guard.py",
        bullets=[
            "Vérification PostgreSQL stricte: Tout véhicule recommandé DOIT exister",
            "Contrôle de disponibilité: Exclusion immédiate si status = 'sold'",
            "Contrôle de prix: Exclusion obligatoire si prix = NULL ou < 10 000 MAD",
            "Sanitisation UUID: Rejet immédiat de tout format d'identifiant invalide",
            "Filtrage hermétique: Le LLM ne reçoit JAMAIS un ID non validé"
        ],
        comment_text="Interroge la base PostgreSQL en temps réel pour certifier chaque ID\navant qu'il ne soit injecté dans le contexte du LLM.",
        why_text="Élimine 100% du risque d'hallucination de modèles ou de prix inexistants\npar le modèle génératif.",
        palette=C_DETERMINISTIC
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 4. GESTION DU CONSENTEMENT CNDP & OUTREACH (X: 50 .. 2550, Y: 1580 .. 1980)
    # ══════════════════════════════════════════════════════════════════════════
    b.add_rect(50, 1580, 2500, 380, C_OUTREACH["border"], "#500724", stroke_width=1, radius=16, opacity=50)
    b.add_text(70, 1595, "📬 COUCHE 4 — CONSENTEMENT CNDP & CYCLE D'OUTREACH 0-60 JOURS (outreach/ & api/routes_consent.py)", color=C_OUTREACH["text"], font_size=18, font_family=2)

    # Card 4.1: Registre de Consentement Loi 09-08
    b.add_card(
        x=70, y=1630, w=580, h=310,
        title="Registre de Consentement (CNDP)",
        subtitle="Chemin: routes_consent.py, models/outreach.py, Migration 019",
        bullets=[
            "Enregistrement explicite: POST /api/consent (Canal, finalité, source)",
            "Droit de retrait (Opt-out): DELETE /api/consent/{id} horodaté",
            "Vérification systématique: Check de validité avant CHAQUE envoi d'outreach",
            "Index partiel PostgreSQL: idx_prospect_consents_active pour perf",
            "Conformité légale: Respect strict de la loi marocaine 09-08"
        ],
        comment_text="Maintient une table d'audit des consentements avec opt_out_at.\nToute révocation interrompt immédiatement toutes les séquences.",
        why_text="Assure la conformité juridique marocaine et protège les utilisateurs\ncontre tout contact non sollicité.",
        palette=C_OUTREACH
    )

    # Card 4.2: Séquenceur d'Outreach 6 Jalons
    b.add_card(
        x=680, y=1630, w=580, h=310,
        title="Séquence d'Engagement 0-60 Jours",
        subtitle="Chemin: outreach/sequence_definitions.py, message_templates.py",
        bullets=[
            "J0: Récapitulatif Top 3 personnalisé par email (immédiat)",
            "J2-3: Fiches détaillées & catalogue interactif (WhatsApp)",
            "J7: Matrice TCO comparative sur 5 ans (Email)",
            "J14: Proposition de mise en relation & essai concessionnaire",
            "J45: Alerte prix (Uniquement si vraie baisse ≥ 1000 MAD en base)",
            "J60: Clôture bienveillante de suivi automatique (Fin de séquence)"
        ],
        comment_text="Génère des messages personnalisés injectant les données réelles du Top 3.\nChaque template inclut une porte de sortie claire ('STOP').",
        why_text="Accompagne le prospect sur la durée moyenne de réflexion d'achat\n(45-60 jours au Maroc) sans pression commerciale.",
        palette=C_OUTREACH
    )

    # Card 4.3: Conditions d'Arrêt & Mode Simulé
    b.add_card(
        x=1290, y=1630, w=580, h=310,
        title="Conditions d'Arrêt & Garde-Fous",
        subtitle="Chemin: outreach/stop_conditions.py, outreach_scheduler.py",
        bullets=[
            "Arrêt 1: Achat confirmé dans la table transactions",
            "Arrêt 2: Essai routier réservé (table test_drive_bookings)",
            "Arrêt 3: Consentement retiré par l'utilisateur (opt-out)",
            "Mode Simulé actif: Logs en base/console sans envoi réel non désiré",
            "Règle stricte: Aucun message envoyé après un arrêt confirmé"
        ],
        comment_text="Évalue les 3 conditions d'arrêt avant tout traitement de jalon.\nSi déclenché, bascule le statut en 'stopped' avec motif horodaté.",
        why_text="Évite le harcèlement d'un prospect qui a déjà acheté son véhicule\nou qui s'est désabonné.",
        palette=C_OUTREACH
    )

    # Card 4.4: DAG Airflow Quotidien
    b.add_card(
        x=1900, y=1630, w=620, h=310,
        title="Orchestration DAG Airflow Outreach",
        subtitle="Chemin: data_pipeline/airflow/dags/outreach_daily_check_dag.py",
        bullets=[
            "Fréquence: Quotidien à 09:00 UTC (10:00 heure Casablanca)",
            "Tâche 1 - Fetch: Sélectionne les séquences actives échues (next_scheduled_at <= NOW)",
            "Tâche 2 - Process: Évalue stop conditions, rend template, avance jalon",
            "Tâche 3 - Report: Résume les volumes traités et envoyés via XCom",
            "Index partiel: idx_outreach_active_scheduled pour requête éclair"
        ],
        comment_text="DAG Airflow automatisant le traitement quotidien des jalons dus,\navec gestion des transactions asynchrones SQLAlchemy.",
        why_text="Délègue l'ordonnancement temporel lourd à Airflow sans bloquer\nle serveur applicatif FastAPI.",
        palette=C_OUTREACH
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 5. DATA PIPELINE, INGESTION & BASES DE DONNÉES (X: 50 .. 2550, Y: 2020 .. 2540)
    # ══════════════════════════════════════════════════════════════════════════
    b.add_rect(50, 2020, 2500, 500, C_DATA_INGESTION["border"], "#451a03", stroke_width=1, radius=16, opacity=50)
    b.add_text(70, 2035, "📥 COUCHE 5 — INGESTION, SCRAPING, STREAMING & BASES DE DONNÉES (data_pipeline/ & database/)", color=C_DATA_INGESTION["text"], font_size=18, font_family=2)

    # Card 5.1: Écosystème Scrapers Multi-Sources
    b.add_card(
        x=70, y=2070, w=580, h=430,
        title="Robots de Scraping & Quarantaine",
        subtitle="Chemin: data_pipeline/scrapers/marketplaces/ & concessionaires/",
        bullets=[
            "Marketplaces: Avito.ma, Moteur.ma, Wandaloo, Spoticar, Otoclic, Kifal",
            "Concessionnaires Neufs: Dacia Maroc, Renault Maroc",
            "Priorité JSON-LD: Extraction structurée sans IA quand possible",
            "Fallback LLM: Extraction Pydantic via GPT/Qwen si pas de JSON-LD",
            "Service Quarantaine: Détection anomalies de prix avant injection",
            "Kafka Producer: Publication des annonces brutes dans listings.raw"
        ],
        comment_text="Scrapeurs asynchrones extrayant les fiches techniques, prix et photos.\nValident la cohérence des données avant publication Kafka.",
        why_text="Alimente continuellement le catalogue avec les stocks réels\ndu marché marocain.",
        palette=C_DATA_INGESTION
    )

    # Card 5.2: Pipeline Kafka & Jobs Spark
    b.add_card(
        x=680, y=2070, w=580, h=430,
        title="Streaming Kafka & Spark Jobs",
        subtitle="Chemin: data_pipeline/kafka/ & data_pipeline/spark/",
        bullets=[
            "Kafka KRaft: Topics listings.raw, listings.silver, user.interactions",
            "Spark Streaming: clean_listings_job.py, clean_interactions_job.py",
            "Spark Batch: aggregate_gold_job.py, silver_to_gold.py",
            "Consumer PostgreSQL: consume_to_postgres.py écrit en base relationnelle",
            "Architecture Médaillon: Bronze (Raw) → Silver (Clean) → Gold (Aggregated)"
        ],
        comment_text="Structure les flux temps-réel d'annonces et d'événements utilisateurs\npour l'entraînement ML et l'analyse.",
        why_text="Garantit l'idempotence, le dédoublonnage et la résilience lors des gros\nvolumes de scraping.",
        palette=C_DATA_INGESTION
    )

    # Card 5.3: Stockage Polyglotte (PostgreSQL, Qdrant, Neo4j)
    b.add_card(
        x=1290, y=2070, w=580, h=430,
        title="Bases de Données & Stockage Polyglotte",
        subtitle="Chemin: database/postgres/, vector-store/, neo4j/",
        bullets=[
            "PostgreSQL 16 (Port 5433): 20 migrations (users, vehicles, outreach...)",
            "Table vehicle_wakala_scores: Source de vérité des 8 scores précalculés",
            "Qdrant (Port 6333): Collection vehicle_embeddings (recherche sémantique)",
            "Neo4j Graphe (Port 7687): Graphe utilisateurs/IP/téléphones pour fraude",
            "pgvector / Qdrant RAG: Embeddings textuels pour similarité de besoin"
        ],
        comment_text="PostgreSQL stocke la vérité transactionnelle, Qdrant gère l'espace vectoriel\net Neo4j analyse les topologies de fraude.",
        why_text="Chaque modèle de données est stocké dans le moteur optimal pour\nson mode d'interrogation (relationnel, vectoriel, graphe).",
        palette=C_STORAGE
    )

    # Card 5.4: DAGs Airflow & Scheduler
    b.add_card(
        x=1900, y=2070, w=620, h=430,
        title="DAGs Airflow de Maintenance & Qualité",
        subtitle="Chemin: data_pipeline/airflow/dags/",
        bullets=[
            "daily_pipeline.py: Ingestion et synchronisation quotidienne",
            "data_quality_check_dag.py: Audit des prix anormaux & doublons",
            "weekly_model_retrain_dag.py: Réentraînement hebdo du modèle de pricing",
            "outreach_daily_check_dag.py: Traitement des relances 0-60 jours",
            "backend/scheduler.py: Tâches de fond locales (vérification statut)"
        ],
        comment_text="Orchestre les pipelines de données, de contrôle qualité et de relances\nautomatisées selon des plannings cron définis.",
        why_text="Automatise l'exploitation de la plateforme et garantit la fraîcheur\npermanente des données.",
        palette=C_DATA_INGESTION
    )

    # ══════════════════════════════════════════════════════════════════════════
    # 6. FLÈCHES DE FLUX RÉELS CONFIRMÉS (INTER-COU мест)
    # ══════════════════════════════════════════════════════════════════════════
    # Frontend -> Backend Gateway
    b.add_arrow(360, 560, 360, 670, stroke="#3b82f6", stroke_width=3, label="REST API (Axios /api/*)")
    b.add_arrow(1580, 560, 1580, 670, stroke="#3b82f6", stroke_width=2, label="Mobile API Sync")

    # Gateway -> Intelligence / Moteur
    b.add_arrow(360, 980, 360, 1090, stroke="#8b5cf6", stroke_width=3, label="Dialogue Chatbot RAG")
    b.add_arrow(970, 980, 970, 1090, stroke="#10b981", stroke_width=3, label="Calcul Scores 8D")
    b.add_arrow(1580, 980, 1580, 1090, stroke="#10b981", stroke_width=2, label="Sélection Top 3")

    # Intelligence -> Compliance Guard & Base
    b.add_arrow(1870, 1300, 1900, 1300, stroke="#10b981", stroke_width=3, label="Validation DB")
    b.add_arrow(2210, 1520, 1580, 2070, stroke="#6366f1", stroke_width=3, label="Vérification Existence PostgreSQL")

    # Outreach -> Base & DAG
    b.add_arrow(360, 1520, 360, 1630, stroke="#ec4899", stroke_width=2, label="Déclenchement Post Top 3")
    b.add_arrow(1580, 1940, 1580, 2070, stroke="#ec4899", stroke_width=2, label="Lecture/Écriture Séquences")
    b.add_arrow(2210, 1940, 2210, 2070, stroke="#ec4899", stroke_width=2, label="Exécution DAG Airflow")

    # Scrapers -> Kafka -> Spark -> Postgres
    b.add_arrow(650, 2280, 680, 2280, stroke="#f59e0b", stroke_width=2, label="Kafka Topic (raw)")
    b.add_arrow(1260, 2280, 1290, 2280, stroke="#f59e0b", stroke_width=3, label="Écriture PostgreSQL & Qdrant")

    # ══════════════════════════════════════════════════════════════════════════
    # 7. SECTION CRITIQUE : ÉCARTS CONSTATÉS (CODE RÉEL VS SPÉCIFICATIONS)
    # ══════════════════════════════════════════════════════════════════════════
    b.add_rect(50, 2580, 2500, 380, C_ALERT["border"], "#450a0a", stroke_width=2, radius=16)
    b.add_text(80, 2600, "⚠️ SECTION D'AUDIT — ÉCARTS CONSTATÉS ENTRE SPÉCIFICATIONS ET CODE RÉEL SUR DISQUE", color="#fca5a5", font_size=20, font_family=2)
    b.add_text(80, 2630, "Cette section documente les éléments décrits dans la documentation théorique mais absents, partiels ou adaptés dans le code réel :", color=TEXT_MUTED, font_size=13, font_family=2)

    # Box Alert 1: Vision & Dégâts
    b.add_rect(80, 2660, 560, 270, C_ALERT["border"], "#1f0707", stroke_width=1, radius=8)
    b.add_text(96, 2675, "1. Computer Vision (damage_detector.py)", color="#fca5a5", font_size=15, font_family=2)
    b.add_text(96, 2700, "• Spécifié : Modèle Deep Learning YOLO / ResNet pour détection\n  complexe de rayures et bosses.\n• Réellement implémenté : Heuristique simple OpenCV basée sur\n  le filtre de Canny (densité de contours). Pas de modèle lourd chargé.\n• Impact : Fonctionnel pour démo/test, mais non robuste pour une\n  expertise de carrosserie industrielle.", color=TEXT_WHITE, font_size=12, font_family=2, line_height=1.35)

    # Box Alert 2: Détection de Fraude Neo4j
    b.add_rect(680, 2660, 560, 270, C_ALERT["border"], "#1f0707", stroke_width=1, radius=8)
    b.add_text(696, 2675, "2. Graphe de Fraude (broker_detector.py)", color="#fca5a5", font_size=15, font_family=2)
    b.add_text(696, 2700, "• Spécifié : Graphe Neo4j live en temps réel pour flagger les courtiers.\n• Réellement implémenté : Requêtes Cypher écrites et prêtes, mais\n  l'exécution dépend de la présence d'une instance Neo4j active.\n• Fallback : Détection d'anomalie IsolationForest locale présente\n  en standalone dans ml/anomaly/detector.py.", color=TEXT_WHITE, font_size=12, font_family=2, line_height=1.35)

    # Box Alert 3: Pivot Véhicules Neufs vs Occasion
    b.add_rect(1280, 2660, 560, 270, C_ALERT["border"], "#1f0707", stroke_width=1, radius=8)
    b.add_text(1296, 2675, "3. Pivot Neuf vs Occasion (price_model.py)", color="#fca5a5", font_size=15, font_family=2)
    b.add_text(1296, 2700, "• Spécifié initialement : Prédiction prix occasion (Argus kilométrique).\n• Réellement implémenté : Le modèle XGBoost a été pivoté pour prédire\n  le prix négocié en concession (Véhicules Neufs 0 km).\n• Suppression : Features 'mileage' et 'condition_score' retirées du\n  modèle d'entraînement actif (car km=0 pour du neuf).", color=TEXT_WHITE, font_size=12, font_family=2, line_height=1.35)

    # Box Alert 4: Mode Outreach Simulé
    b.add_rect(1880, 2660, 640, 270, C_ALERT["border"], "#1f0707", stroke_width=1, radius=8)
    b.add_text(1896, 2675, "4. Outreach 0-60 Jours en Mode Simulé", color="#fca5a5", font_size=15, font_family=2)
    b.add_text(1896, 2700, "• Spécifié : Envois réels de messages WhatsApp Business API et SMS.\n• Réellement implémenté : Mode 'SIMULÉ' par défaut dans outreach_scheduler.py.\n  Les messages sont loggés en base et en console, mais pas envoyés vers\n  une passerelle tierce payante tant que l'intégration n'est pas branchée.\n• Sécurité : Conformité CNDP totale et tests d'envoi unitaires validés.", color=TEXT_WHITE, font_size=12, font_family=2, line_height=1.35)

    # ══════════════════════════════════════════════════════════════════════════
    # 8. LÉGENDE DES COULEURS & RESPONSABILITÉS
    # ══════════════════════════════════════════════════════════════════════════
    b.add_rect(50, 3000, 2500, 120, "#374151", "#0f172a", stroke_width=1, radius=12)
    b.add_text(80, 3015, "🎨 LÉGENDE DU CODE COULEUR PAR TYPE DE RESPONSABILITÉ :", color=TEXT_WHITE, font_size=14, font_family=2)

    legends = [
        ("Application & IHM", C_FRONTEND["border"]),
        ("Gateway & Auth", C_GATEWAY["border"]),
        ("Calcul Déterministe (ML 8D)", C_DETERMINISTIC["border"]),
        ("IA & RAG Consultatif", C_AI_RAG["border"]),
        ("Outreach & Consentement", C_OUTREACH["border"]),
        ("Ingestion & Scrapers", C_DATA_INGESTION["border"]),
        ("Stockage Polyglotte", C_STORAGE["border"]),
        ("Écarts / Alertes Audit", C_ALERT["border"])
    ]

    leg_x = 80
    for label, color in legends:
        b.add_rect(leg_x, 3050, 20, 20, color, color, stroke_width=1, radius=4)
        b.add_text(leg_x + 30, 3052, label, color=TEXT_MUTED, font_size=13, font_family=2)
        leg_x += 300

    return b.to_dict()


if __name__ == "__main__":
    excalidraw_data = build_architecture_diagram()
    
    # Save to docs/ and Livrables/
    p1 = Path("d:/Projet automobile/vente-auto-platform/docs/architecture_reelle_wakala.excalidraw")
    p2 = Path("d:/Projet automobile/vente-auto-platform/Livrables/Wakala_Architecture_Reelle.excalidraw")
    
    p1.parent.mkdir(parents=True, exist_ok=True)
    p2.parent.mkdir(parents=True, exist_ok=True)
    
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(excalidraw_data, f, indent=2, ensure_ascii=False)
        
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(excalidraw_data, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {len(excalidraw_data['elements'])} elements into:")
    print(f"- {p1}")
    print(f"- {p2}")
