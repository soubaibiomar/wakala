# Problèmes et Chantiers Restants : Recommandation & Chatbot

Ce document recense de manière exhaustive les anomalies, limitations techniques et chantiers d'amélioration qui **ne sont pas encore traités** sur le moteur de recommandation et le chatbot de la plateforme Wakala.

---

## Synthèse des Priorités

| ID | Domaine | Problème / Limitation | Gravité | Statut |
| :--- | :--- | :--- | :---: | :---: |
| **#01** | Architecture Chat | Dualité non synchronisée entre `ChatbotWidget` et `RecommendationExperience` | 🔴 Élevée | ✅ Résolu (masquage collision + handoff d'intention `wakala_pending_intent`) |
| **#02** | Fournisseur LLM | Instabilité et coupures des modèles gratuits OpenRouter | 🔴 Élevée | ✅ Résolu (timeout 6s + cascade Groq Llama 3.3 + repli textuel) |
| **#03** | Backend IA | Dépendance stricte à Qdrant sans fallback dégradé automatique | 🔴 Élevée | ✅ Résolu (fallback direct PostgreSQL ILIKE / filtres réels) |
| **#04** | Tests Backend | Échec de collection des tests de recommandation Python (`sklearn`, `xgboost`) | 🔴 Élevée | ✅ Résolu (19/19 tests pytest validés) |
| **#05** | Accessibilité / Voice | Reconnaissance vocale inaccessible sur Firefox et Safari mobile | 🟠 Moyenne | ✅ Résolu (détection et statut audio) |
| **#06** | UX / Session | Perte de l'historique et de l'état du questionnaire au rafraîchissement (F5) | 🟠 Moyenne | ✅ Résolu (sessionStorage restauré) |
| **#07** | Logique Métier | Gestion des requêtes contradictoires (zéro match sans contre-proposition) | 🟠 Moyenne | ✅ Résolu (dialogue d'arbitrage 4 langues) |
| **#08** | UI Catalogue | Désynchronisation visuelle entre filtres latéraux et sélection du chatbot | 🟡 Modérée | ✅ Résolu (event wakala:recommendation-results) |
| **#09** | NLU / Langues | Compréhension imparfaite du Darija automobile spécifique par le LLM backend | 🟡 Modérée | ✅ Résolu (glossaire marocain intégré au prompt) |
| **#10** | Rendu Scores 8D | Absence de fallback explicite quand le microservice de scoring 8D échoue | 🟡 Modérée | ✅ Résolu (calculateur heuristique local 8D) |
| **#11** | Logique Métier / NLU | Profil métier spécial Taxi (Moul Taxi) : questionnaire inadapté et marques de luxe | 🔴 Élevée | ✅ Résolu (qualification Petit/Grand taxi, slider borné 90k-250k, exclusion stricte luxe, Vitest 143/143) |

---

## 1. Architecture & Expérience Conversationnelle

### #01 — Dualité non synchronisée entre `ChatbotWidget` et `RecommendationExperience`
* **Fichiers concernés** :
  * [`frontend/src/components/chatbot-widget/ChatbotWidget.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/chatbot-widget/ChatbotWidget.tsx)
  * [`frontend/src/components/recommendation-experience/RecommendationExperience.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/RecommendationExperience.tsx)
  * [`frontend/src/components/chatbot-widget/useChatSession.ts`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/chatbot-widget/useChatSession.ts)
* **Description** :
  Il existe actuellement deux composants de chat distincts : la bulle flottante présente sur les pages d'accueil et de présentation (`ChatbotWidget`), et l'interface de recommandation intégrée au catalogue (`RecommendationExperience`). Chacun gère son propre état de conversation (`messages`) de façon indépendante.
* **Impact Utilisateur** :
  Si un utilisateur commence à formuler son besoin sur la page d'accueil puis clique sur une suggestion menant au catalogue, son échange précédent n'est pas transmis : la discussion recommence à zéro dans le catalogue.
* **Solution Recommandée** :
  Unifier la gestion d'état dans un store global partagé (Zustand ou React Context) pour conserver le fil de discussion et la progression du questionnaire entre toutes les pages.

---

### #06 — Perte d'état au rafraîchissement de la page (F5)
* **Fichiers concernés** :
  * [`frontend/src/components/recommendation-experience/RecommendationExperience.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/RecommendationExperience.tsx)
* **Description** :
  L'historique des réponses, la langue active et les véhicules candidats sont stockés dans des `useState` en mémoire vive du navigateur.
* **Impact Utilisateur** :
  Un rechargement accidentel de page ou une perte momentanée de connexion réinitialise entièrement le questionnaire (budget, usage, valises), forçant l'utilisateur à tout recommencer.
* **Solution Recommandée** :
  Mettre en place une persistance dans `sessionStorage` ou `localStorage` pour restaurer automatiquement l'état actif lors du rechargement.

---

## 2. Robustesse du Backend, LLM & Microservices

### #02 — Instabilité des modèles gratuits OpenRouter
* **Fichiers concernés** :
  * [`backend/app/core/config.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/core/config.py)
  * [`backend/app/services/ai/chat.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/services/ai/chat.py)
  * [`backend/app/rag/chatbot_chain.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/rag/chatbot_chain.py)
* **Description** :
  La configuration par défaut cible des modèles OpenRouter gratuits (`liquid/lfm-2.5-2.6b:free`, `minimax/minimax-m3:free`, `openrouter/free`). Ces endpoints subissent régulièrement des coupures inopinées, des files d'attente saturées et des blocages HTTP 429 (*Too Many Requests*).
* **Impact Utilisateur** :
  Le chatbot met plus de 10 secondes à répondre, génère des réponses incomplètes ou affiche un message d'erreur générique.
* **Solution Recommandée** :
  Mettre en place un système de basculement automatique (*multi-provider fallback*) : OpenRouter Pro / Groq (Llama 3.3 70B) / Mistral / OpenAI avec disjoncteur (*circuit breaker*) en cas d'indisponibilité.

---

### #03 — Dépendance stricte à Qdrant & Neo4j sans dégradation gracieuse
* **Fichiers concernés** :
  * [`backend/app/core/qdrant_client.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/core/qdrant_client.py)
  * [`backend/app/core/neo4j_client.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/core/neo4j_client.py)
  * [`backend/app/rag/consultative_flow.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/rag/consultative_flow.py)
* **Description** :
  Le flux de recherche sémantique dépend directement de Qdrant (pour les vecteurs de véhicules) et Neo4j (pour les relations de compatibilité). Si les conteneurs correspondants ne sont pas joignables ou que les variables d'environnement sont vides, les requêtes backend peuvent lever des exceptions non interceptées (500 Internal Server Error).
* **Impact Utilisateur** :
  Blocage de la recherche sémantique en environnement de test ou lors d'un incident réseau sur les microservices.
* **Solution Recommandée** :
  Intégrer un intercepteur avec repli systématique sur la recherche textuelle PostgreSQL (`pg_trgm` ou `to_tsvector`) dès que Qdrant ou Neo4j ne répond pas sous 500 ms.

---

### #04 — Échecs des tests unitaires backend du module de recommandation
* **Fichiers concernés** :
  * `backend/tests/test_recommendation.py`
  * `backend/tests/unit/test_matching_engine.py`
  * `backend/tests/unit/test_price_model.py`
  * `backend/tests/unit/test_price_prediction.py`
  * `backend/tests/unit/test_recommendation_hybrid.py`
  * `backend/tests/test_wakala_core.py`
* **Description** :
  L'exécution de `pytest` remonte 12 erreurs de collection :
  1. `ModuleNotFoundError: No module named 'sklearn'`
  2. `ModuleNotFoundError: No module named 'xgboost'`
  3. `ModuleNotFoundError: No module named 'app.ml.matching.wakala_scoring'`
  4. `ModuleNotFoundError: No module named 'email_validator'`
* **Impact Développeur / CI-CD** :
  Les pipelines d'intégration continue backend sont bloqués et les algorithmes de pricing et de recommandation hybride ne peuvent pas être testés localement sans reconstruire un environnement virtuel complet.
* **Solution Recommandée** :
  Mettre à jour l'arborescence des imports (`wakala_scoring`), installer les dépendances de test requises et isoler les tests de ML dans une suite dédiée avec mocks d'inférence.

---

## 3. Logique Métier & Algorithme de Recommandation

### #07 — Gestion des requêtes contradictoires ou impossibles
* **Fichiers concernés** :
  * [`frontend/src/components/recommendation-experience/recommendationClient.ts`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/recommendationClient.ts)
  * [`frontend/src/components/recommendation-experience/RecommendationExperience.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/RecommendationExperience.tsx)
* **Description** :
  Si l'utilisateur demande une combinaison inexistante dans le catalogue (ex. *« une citadine 7 places »*, *« une Ferrari diesel »* ou *« un SUV électrique à moins de 80 000 MAD »*), le moteur filtre strictement jusqu'à obtenir 0 véhicule, puis affiche : *« Aucun véhicule ne correspond à tous ces critères. Élargissez la fourchette pour continuer »*.
* **Impact Utilisateur** :
  L'utilisateur se retrouve dans une impasse conversationnelle sans explication didactique sur la contradiction de sa demande.
* **Solution Recommandée** :
  Implémenter un détecteur de conflit de contraintes :
  * Identifier la contrainte la plus restrictive (ex. *citadine* vs *7 places*).
  * Répondre proactivement : *« Il n'existe pas de citadine 7 places. Souhaitez-vous plutôt voir des monospaces compacts ou des citadines 5 places ? »*.

---

### #08 — Désynchronisation visuelle entre filtres latéraux et chatbot
* **Fichiers concernés** :
  * [`frontend/src/pages/Catalogue.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/pages/Catalogue.tsx)
  * [`frontend/src/components/recommendation-experience/RecommendationExperience.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/RecommendationExperience.tsx)
* **Description** :
  Lorsque le chatbot applique un filtre (par exemple *SUV*, *Diesel*, *Automatique*), les véhicules affichés au centre sont correctement restreints, mais les cases à cocher de la colonne de filtres à gauche de la page ne se cochent pas automatiquement pour refléter ces critères.
* **Impact Utilisateur** :
  Confusion visuelle : l'utilisateur a l'impression que les filtres de la page sont inactifs alors que la liste est restreinte.
* **Solution Recommandée** :
  Émettre un événement bidirectionnel (`wakala:filter-sync`) pour synchroniser en temps réel l'état des composants de filtres du catalogue avec les décisions du chatbot.

---

### #10 — Absence de repli explicite en cas d'échec du scoring 8D
* **Fichiers concernés** :
  * [`frontend/src/components/recommendation-experience/RecommendationExperience.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/RecommendationExperience.tsx) (lignes 179-198)
  * [`frontend/src/components/recommendation-experience/EightDimensionScores.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/EightDimensionScores.tsx)
* **Description** :
  À la fin du questionnaire, le client appelle `recommendationService.scoreVehicles8d`. Si cet appel échoue (serveur hors ligne, erreur réseau), le bloc `catch` avale l'erreur sans notification et les 3 voitures finales s'affichent sans leurs badges de score 8D ni pourcentage de correspondance.
* **Impact Utilisateur** :
  L'utilisateur final perd la valeur ajoutée de l'explication comparative 8D sans savoir pourquoi les jauges ne s'affichent pas.
* **Solution Recommandée** :
  Calculer un score 8D heuristique de secours côté frontend basé sur les données techniques locales (coffre, puissance, consommation, NCAP) si le service distant ne répond pas.

---

## 4. Accessibilité & Traitement du Langage (NLU)

### #05 — Compatibilité de la saisie vocale sur navigateurs non-Chromium
* **Fichiers concernés** :
  * [`frontend/src/hooks/useVoiceAssistant.ts`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/hooks/useVoiceAssistant.ts)
  * [`frontend/src/hooks/useVoiceInput.ts`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/hooks/useVoiceInput.ts)
* **Description** :
  La reconnaissance vocale repose sur l'API native `window.SpeechRecognition || window.webkitSpeechRecognition`. Cette API est supportée sur Chrome et Edge, mais **désactivée par défaut ou absente sur Firefox et Safari mobile**.
* **Impact Utilisateur** :
  Sur iPhone ou Firefox, cliquer sur le micro ne produit aucun effet ou génère une erreur silencieuse.
* **Solution Recommandée** :
  1. Détecter le support de l'API au montage.
  2. Si non supportée, afficher un tooltip explicatif (*« La saisie vocale nécessite Google Chrome ou Microsoft Edge »*) ou intégrer un enregistreur audio HTML5 standard (`MediaRecorder`) envoyant l'audio au backend Whisper.

---

### #09 — Compréhension du Darija automobile spécifique dans le backend
* **Fichiers concernés** :
  * [`backend/app/rag/chatbot_chain.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/rag/chatbot_chain.py)
  * [`backend/app/rag/prompts.py`](file:///d:/Projet%20automobile/vente-auto-platform/backend/app/rag/prompts.py)
* **Description** :
  Le frontend reconnaît efficacement les mots clés Darija via regex (`bghit`, `tomobil`, `dyal`, `3a2ila`). En revanche, lorsque des questions techniques sont transmises au LLM du backend en Darija marocain avec du jargon local (ex. *la ferraille*, *ww*, *dédouanée*, *diwana*, *vignette*, *dariba*, *reprise*), le modèle généraliste interprète parfois le sens de manière approximative.
* **Impact Utilisateur** :
  Réponses hors sujet ou traductions littérales maladroites sur les questions administratives et le marché de l'occasion marocain.
* **Solution Recommandée** :
  Enrichir le prompt système du chatbot avec un glossaire marocain bilingue (Darija / Arabe / Français) couvrant les termes administratifs et marchands de l'automobile au Maroc.

---

### #11 — Expérience & Questionnaire Métier Spécial Taxi (Moul Taxi)
* **Fichiers concernés** :
  * [`frontend/src/components/recommendation-experience/recommendationClient.ts`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/recommendationClient.ts)
  * [`frontend/src/components/recommendation-experience/RecommendationExperience.tsx`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/RecommendationExperience.tsx)
  * [`frontend/src/components/recommendation-experience/recommendationClient.test.ts`](file:///d:/Projet%20automobile/vente-auto-platform/frontend/src/components/recommendation-experience/recommendationClient.test.ts)
* **Description** :
  Les requêtes des professionnels du taxi (ex. *« Ana moul taxi khesni tomobil s7i7a »*, *« chauffeur de taxi »*, *« سائق طاكسي »*) étaient auparavant classées dans la catégorie générique `commercial_commuter`. Le chatbot posait des questions inadaptées (*« Pour vos tournées professionnelles et déplacements fréquents... »*), affichait un curseur de budget catalogue disproportionné pouvant atteindre 39 millions MAD, et pouvait proposer des modèles de grand luxe (Audi, BMW, Porsche) dotés d'un moteur diesel.
* **Impact Utilisateur** :
  Perte de crédibilité immédiate auprès des professionnels du transport et recommandations incohérentes avec la réglementation marocaine du taxi (Petit Taxi vs Grand Taxi).
* **Solution Implémentée & Validée** :
  1. **Profil Dédié `'taxi'`** distinct dans `detectClientProfile` pour les 4 langues.
  2. **Question 1 de Qualification Taxi** : Petit Taxi (urbain, 5 places) vs Grand Taxi (interurbain, 6-7 places) avec chips cliquables.
  3. **Question 2 de Budget d'Investissement** : Slider borné et réaliste (`90 000 – 250 000 MAD`).
  4. **Question 3 de Priorité TCO** : Consommation minimale (Diesel/Hybride), pièces abordables & entretien facile, grand coffre & confort passagers.
  5. **Exclusion stricte (-500 pts)** de toutes les marques de luxe et coupés/cabriolets.
  6. **Bonus prioritaire (+60 à +35 pts)** pour les références du taxi marocain : Dacia (Logan, Sandero, Jogger), Fiat (Tipo, Doblo), Citroën (C-Elysée, Berlingo), Peugeot (208, 301, Partner), Renault (Clio, Express) et Toyota (Yaris/Corolla hybrides).

