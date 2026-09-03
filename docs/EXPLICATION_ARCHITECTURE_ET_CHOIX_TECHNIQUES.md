# 📘 Wakala — Guide Complet de l'Architecture, des Choix Techniques et de la Reproduction

> **Document de Référence Technique & Fonctionnelle**  
> Ce document détaille les justifications approfondies (*pourquoi*) des choix technologiques et des fonctions métier de la plateforme **Wakala**, ainsi que la méthode pas-à-pas pour recréer l'architecture logicielle et son schéma visuel Excalidraw.

---

## 📑 Table des Matières

1. [Vision & Principe Directeur de Wakala](#1-vision--principe-directeur-de-wakala)
2. [Justification Approfondie des Choix Technologiques (*Le POURQUOI des Technologies*)](#2-justification-approfondie-des-choix-technologiques)
   - 2.1. Frontend & Visualisation 3D
   - 2.2. Backend & Moteur d'Exécution
   - 2.3. Stockage Polyglotte (PostgreSQL, Qdrant, Neo4j)
   - 2.4. Data Pipeline & Ingestion (Kafka, Spark, Airflow)
3. [Justification des Fonctions & Mécanismes Métier (*Le POURQUOI des Fonctions*)](#3-justification-des-fonctions--mécanismes-métier)
   - 3.1. L'Assistant Consultatif 2 Phases (RAG)
   - 3.2. Le Moteur Déterministe sur 8 Dimensions
   - 3.3. Pondération par Personas & Sélecteur Top 3 Certifié
   - 3.4. Le Garde-Fou Anti-Hallucination (*Compliance Guard*)
   - 3.5. Registre de Consentement CNDP (Loi 09-08)
   - 3.6. Cycle d'Outreach 0–60 Jours & Conditions d'Arrêt
4. [Guide Pas-à-Pas pour Recréer l'Architecture & le Schéma Excalidraw](#4-guide-pas-à-pas-pour-recréer-larchitecture--le-schéma-excalidraw)
   - Étape 1 : Initialisation de l'Infrastructure Docker
   - Étape 2 : Déploiement des Schémas de Base de Données
   - Étape 3 : Implémentation du Cœur ML & RAG
   - Étape 4 : Déploiement du Pipeline de Scraping & DAGs Airflow
   - Étape 5 : Lancement et Validation des Tests (154 tests)
   - Étape 6 : Génération Programmatique du Schéma Excalidraw

---

## 1. Vision & Principe Directeur de Wakala

Wakala est une plateforme d'aide à la décision et d'achat automobile pour le marché marocain.

### 🏛️ Le Principe Directeur Invariant
> **« Le LLM comprend, qualifie et argumente ; le moteur déterministe calcule, certifie et filtre. »**

- **Le LLM ne calcule JAMAIS un score**, ne trie jamais des véhicules et n'invente jamais un prix ou une remise.
- **Le moteur déterministe calcule les scores sur des formules mathématiques claires**, applique les filtres durs et interroge la base PostgreSQL.
- **Le LLM reçoit la sélection déjà ordonnée et certifiée** pour la restituer sous une forme empathique, fluide et adaptée à la culture locale (Français, Darija, Arabe).

---

## 2. Justification Approfondie des Choix Technologiques

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        APPLICATIONS CLIENTES                             │
│       React 18 + Vite + TypeScript (Web)  •  React Native Expo (Mobile)  │
│                      Configurateur 3D Paramétrique                       │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ REST JSON (Axios)
┌────────────────────────────────────▼─────────────────────────────────────┐
│                       BACKEND API & TRANSACTIONNEL                       │
│                     FastAPI (Python 3.11+ AsyncIO)                       │
│                 SQLAlchemy Async ORM • Pydantic v2 Val.                  │
├────────────────────┬────────────────────┬────────────────────────────────┤
│    PostgreSQL 16   │    Qdrant Vector   │         Neo4j Graph GDS        │
│  (ACID & Vérité)   │ (Recherche Sémant) │     (Détection de Fraude)      │
└────────────────────┴────────────────────┴────────────────────────────────┘
```

### 2.1. Frontend & Visualisation 3D

| Technologie | Rôle | Pourquoi ce choix ? |
| :--- | :--- | :--- |
| **React 18 + Vite** | SPA Web | Temps de chargement quasi-instantané (HMR ultra-rapide), gestion fluide du state applicatif complexe (filtres, chat en direct, comparateur). |
| **TypeScript** | Typage statique | Élimine les erreurs d'interface entre les modèles Pydantic du backend et les composants d'affichage frontend. |
| **Three.js + glTF 2.0 Paramétrique** | Studio 3D Véhicule | Plutôt que de dépendre de modèles 3D tiers très lourds (>50 Mo) ou propriétaires, Wakala génère programmatiquement son modèle glTF (`generate_dacia_sandero_stepway_3d.py`). Cela permet d'ajuster les matériaux PBR (peinture métallisée, vitres fumées, jantes diamantées) en temps réel avec un poids plume (<1 Mo). |
| **React Native Expo** | Application Mobile | Permet de cibler iOS et Android avec une seule base de code TypeScript, en partageant les schémas d'API et la logique métier. |

### 2.2. Backend & Moteur d'Exécution

| Technologie | Rôle | Pourquoi ce choix ? |
| :--- | :--- | :--- |
| **FastAPI (Python AsyncIO)** | Passerelle API REST | FastAPI offre des performances proches de Go/Node.js grâce à `uvicorn`/`starlette`. Le support natif de l'asynchronisme (`async`/`await`) est indispensable pour gérer simultanément les appels LLM cloud, les requêtes vectorielles Qdrant et les requêtes relationnelles PostgreSQL. |
| **Pydantic v2** | Validation & Contrats de données | Sérialisation et validation strictes à l'entrée et à la sortie de chaque endpoint. Empêche toute injection de types invalides dans le pipeline de scoring. |
| **SQLAlchemy 2.0 Async** | ORM Relationnel | Sessions asynchrones non bloquantes, gestion fine des transactions pour les réservations, transactions de séquestre et logs d'audit. |

### 2.3. Stockage Polyglotte

Le principe du stockage polyglotte consiste à utiliser la base la plus performante pour chaque type de structure de données :

1. **PostgreSQL 16 (Relationnel & Transactionnel)** :
   - *Pourquoi* : Source unique de vérité (SSOT). Garantit les propriétés ACID indispensables pour les transactions, les utilisateurs, l'inventaire certifié et le registre de consentement CNDP.
2. **Qdrant (Base de Données Vectorielle)** :
   - *Pourquoi* : Recherche sémantique haute performance. Les fiches techniques et avis sont vectorisés (embeddings). Quand un utilisateur dit *"voiture haute pour chemins de campagne"*, Qdrant fait matcher le concept sémantique avec la garde au sol et la motricité.
3. **Neo4j 5.23 (Base de Données Graphe)** :
   - *Pourquoi* : Détection de fraude et de courtiers clandestins (*samsars*). La structure en graphe permet de repérer en 1 requête Cypher les numéros de téléphone et adresses IP partagés entre des dizaines d'annonces de vendeurs prétendument "particuliers".

### 2.4. Data Pipeline & Ingestion

1. **Scraping Hybride (JSON-LD prioritaire + Fallback LLM)** :
   - *Pourquoi* : Les sites d'annonces changent fréquemment de structure HTML. En extrayant d'abord les balises `<script type="application/ld+json">`, on obtient des données propres et standardisées à 0 coût IA. Le LLM n'intervient qu'en second recours sur le texte brut.
2. **Kafka (KRaft) & Spark (Streaming & Batch)** :
   - *Pourquoi* : Découple les robots de scraping du traitement lourd en base. Permet de nettoyer (*Silver*) et d'agréger (*Gold*) les données d'annonces de manière idempotente sans verrouiller PostgreSQL.
3. **Apache Airflow** :
   - *Pourquoi* : Planification fiable et observable des DAGs quotidiens (ingestion, vérification de conformité, alerte de baisse de prix J+45, audit des données orphelines).

---

## 3. Justification des Fonctions & Mécanismes Métier

### 3.1. L'Assistant Consultatif 2 Phases (RAG)
*Fichiers clés : `consultative_flow.py`, `needs_profile_schema.py`, `chatbot_chain.py`*

- **Pourquoi deux phases distinctes ?**
  Dans le commerce automobile marocain, proposer un véhicule dès le premier message génère de la méfiance et un fort taux de rebond.
  - **Phase 1 (DÉCOUVERTE)** : Le chatbot écoute, pose **1 à 2 questions maximum** pour combler les manques essentiels (**Budget max** et **Usage principal**). Il refuse d'évoquer des modèles précis.
  - **Phase 2 (RESTITUTION)** : Déclenchée **uniquement** quand le profil est complet. Le LLM prend la sortie certifiée du moteur et en explique les bénéfices.
- **Pourquoi le support Darija / Arabizi ?**
  Une grande partie des acheteurs au Maroc s'expriment en Darija écrite en caractères latins (Arabizi : *3andi*, *ghir*, *dyal*) ou arabes. Les expressions de budget (*"20 melyoun"*, *"250k"*) sont normalisées par des regex dédiées.

---

### 3.2. Le Moteur Déterministe sur 8 Dimensions
*Fichier clé : `eight_dimension_scorer.py`*

Pour évaluer un véhicule avec une neutralité mathématique parfaite, Wakala utilise **8 dimensions universelles normées de 1.0 à 5.0** :

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LES 8 DIMENSIONS DU SCORING WAKALA                   │
├───────────────────┬─────────────────────────────────────────────────────┤
│ 1. Espace         │ Coffre (L), 5 ou 7 places, modularité habitacle     │
│ 2. Sécurité       │ Étoiles Euro NCAP, ADAS, année de conception        │
│ 3. Coût Réel (TCO)│ Consommation (L/100km), carburant (Élec/Hybride/D.) │
│ 4. Prix d'Accès   │ Positionnement tarifaire brut par rapport au marché │
│ 5. Praticité Urb. │ Longueur hors-tout (<4m = 5/5), rayon de braquage   │
│ 6. Performance    │ Puissance fiscale & dynamique (ch DIN, couple Nm)   │
│ 7. Écologie       │ Émissions CO2 (g/km), malus écologique              │
│ 8. Motricité      │ Transmission intégrale (4x4), garde au sol SUV      │
└───────────────────┴─────────────────────────────────────────────────────┘
```

- **Pourquoi 8 dimensions ?**
  Elles couvrent l'intégralité du compromis d'achat automobile sans angle mort. Un véhicule n'est jamais "parfait" : il arbitre entre coût, espace, gabarit et performance.
- **Pourquoi déterministe ?**
  Si le calcul était confié au LLM, deux requêtes identiques donneraient des notes différentes (stochasticité du LLM). L'algorithme mathématique assure une reproductibilité et une équité totales.

---

### 3.3. Pondération par Personas & Sélecteur Top 3 Certifié
*Fichiers clés : `dynamic_weighting.py`, `top3_selector.py`*

- **Pondération Personas** : Un père de famille donne 35% de poids à l'Espace et 25% à la Sécurité. Un jeune urbain donne 35% à la Praticité et 30% au Coût réel.
- **Boost de Priorités (+15%)** : Si l'acheteur coche explicitement "Écologie", le poids de cette dimension est majoré de +15%.
- **Cascade de Relâchement Ordonnée** : Si les filtres stricts renvoient moins de 3 véhicules, le moteur relâche progressivement :
  1. La marque préférée
  2. Le type de carrosserie
  3. Le carburant
  4. En dernier recours, le budget (tolérance max +15%).
- **Règle de Diversité des Marques** : Le Top 3 ne peut pas contenir 3 fois la même marque (max 2 véhicules d'un même constructeur pour garantir un choix réel).
- **Compromis Explicites** : Toute note < 3/5 est automatiquement extraite et affichée comme point de vigilance (ex: *"⚠ Performance modeste pour autoroute"*).

---

### 3.4. Le Garde-Fou Anti-Hallucination (*Compliance Guard*)
*Fichier clé : `compliance_guard.py`*

- **Pourquoi est-il indispensable ?**
  Les modèles de langage peuvent inventer des finitions, des prix ou des véhicules vendus.
- **Comment fonctionne-t-il ?**
  Avant que la liste des véhicules recommandés ne parvienne au prompt du chatbot, le `ComplianceGuard` exécute une requête SQL directe :
  `SELECT id FROM vehicles WHERE id IN (...) AND status = 'available' AND price IS NOT NULL;`
  Tout identifiant non certifié est éliminé de manière silencieuse et hermétique.

---

### 3.5. Registre de Consentement CNDP (Loi 09-08)
*Fichiers clés : `routes_consent.py`, `models/outreach.py`, `019_create_consent_table.sql`*

- **Pourquoi la conformité CNDP ?**
  La législation marocaine (Loi 09-08 de la Commission Nationale de contrôle de la protection des Données à caractère Personnel) interdit toute prospection sans consentement préalable explicite.
- **Mécanisme réel** :
  - Inscription horodatée du consentement (`POST /api/consent`) avec canal autorisé (`whatsapp`, `email`, `sms`).
  - Droit au retrait immédiat (`DELETE /api/consent/{prospect_id}`) qui remplit `opt_out_at`.
  - **Vérification systématique avant chaque envoi** dans `verify_consent()`.

---

### 3.6. Cycle d'Outreach 0–60 Jours & Conditions d'Arrêt
*Fichiers clés : `sequence_definitions.py`, `message_templates.py`, `stop_conditions.py`, `outreach_scheduler.py`*

Au Maroc, le cycle de décision pour un véhicule neuf s'étend sur 45 à 60 jours. Wakala accompagne ce cycle sans harcèlement commercial :

| Jalon | Délai | Canal | Objectif & Règle Stricte |
| :---: | :---: | :---: | :--- |
| **J0** | Immédiat | Email | Récapitulatif du Top 3 certifié avec forces et compromis. |
| **J2-3** | 2 jours | WhatsApp | Fiche technique détaillée et lien configurateur 3D. |
| **J7** | 7 jours | Email | Matrice comparative du Coût Total de Possession (TCO 5 ans). |
| **J14** | 14 jours | WhatsApp | Proposition sans engagement d'un essai en concessionnaire partenaire. |
| **J45** | 45 jours | Email | **Alerte Baisse de Prix** : envoyée **UNIQUEMENT** si une baisse réelle ≥ 1000 MAD est constatée en base. Si aucun prix n'a baissé, le jalon est **sauté**. |
| **J60** | 60 jours | Email | Clôture bienveillante et arrêt définitif de la séquence automatique. |

- **Les 3 Conditions d'Arrêt Immédiat** :
  1. Achat confirmé en base (`transactions`)
  2. Essai routier réservé (`test_drive_bookings`)
  3. Consentement révoqué (Opt-out `prospect_consents`)

---

## 4. Guide Pas-à-Pas pour Recréer l'Architecture & le Schéma Excalidraw

### Étape 1 : Initialisation de l'Infrastructure Docker

Lancez les conteneurs requis pour le stockage et l'ingestion :

```bash
cd "d:/Projet automobile/vente-auto-platform"
docker compose up -d postgres neo4j qdrant kafka
```

### Étape 2 : Déploiement des Migrations SQL

Appliquez les migrations PostgreSQL dans l'ordre numérique (dont la 019 pour le consentement et la 020 pour l'outreach) :

```bash
# Les scripts sont exécutés automatiquement au démarrage du conteneur postgres
# Ou manuellement via psql :
docker exec -i wakala-postgres psql -U wakala_user -d wakala < database/postgres/migrations/019_create_consent_table.sql
docker exec -i wakala-postgres psql -U wakala_user -d wakala < database/postgres/migrations/020_create_outreach_sequences.sql
```

### Étape 3 : Configuration de l'Environnement Backend Python

Activez l'environnement virtuel et installez les dépendances :

```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
```

### Étape 4 : Lancement et Validation des 154 Tests Automatisés

Vérifiez l'intégrité complète de la chaîne (RAG, Scoring 8D, Top 3, Compliance, Outreach) :

```bash
python -m pytest tests/unit/ tests/compliance/ tests/integration/ -v
```

*Résultat attendu : `154 passed in 1.65s`.*

### Étape 5 : Démarrage des Services Applicatifs

1. **Backend FastAPI** :
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend React** :
   ```bash
   cd ../frontend
   npm install
   npm run dev -- --port 3000
   ```

### Étape 6 : Génération Automatique du Schéma d'Architecture Excalidraw

Pour régénérer à tout moment le schéma visuel `.excalidraw` synchronisé avec le code :

```bash
cd "d:/Projet automobile/vente-auto-platform"
python scripts/generate_real_architecture_excalidraw.py
```

Le script produit instantanément les deux livrables :
- `docs/architecture_reelle_wakala.excalidraw`
- `Livrables/Wakala_Architecture_Reelle.excalidraw`

---

## 5. Synthèse des Livrables Produits

| Livrable | Type | Emplacement |
| :--- | :--- | :--- |
| **Schéma Excalidraw** | JSON Excalidraw v2 | [`docs/architecture_reelle_wakala.excalidraw`](file:///d:/Projet%20automobile/vente-auto-platform/docs/architecture_reelle_wakala.excalidraw) |
| **Schéma Excalidraw (Copie Livrables)** | JSON Excalidraw v2 | [`Livrables/Wakala_Architecture_Reelle.excalidraw`](file:///d:/Projet%20automobile/vente-auto-platform/Livrables/Wakala_Architecture_Reelle.excalidraw) |
| **Script Générateur Excalidraw** | Python | [`scripts/generate_real_architecture_excalidraw.py`](file:///d:/Projet%20automobile/vente-auto-platform/scripts/generate_real_architecture_excalidraw.py) |
| **Document Explicatif Complet** | Markdown | [`docs/EXPLICATION_ARCHITECTURE_ET_CHOIX_TECHNIQUES.md`](file:///d:/Projet%20automobile/vente-auto-platform/docs/EXPLICATION_ARCHITECTURE_ET_CHOIX_TECHNIQUES.md) |
| **Suite de 154 Tests de Conformité** | Pytest | `backend/tests/compliance/` & `backend/tests/unit/` |
