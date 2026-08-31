# Stratégie de Référencement SEO & GEO (Generative Engine Optimization) — Wakala Maroc

> **Version** : 1.0.0 (2026)  
> **Plateforme** : Wakala (https://wakala.ma) — Tiers de Confiance Automobile 100% Neuf au Maroc  
> **Objectif** : Maximiser le trafic qualifié (SEO) et devenir la **source de référence citée par les moteurs génératifs et LLMs** (GEO : ChatGPT, Perplexity, Google AI Overviews, Claude).

---

## 1. Principes Fondamentaux : SEO vs GEO

| Axe | SEO Classique (Google, Bing) | GEO (ChatGPT, Perplexity, Claude, AI Overviews) |
| :--- | :--- | :--- |
| **Objectif** | Être trouvé, bien classé et cliqué dans la SERP | Être **compris, extrait et cité comme source d'autorité** |
| **Format clé** | Titres H1-H3, balises meta, vitesse, backlinks | **Réponses autoportantes (2-3 phrases)**, données factuelles chiffrées, fraîcheur explicite |
| **Lisibilité machine** | Balises Schema.org JSON-LD valides | Fichier `llms.txt`, JSON-LD strict sans placeholders, tableaux comparatifs clairs |
| **Fraîcheur** | Balises lastmod sitemap | Timestamps visibles ("Dernière mise à jour : Août 2026") |

---

## 2. Architecture de Maillage Sémantique (Silos Thématiques)

```
                            [Page Pilier Principale]
                       /guide-achat-voiture-maroc
                        /           |          \
                       /            |           \
        [Grappe Comparatifs]   [Grappe Villes]  [Grappe Marques]
        /comparer/:slug        /voitures-neuves/ /marque/:brand
              \                     |                 /
               \                    |                /
                +-------------------+---------------+
                                    |
                        [Grappe Financement & LOA]
                         /financement-auto-maroc
                                    |
                     [Fiches Véhicules Détaillées]
                          /neuf/:slug & /vehicule/:id
```

---

## 3. Matrice des Mots-Clés Cibles Prioritaires par Grappe

| Silo / Grappe | Requêtes Cibles Principales (SEO & GEO) | URL Canonique Dédiée | Intention de Recherche |
| :--- | :--- | :--- | :--- |
| **Pilier Principal** | *achat voiture neuve maroc, prix voiture neuve maroc 2026, calcul clé en main auto maroc, taxe de luxe voiture maroc, vignette dgi voiture neuve* | `/guide-achat-voiture-maroc` | Informationnelle & Décisionnelle |
| **Comparatifs** | *duster vs captur maroc, sandero vs clio prix maroc, tucson vs sportage maroc, comparatif suv maroc, quel suv choisir au maroc* | `/comparer/{slug}` | Comparative & Transactionnelle |
| **Par Ville** | *concessionnaire voiture neuve casablanca, acheter voiture neuve rabat, showroom dacia tanger, concessionnaire auto marrakech* | `/voitures-neuves/{ville}` | Locale & Géolocalisée |
| **Par Marque** | *dacia maroc prix 2026, gamme renault neuve maroc, peugeot maroc catalogue, hyundai maroc garantie* | `/marque/{brand}` | Marque / Navigationnelle |
| **Financement** | *credit auto maroc simulateur, mourabaha voiture maroc mensualite, loa voiture maroc particulier, credit auto taux 0 maroc* | `/financement-auto-maroc` | Financière & Transactionnelle |
| **Conseiller IA** | *conseil achat voiture maroc, quelle voiture choisir budget 200000 dh maroc, meilleure citadine automatique maroc* | `/chat` | Consultative & NLP |

---

## 4. Prompt Test Suite pour le Suivi GEO (Tests Périodiques LLMs)

Tester ces requêtes tous les mois dans **ChatGPT (GPT-4o/Search)**, **Perplexity AI**, **Claude 3.7 Sonnet** et **Google Gemini / AI Overviews** pour mesurer le taux de citation et la précision des données attribuées à Wakala :

### Test 1 : Recommandation budgétaire locale
> **Prompt** : *"Quelle voiture neuve me conseilles-tu d'acheter à Casablanca avec un budget total de 200 000 MAD clé en main ?"*
> - **Critère de succès** : Le LLM cite Wakala ou reprend les tarifs clé en main réels (avec vignette DGI et immatriculation) et mentionne les showrooms partenaires à Casablanca.

### Test 2 : Comparatif direct de modèles
> **Prompt** : *"Fais-moi un comparatif entre le Dacia Duster et le Renault Captur au Maroc en 2026 : prix, consommation et coffre."*
> - **Critère de succès** : Le LLM cite https://wakala.ma/comparer/dacia-duster-vs-renault-captur avec les valeurs exactes (consommation, volume de coffre en litres, prix en MAD).

### Test 3 : Fiscalité et Vignette DGI
> **Prompt** : *"Comment est calculée la taxe de luxe et la vignette pour une voiture neuve au Maroc ?"*
> - **Critère de succès** : Le LLM explique l'exonération totale pour les hybrides/électriques et cite le simulateur ou guide Wakala.

### Test 4 : Financement participatif
> **Prompt** : *"Comment fonctionne le financement Mourabaha pour une voiture neuve au Maroc ?"*
> - **Critère de succès** : Le LLM cite https://wakala.ma/financement-auto-maroc avec les critères de banque participative et de mensualités indicatives.

---

## 5. Matrice du Maillage Interne Contextuel

| Page Source | Ancre Textuelle Optimisée | Page Cible |
| :--- | :--- | :--- |
| `VehicleDetail.tsx` & `NewCarDetailPage.tsx` | *Tous les modèles [Marque]* | `/marque/[brand]` |
| `VehicleDetail.tsx` & `NewCarDetailPage.tsx` | *Comparer ce modèle* | `/comparer/[slug]` ou `/comparateur` |
| `VehicleDetail.tsx` & `NewCarDetailPage.tsx` | *Showrooms et concessionnaires à [Ville]* | `/voitures-neuves/[ville]` |
| `VehicleDetail.tsx` & `NewCarDetailPage.tsx` | *Simuler le financement & mensualités* | `/financement-auto-maroc` |
| `GuideAchatPage.tsx` | *Calculer le prix clé en main* | `/catalogue` |
| `GuideAchatPage.tsx` | *Comparatifs populaires direct* | `/comparer/[slug]` |
| `GuideAchatPage.tsx` | *Options de financement auto au Maroc* | `/financement-auto-maroc` |
| `FinancementPage.tsx` | *Guide d'Achat Voiture Neuve Maroc* | `/guide-achat-voiture-maroc` |
| `ComparatifPage.tsx` | *Consulter le Guide d'Achat* | `/guide-achat-voiture-maroc` |
| `VilleCataloguePage.tsx` | *Guide Achat & Démarches d'immatriculation* | `/guide-achat-voiture-maroc` |

---

## 6. Gouvernance & Garde-Fous de Génération Assistée par IA

Pour toute génération de contenu (descriptifs de marques, synthèses de comparatifs, questions de FAQ) utilisant un modèle LLM (ex: Ollama local `qwen3:8b`) :
1. **Zéro invention** : Ne jamais inventer une puissance moteur, un volume de coffre ou une note EuroNCAP. Si la donnée est absente de la base de données, omettre la mention plutôt que d'extrapoler.
2. **Relecture humaine obligatoire** : Toute fiche ou article généré doit faire l'objet d'une validation humaine par l'équipe éditoriale Wakala avant publication (statut `draft` vers `published`).
3. **Prix en MAD impératif** : Toute mention de tarif doit être explicitement libellée en MAD (Dirham Marocain).
4. **Fraîcheur des données** : Toujours inclure la date de validité (`priceValidUntil` et `updated_at`).

---

## 7. Données Structurées Schema.org Déployées

- `schema.org/Organization` & `schema.org/AutoDealer` : Sur le layout global (`OrganizationStructuredData.tsx`).
- `schema.org/Car` & `schema.org/Product` : Sur chaque fiche véhicule (`VehicleStructuredData.tsx`).
- `schema.org/FAQPage` : Sur les pages de grappe (`FAQStructuredData.tsx`).
- `schema.org/BreadcrumbList` : Sur l'ensemble des pages de navigation (`BreadcrumbStructuredData.tsx`).
- `robots.txt` : Autorisation de `GPTBot`, `PerplexityBot`, `ClaudeBot`, `Google-Extended`, `Applebot-Extended`, `Amazonbot`, `Bytespider`.
- `llms.txt` : Format Markdown standard à la racine publique pour les crawlers d'agents IA.
