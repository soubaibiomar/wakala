# Wakala — Documentation Complète des Fonctionnalités

> **Wakala** est une marketplace automobile intelligente propulsée par l'IA, conçue pour le marché marocain. Ce document détaille l'ensemble des idées et modules implémentés dans le projet, avec leur fonctionnement technique.

---

## Table des Matières

1. [Architecture Globale](#1-architecture-globale)
2. [Système d'Authentification & Sécurité](#2-système-dauthentification--sécurité)
3. [Scraping IA & Ingestion de Données](#3-scraping-ia--ingestion-de-données)
4. [Moteur de Recherche Vectorielle (RAG)](#4-moteur-de-recherche-vectorielle-rag)
5. [Chatbot IA Conversationnel](#5-chatbot-ia-conversationnel)
6. [Argus Intelligent (Prédiction de Prix)](#6-argus-intelligent-prédiction-de-prix)
7. [Moteur de Recommandation Hybride](#7-moteur-de-recommandation-hybride)
8. [Computer Vision (Analyse d'Images)](#8-computer-vision-analyse-dimages)
9. [Détection de Fraude (Graphe Neo4j)](#9-détection-de-fraude-graphe-neo4j)
10. [Détection d'Anomalies (Isolation Forest)](#10-détection-danomalies-isolation-forest)
11. [Analyse de Sentiment (NLP)](#11-analyse-de-sentiment-nlp)
12. [Segmentation des Acheteurs (K-Means)](#12-segmentation-des-acheteurs-k-means)
13. [Simulateur de Dédouanement](#13-simulateur-de-dédouanement)
14. [Système d'Escrow (Séquestre)](#14-système-descrow-séquestre)
15. [Health Checker (Disponibilité des Annonces)](#15-health-checker-disponibilité-des-annonces)
16. [Carnet d'Entretien Véhicule](#16-carnet-dentretien-véhicule)
17. [Dashboard Unifié (Bento Grid)](#17-dashboard-unifié-bento-grid)
18. [Sécurité de Niveau Production](#18-sécurité-de-niveau-production)
19. [Détails Techniques & Mathématiques des Algorithmes](#19-détails-techniques--mathématiques-des-algorithmes)
20. [Stratégies de Déploiement & Scaling](#20-stratégies-de-déploiement--scaling)

---

## 1. Architecture Globale

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18 + TypeScript)          │
│                  Vite • React Router • React Query           │
└───────────────────────────┬──────────────────────────────────┘
                            │ REST API (JSON)
┌───────────────────────────▼──────────────────────────────────┐
│                    BACKEND (FastAPI / Python)                 │
│        Async • SQLAlchemy ORM • Pydantic Validation          │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│PostgreSQL│  Qdrant  │  Neo4j   │  OpenAI  │   XGBoost/ML    │
│(pgvector)│ (Vector) │ (Graph)  │  (LLM)   │   (Pricing)     │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Frontend | React 18, TypeScript, Vite | UI Premium, Dark Mode, Responsive |
| Backend | FastAPI, SQLAlchemy (async) | API REST, Business Logic |
| Base Relationnelle | PostgreSQL | Véhicules, Users, Annonces, Transactions |
| Base Vectorielle | Qdrant | Embeddings véhicules pour recherche sémantique |
| Base Graphe | Neo4j | Détection de fraude, similarité véhicules |
| LLM | OpenAI GPT-4o-mini | Chatbot, extraction sémantique scraping |
| ML | XGBoost, Isolation Forest, K-Means | Pricing, anomalies, segmentation |
| Vision | OpenCV, YOLO | Détection de dommages, floutage de plaques |
| NLP | HuggingFace Transformers | Analyse de sentiment des avis |

---

## 2. Système d'Authentification & Sécurité

### Comment ça marche
1. **Inscription** : L'utilisateur s'inscrit avec email + mot de passe. Un **OTP (One-Time Password)** à 6 chiffres est envoyé par email via SMTP.
2. **Vérification** : L'utilisateur saisit l'OTP pour activer son compte. Les OTP expirent après un délai configurable.
3. **Connexion** : Un **JWT (JSON Web Token)** est généré avec une durée de vie de 60 minutes. Stocké côté client dans `localStorage`.
4. **Rôles** : Trois rôles — `buyer`, `seller`, `admin` — contrôlent l'accès aux fonctionnalités.

### Sécurité Appliquée
| Mesure | Détail |
|--------|--------|
| **Rate Limiting** | `slowapi` — 3 req/15 min sur `/register` et `/verify-email` |
| **Headers HTTP** | `X-Frame-Options: DENY`, `HSTS`, `nosniff`, `CSP` |
| **Audit Logging** | Middleware qui log toutes les réponses 401/403 avec l'IP |
| **Route Guard Frontend** | Redirection immédiate vers `/login` si token absent |
| **PII Redaction** | Masquage automatique des emails/téléphones avant envoi au LLM |

> **Fichiers clés** : `routes_auth.py`, `middlewares/security.py`, `AuthContext.tsx`

---

## 3. Scraping IA & Ingestion de Données

### Idée
Construire un catalogue automobile complet en temps quasi-réel à partir des annonces publiées sur les sites marocains (Avito.ma, Moteur.ma).

### Comment ça marche

```
Page HTML ──► JSON-LD ──► Données structurées ✓
     │
     └──► (si absent) ──► Texte brut ──► GPT-4o-mini ──► Pydantic Model ✓
```

1. **Priorité 1 — JSON-LD** : Le parseur cherche les balises `<script type="application/ld+json">` dans le HTML. Si un schéma `Car`, `Vehicle` ou `Product` est trouvé, les données sont extraites directement (fiabilité maximale).

2. **Priorité 2 — Extraction LLM** : Si le JSON-LD est absent, le texte brut est nettoyé (suppression `<script>`, `<nav>`, `<footer>`), tronqué à 15 000 caractères, puis envoyé à `gpt-4o-mini` avec `structured_output` pour extraire un modèle Pydantic strict (`ScrapedVehicleData`).

3. **Circuit Breaker** : Si le LLM échoue 3 fois consécutives, le circuit "s'ouvre" (pause de 60 secondes). L'URL en échec est enregistrée dans la table `failed_scrapes` pour un retry ultérieur via `retry_failed.py`.

4. **Scrapers spécialisés** :
   - **Avito.ma** : Parse le JSON intégré dans `__NEXT_DATA__` (Next.js).
   - **Moteur.ma** : Parse le HTML avec BeautifulSoup (extraction par cartes CSS).

> **Fichiers clés** : `hybrid_parser.py`, `avito.py`, `moteur.py`, `retry_failed.py`, `FailedScrape` model

---

## 4. Moteur de Recherche Vectorielle (RAG)

### Idée
Permettre une recherche sémantique en langage naturel ("une voiture familiale diesel pas chère à Casablanca") au lieu d'une recherche par filtres.

### Comment ça marche

```
Véhicule en BD ──► Génération description textuelle ──► text-embedding-3-small ──► Vecteur 1536D ──► Qdrant
                                                                                                        │
Requête utilisateur ──► Embedding ──► Recherche par similarité cosinus ──────────────────────────────────┘
```

1. **Ingestion** : Chaque véhicule est transformé en description textuelle ("`Dacia Sandero 2020 diesel, 45000km, Casablanca, 95000 MAD`"), puis converti en vecteur via `text-embedding-3-small` (OpenAI) et stocké dans **Qdrant**.

2. **Recherche** : La requête utilisateur est aussi convertie en vecteur. Qdrant effectue une **recherche par similarité cosinus** et retourne les top-K véhicules les plus pertinents.

3. **Filtres** : Des filtres Qdrant supplémentaires sont appliqués (prix max, statut `available`).

4. **Synchronisation Near Real-Time** : Grâce à `BackgroundTasks` de FastAPI, chaque création/modification/suppression de véhicule met à jour Qdrant automatiquement sans bloquer l'API.

> **Fichiers clés** : `ingestion.py`, `sync.py`, `qdrant.py`, `chat.py`

---

## 5. Chatbot IA Conversationnel

### Idée
Un assistant virtuel expert automobile marocain qui répond en français et en Darija, recommande des véhicules concrets du catalogue, et guide l'utilisateur.

### Comment ça marche

```
Message utilisateur
    │
    ▼
sanitize_input() ──► redact_pii() ──► Analyse d'intention (LLM JSON mode)
    │                                        │
    │                            ┌────────────┴─────────────────┐
    │                            │                              │
    │                      car_search                    general_advice
    │                            │                              │
    │                   Recherche Qdrant                   Réponse directe
    │                            │                              │
    └────────────► Construction prompt ◄────────────────────────┘
                            │
                      GPT-4o-mini (streaming)
                            │
                      Réponse en temps réel
```

1. **Analyse d'intention** : Un premier appel LLM (JSON mode) détermine l'intention (`car_search`, `maintenance_check`, `general_advice`, `customs`) et le budget max éventuel.

2. **Récupération RAG** : Si l'intention est `car_search`, les véhicules pertinents sont récupérés depuis Qdrant et injectés dans le contexte du prompt.

3. **Génération** : Le prompt système inclut les véhicules trouvés, une persona d'expert marocain, et des règles de formatage (cartes JSON pour l'affichage riche). La réponse est streamée token par token.

4. **Guardrails** :
   - `sanitize_input()` : Supprime les caractères de contrôle, limite à 500 caractères.
   - `redact_pii()` : Masque emails et téléphones marocains (`[EMAIL_MASKED]`, `[PHONE_MASKED]`).
   - Protection anti-prompt-injection dans le system prompt.

5. **Rate Limiting** : 10 messages/minute maximum par utilisateur (via `slowapi`).

> **Fichiers clés** : `chat.py`, `ai.py`, `ChatbotWidget.tsx`, `ChatMessage.tsx`

---

## 6. Argus Intelligent (Prédiction de Prix)

### Idée
Estimer la valeur de marché d'un véhicule au Maroc en analysant les données historiques, comme un "Argus" marocain alimenté par le Machine Learning.

### Comment ça marche

```
Véhicule (marque, modèle, année, km, ville, carburant...)
    │
    ▼
Feature Engineering:
  - vehicle_age = 2026 - année
  - annual_mileage = km / age
  - condition_score (si disponible)
    │
    ▼
Label Encoding (catégoriques) ──► StandardScaler (numériques)
    │
    ▼
XGBoost Regressor ──► Prix prédit (MAD) + Intervalle de confiance
```

1. **Feature Engineering** :
   - `vehicle_age` : Âge du véhicule.
   - `annual_mileage` : Kilométrage annuel moyen.
   - Variables catégorielles encodées via `LabelEncoder`.
   - Variables numériques normalisées via `StandardScaler`.

2. **Modèle** : `XGBRegressor` entraîné sur les données scrapées. Sauvegardé en format `.ubj` avec ses encodeurs et scaler en `.pkl`.

3. **Fallback** : Si le modèle n'est pas encore entraîné (cold start), un prix par défaut de 150 000 MAD est retourné.

4. **Entraînement** : Un script `train_pricing.py` charge les véhicules depuis PostgreSQL, applique le feature engineering, entraîne le modèle et sauvegarde les artefacts.

> **Fichiers clés** : `price_model.py`, `train_pricing.py`, `price_predictor.py`, `routes_pricing.py`

---

## 7. Moteur de Recommandation Hybride

### Idée
Combiner la recommandation basée sur le contenu (similarité véhicule) et la recommandation collaborative (comportement des utilisateurs similaires) pour des suggestions ultra-pertinentes.

### Comment ça marche

```
                    ┌── Content-Based ──► Score contenu (similarité features)
Utilisateur ────────┤
                    └── Collaborative ──► Score collaboratif (historique utilisateurs)
                                │
                                ▼
                    Hybrid Engine: α × content + (1-α) × collaborative
                                │
                                ▼
                    Liste triée de recommandations + match_score (%)
```

1. **Content-Based** : Calcule la similarité entre le profil de l'utilisateur (budget, type de carrosserie préféré) et les caractéristiques des véhicules en base.

2. **Collaborative** : Analyse les interactions des utilisateurs similaires (véhicules consultés, favoris) pour identifier des patterns.

3. **Hybride** : Le `HybridEngine` combine les deux scores avec un coefficient `α` (60% content / 40% collaborative par défaut).

4. **A/B Testing** : Le moteur inclut un bucketing automatique basé sur le hash de l'user_id. Variant A (α=0.8, content dominant) vs Variant B (α=0.2, collaborative dominant).

5. **Cold Start** : Pour les nouveaux utilisateurs sans historique, seul le score content-based est utilisé.

> **Fichiers clés** : `hybrid_engine.py`, `content_based.py`, `collaborative.py`, `feature_extraction.py`

---

## 8. Computer Vision (Analyse d'Images)

### Idée
Analyser automatiquement les photos des véhicules pour évaluer leur état, flouter les plaques d'immatriculation (RGPD/Loi 09-08), et détecter les modèles.

### Modules implémentés

| Module | Fonctionnement |
|--------|----------------|
| **Damage Detector** | Utilise OpenCV (Canny Edge Detection + analyse de densité des contours). Plus la carrosserie a de "bruit" visuel, plus le score baisse. Retourne un `condition_score` (50-100). |
| **Plate Blur** | Détecte les plaques marocaines (format `XXXXX-X-XX`) par analyse de contours (ratio d'aspect 2.0–6.0) et applique un flou gaussien. |
| **OCR Validator** | Simule un scan Tesseract du certificat de cession pour vérifier la correspondance vendeur/document lors d'un transfert de propriété. |
| **YOLO Detector** | Détection d'objets (modèle, type de carrosserie) via YOLO pour enrichir automatiquement les annonces. |

> **Fichiers clés** : `damage_detector.py`, `plate_blur.py`, `ocr_validator.py`, `yolo_detector.py`

---

## 9. Détection de Fraude (Graphe Neo4j)

### Idée
Identifier les courtiers clandestins qui se font passer pour des particuliers en analysant les relations entre utilisateurs, adresses IP, numéros de téléphone et véhicules publiés.

### Comment ça marche

```
Neo4j Graph:
  (User) ──PUBLIE_ANNONCE──► (Vehicle)
  (User) ──PARTAGE_IP──► (IPAddress) ◄──PARTAGE_IP── (User2)
  (User) ──A_POUR_TELEPHONE──► (PhoneNumber) ◄──A_POUR_TELEPHONE── (User3)
```

1. **Ingestion** : À chaque publication d'annonce, les nœuds `User`, `IPAddress`, `PhoneNumber` et `Vehicle` sont créés/mis à jour dans Neo4j avec leurs relations.

2. **Détection** : Une requête Cypher identifie les clusters d'utilisateurs qui :
   - Partagent la même IP ou le même numéro de téléphone.
   - Publient ≥ 2 annonces sur ≥ 2 marques différentes (comportement de courtier).

3. **Résultat** : Retourne la liste des `suspect_id` pour modération par l'admin.

> **Fichiers clés** : `broker_detector.py`, `graph_service.py`

---

## 10. Détection d'Anomalies (Isolation Forest)

### Idée
Détecter les annonces suspectes (prix anormalement bas/haut, kilométrage truqué) et calculer un **Trust Score** pour chaque vendeur/annonce.

### Comment ça marche
1. **Entraînement** : L'`IsolationForest` (200 estimateurs, contamination 5%) est entraîné sur les features numériques des annonces "normales".
2. **Prédiction** : Chaque nouvelle annonce est passée au modèle. Si elle est détectée comme anomalie (`predict = -1`), elle est flaggée.
3. **Trust Score** : Le `decision_function` (score [-0.5, 0.5]) est normalisé en un score de confiance [0–100] affiché dans l'UI.

> **Fichiers clés** : `anomaly/detector.py`

---

## 11. Analyse de Sentiment (NLP)

### Idée
Analyser automatiquement le ton des avis clients pour calculer un score de satisfaction et enrichir le profil des vendeurs.

### Comment ça marche
1. **Modèle** : `nlptown/bert-base-multilingual-uncased-sentiment` (HuggingFace) — un BERT multilingue fine-tuné pour la classification de sentiment (1-5 étoiles).
2. **Pipeline** : Le texte de l'avis (tronqué à 512 tokens) est passé au modèle. Le label retourné ("1 star" à "5 stars") est converti en score [0–1].
3. **Lazy Loading** : Le modèle n'est chargé en mémoire qu'au premier appel pour ne pas ralentir le démarrage du serveur.

> **Fichiers clés** : `sentiment_analyzer.py`, `routes_reviews.py`

---

## 12. Segmentation des Acheteurs (K-Means)

### Idée
Classer automatiquement les acheteurs en profils types pour personnaliser l'expérience (recommandations, publicités ciblées).

### Segments définis

| Cluster | Label | Profil type |
|---------|-------|-------------|
| 0 | Budget Eco | Petit budget, véhicules économiques |
| 1 | Famille / SUV | Budget moyen, préférence SUV/monospace |
| 2 | Premium / Luxe | Budget élevé, marques premium |
| 3 | Citadin régulier | Usage urbain, citadines compactes |

### Comment ça marche
- **Features** : Budget moyen, fréquence de visite, proportion de SUV consultés.
- **Algorithme** : `KMeans` (scikit-learn, 4 clusters).
- **Persistance** : Modèle sauvegardé en `.joblib` et rechargé au démarrage.

> **Fichiers clés** : `buyer_segments.py`

---

## 13. Simulateur de Dédouanement

### Idée
Permettre aux utilisateurs d'estimer le coût total d'importation d'un véhicule au Maroc, incluant les droits de douane (ADII), la TVA et les taxes additionnelles.

### Comment ça marche

```
Inputs: Prix d'achat, Âge, Carburant, Puissance fiscale, Origine UE/Hors-UE
    │
    ▼
Droits d'importation: 2.5% (UE) ou 17.5% (Hors-UE)
Taxe parafiscale: 0.25%
TVA: 20% × (Base + DI + TP)
Taxe puissance: 5 000 MAD (>10 CV) ou 20 000 MAD (>14 CV)
    │
    ▼
Total = Prix d'achat + Droits + TVA + Taxes
```

L'interface frontend propose un formulaire interactif avec un **breakdown visuel** (barres de couleur) du coût total.

> **Fichiers clés** : `customs_service.py`, `routes_customs.py`, `CustomsPage.tsx`

---

## 14. Système d'Escrow (Séquestre)

### Idée
Sécuriser les transactions entre acheteur et vendeur via un système de séquestre. Les fonds sont bloqués jusqu'à la validation du transfert de propriété.

### Workflow

```
1. Acheteur ──► Initie la transaction (crée un Payment Intent)
2. Fonds bloqués ──► Statut: FUNDS_SECURED
3. Vendeur fournit le certificat de cession
4. OCR Validator ──► Vérifie la correspondance vendeur/document
5. Si OK ──► Fonds débloqués vers le vendeur (COMPLETED)
6. Si KO ──► Fonds remboursés à l'acheteur (REFUNDED)
```

Le `PaymentService` simule un partenaire bancaire (CMI/Stripe Connect) avec des méthodes pour `create_payment_intent`, `simulate_webhook_payment_success`, et `release_funds`.

> **Fichiers clés** : `payment_service.py`, `routes_transactions.py`, `transaction.py`

---

## 15. Health Checker (Disponibilité des Annonces)

### Idée
Vérifier automatiquement que les annonces scrapées sont toujours en ligne. Si une annonce source retourne un 404, le véhicule est marqué comme `sold`.

### Comment ça marche
1. **Boucle asynchrone** : Un `asyncio.create_task()` lance une boucle infinie au démarrage de l'application.
2. **Vérification** : Toutes les 6 heures, tous les véhicules `available` avec une `source_url` sont vérifiés par lots de 5 (requêtes parallèles avec pause de 2s entre les lots).
3. **Marquage** : Si une URL retourne un code HTTP 404, le véhicule passe en statut `sold`.
4. **User-Agent** : Un User-Agent Chrome réaliste est utilisé pour éviter les blocages.

> **Fichiers clés** : `health_checker.py`

---

## 16. Carnet d'Entretien Véhicule

### Idée
Permettre aux propriétaires de gérer l'historique de maintenance de leur véhicule (vidanges, pneus, freinage) et recevoir des rappels prédictifs.

### Modèle de données

| Table | Champs clés |
|-------|-------------|
| `vehicle_services` | `service_type`, `mileage`, `date`, `cost`, `receipt_url`, `notes` |
| `service_reminders` | `trigger_mileage`, `trigger_date`, `car_id` |

### Fonctionnalités
- **Timeline visuelle** : Affichage chronologique de tous les entretiens avec icônes par type.
- **Ajout d'entretien** : Formulaire avec upload de facture (stockée en local `uploads/receipts`).
- **Rappels** : Rappels basés sur le kilométrage ou une date cible.
- **Intégration IA** : Le chatbot peut répondre aux questions d'entretien (`intent: maintenance_check`).

> **Fichiers clés** : `maintenance.py` (model), `maintenance.py` (endpoint), `MaintenanceBook.tsx`, `MaintenanceTimeline.tsx`

---

## 17. Dashboard Unifié (Bento Grid)

### Idée
Un dashboard SaaS premium avec une grille de widgets modulaires (Bento Grid), une sidebar rétractable, et une navigation mobile bottom-bar.

### Layout

```
┌─────────┬───────────────────────────────────────────┐
│         │  Widget 1: Statut IA                      │
│ Sidebar │  "3 annonces correspondent à vos critères"│
│         ├─────────────────┬─────────────────────────┤
│ Accueil │  Widget 2:      │  Widget 3:              │
│ Carnet  │  Argus Rapide   │  Activité Récente       │
│ Annonces│  (estimation    │  (véhicules consultés)  │
│ Favoris │   en 1 clic)    │                         │
│ Argus   ├─────────────────┴─────────────────────────┤
│         │  Widget 4: Admin (si role=admin)           │
│ [Logout]│  Stats rapides + modération                │
└─────────┴───────────────────────────────────────────┘
```

### Sécurité
- **Route Guard** : Si l'utilisateur n'est pas authentifié, il est redirigé vers `/login` sans voir le contenu.
- **Loading State** : Un écran de chargement est affiché pendant la restauration du token JWT (évite le "flash" d'UI protégée).

> **Fichiers clés** : `DashboardLayout.tsx`, `DashboardIndex.tsx`, `DashboardLayout.module.css`

---

## 18. Sécurité de Niveau Production

### Backend

| Mesure | Implémentation |
|--------|----------------|
| Rate Limiting | `slowapi` — 3/15min (auth), 10/min (chat) |
| Security Headers | `X-Frame-Options: DENY`, `HSTS`, `nosniff`, `CSP` |
| Audit Logging | Middleware logguant 401/403 avec IP |
| Input Validation | Pydantic models stricts sur tous les endpoints |
| Key Function | Identification hybride user_id / IP pour le limiteur |

### IA (RAG Guardrails)

| Mesure | Implémentation |
|--------|----------------|
| Sanitization | Suppression caractères de contrôle, limite 500 chars |
| PII Redaction | Regex sur emails et téléphones marocains → `[MASKED]` |
| Prompt Protection | Directive anti-injection dans le system prompt |
| Status Filter | Qdrant filtre sur `status = 'available'` uniquement |

### Frontend

| Mesure | Implémentation |
|--------|----------------|
| CSP | `<meta http-equiv="Content-Security-Policy">` strict |
| Route Guard | `<Navigate to="/login">` si token absent |
| Secrets Check | Script `npm run check-env` post-build |

### Audit Automatisé
- Script `security_audit.ps1` qui exécute `pip-audit`, `npm audit` et détection de secrets dans le build compilé.

> **Fichiers clés** : `security.py`, `main.py`, `index.html`, `security_audit.ps1`

---

## 19. Détails Techniques & Mathématiques des Algorithmes

### XGBoost (Prédiction de Prix)
**Pourquoi XGBoost ?** C'est un algorithme basé sur les arbres de décision (Gradient Boosting) extrêmement performant pour les données tabulaires avec des relations non linéaires (ex: la décote d'une voiture n'est pas linéaire avec l'âge).
- **Objectif mathématique** : Minimiser l'erreur quadratique moyenne (MSE) entre le prix prédit et le prix réel.
- **Feature Engineering Clé** : La création de la variable `annual_mileage` (kilométrage / âge) aide le modèle à distinguer un véhicule très roulé (taxi/VTC) d'un véhicule à usage occasionnel, ce qui impacte fortement le prix sur le marché marocain.

### K-Means (Segmentation)
- **Fonctionnement** : L'algorithme regroupe les utilisateurs en *K* clusters en minimisant la variance intra-cluster (la distance entre chaque point et le centre de son cluster, ou centroïde).
- **Features normalisées** : Les données (budget, fréquence) doivent être normalisées (StandardScaler) avant K-Means, car l'algorithme est sensible aux échelles (un budget en milliers de MAD dominerait la fréquence de visite qui est de l'ordre des dizaines).

### Filtrage Collaboratif (Recommandation)
- **Similarité Cosinus** : Utilisée pour trouver des utilisateurs au comportement similaire. Si l'utilisateur A et B consultent les mêmes véhicules, le cosinus de l'angle entre leurs vecteurs d'interaction se rapproche de 1.
- **Cold Start Problem** : C'est pourquoi le moteur hybride (`hybrid_engine.py`) est crucial. Un nouvel utilisateur n'a pas d'interactions (vecteur vide = score collaboratif de 0). Le système bascule alors automatiquement sur un score purement *Content-Based* (basé sur le budget et la carrosserie choisis à l'inscription).

---

## 20. Stratégies de Déploiement & Scaling

- **Bases de données séparées** : En production, séparez PostgreSQL (données relationnelles transactionnelles), Qdrant (recherche ultra-rapide en RAM) et Neo4j (requêtes de graphe complexes).
- **Workers Asynchrones** : Les tâches lourdes (entraînement ML, scraping de masse, redimensionnement d'images, synchronisation Qdrant) devraient être gérées par des workers (ex: **Celery** + **RabbitMQ** ou **Redis**) pour ne pas bloquer l'API FastAPI.
- **Mise en cache** : Utilisez Redis pour cacher les résultats de prédiction de prix pour des combinaisons (Marque, Modèle, Année) très fréquentes, et pour cacher les requêtes LLM récurrentes.

---

## Stack Technologique Complète

| Catégorie | Technologies |
|-----------|-------------|
| **Frontend** | React 18, TypeScript, Vite, Framer Motion, Lucide Icons, React Query |
| **Backend** | FastAPI, SQLAlchemy (async), Pydantic v2, slowapi |
| **Bases de Données** | PostgreSQL (pgvector), Qdrant (vectoriel), Neo4j (graphe) |
| **IA / LLM** | OpenAI GPT-4o-mini, text-embedding-3-small, LangChain |
| **Machine Learning** | XGBoost, scikit-learn (Isolation Forest, K-Means), HuggingFace Transformers |
| **Computer Vision** | OpenCV, YOLO |
| **Scraping** | BeautifulSoup, cloudscraper |
| **DevOps** | Docker, pip-audit, npm audit |

---

*Document généré le 16 Juillet 2026 — Projet Wakala v0.1.0*
