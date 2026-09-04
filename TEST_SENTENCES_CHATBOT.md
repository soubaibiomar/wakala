# Guide de Test Conversationnel : Moteur de Recommandation & Chatbot Wakala

Ce document rassemble un jeu de phrases d'évaluation et de validation méthodique pour tester l'ensemble des fonctionnalités, aiguillages, détections multilingues et cas limites du chatbot et du moteur de recommandation Wakala.

---

## Sommaire

1. [Profils Professionnels & Rôles Statutaires (Soft Scoring)](#1-profils-professionnels--rôles-statutaires)
2. [Budget & Spécifications Techniques](#2-budget--spécifications-techniques)
3. [Requêtes Contradictoires & Arbitrage Métier (#07)](#3-requêtes-contradictoires--arbitrage-métier)
4. [Usage Familial & Capacité de Coffre](#4-usage-familial--capacité-de-coffre)
5. [Sécurité & Certifications Euro NCAP](#5-sécurité--certifications-euro-ncap)
6. [Marché Marocain & Réglementation Locale (#09)](#6-marché-marocain--réglementation-locale)
7. [Questions Techniques & Conseils Mécaniques (Non-recommandation)](#7-questions-techniques--conseils-mécaniques)
8. [Comparaisons Directes de Véhicules](#8-comparaisons-directes-de-véhicules)
9. [Darija Marocain & Arabizi Avancé](#9-darija-marocain--arabizi-avancé)
10. [Cas Extrêmes, Salutations & Reprise de Session](#10-cas-extrêmes-salutations--reprise-de-session)

---

## 1. Profils Professionnels & Rôles Statutaires

Ces requêtes doivent être reconnues comme des amorces de recommandation. Le chatbot doit adapter sa formulation, appliquer un bonus de pertinence (*soft scoring*) sur les segments adaptés et afficher le slider de budget.

| # | Phrase de Test | Langue | Comportement Attendu |
| :--- | :--- | :---: | :--- |
| 1.1 | `I am a director` | EN | Réponse valorisante pour dirigeant, proposition de berlines/SUV premium, slider de budget affiché. |
| 1.2 | `Je suis directeur d'entreprise` | FR | Qualification statutaire (*« En tant que dirigeant... »*), valorisation des modèles exécutifs. |
| 1.3 | `أنا مدير تنفيذي وأبحث عن سيارة تليق بموقعي` | AR | Détection sans échec, question sur le budget en arabe avec slider activé. |
| 1.4 | `Ana mdir chouff lia tomobil de standing` | Darija | Détection Arabizi (*mdir*), orientation vers les berlines ou SUV haut de gamme. |
| 1.5 | `Je suis médecin avec un budget de 380 000 MAD` | FR | Détection du profil médical + extraction immédiate du budget (<= 380k) + question sur l'usage (ville/gardes). |
| 1.6 | `I am a lawyer looking for a prestige car` | EN | Détection avocat/standing, filtrage automatique des berlines allemandes/prestige. |
| 1.7 | `Je suis commercial, je roule 40 000 km par an` | FR | Profil grand rouleur : priorisation du diesel et de l'hybride sobre, confort autoroutier. |
| 1.8 | `أنا أستاذ ميزانيتي 180000 درهم` | AR | Profil éducation / budget maîtrisé : suggestion de berlines compactes fiables et économiques. |
| 1.9 | `Je suis jeune conducteur, première voiture` | FR | Priorisation des citadines, faible puissance fiscale (CV) pour assurance réduite, note de sécurité. |
| 1.10 | `Ana moul taxi khesni tomobil s7i7a` | Darija | Détection chauffeur / fort kilométrage : robustesse (Dacia, Toyota, Fiat), diesel sobre, habitabilité. |

---

## 2. Budget & Spécifications Techniques

Test de l'extraction des filtres numériques, devises marocaines, carburants et boîtes de vitesses.

| # | Phrase de Test | Langue | Comportement Attendu |
| :--- | :--- | :---: | :--- |
| 2.1 | `SUV diesel automatique budget 300 000 MAD` | FR | Extraction combinée : Carrosserie = SUV, Carburant = Diesel, Boîte = Automatique, Prix max = 300 000. Synchronisation visuelle de la barre latérale (#08). |
| 2.2 | `Voiture électrique moins de 250 000 dhs` | FR | Filtre 100% électrique, plafond 250k. |
| 2.3 | `Car under 180k mad with manual gearbox` | EN | Détection 180k MAD, transmission manuelle. |
| 2.4 | `بغيت طوموبيل مازوط أوتوماتيك قل من 22 مليون` | Darija | Détection de 22 millions de centimes (= 220 000 MAD), carburant diesel, boîte auto. |
| 2.5 | `Voiture hybride rechargeable avec grand coffre` | FR | Carburant PHEV / Hybride rechargeable, filtre coffre >= 450 L. |
| 2.6 | `4x4 pour piste et montagne budget 400k` | FR | Transmission intégrale (is_4x4 = true), SUV ou tout-terrain. |

---

## 3. Requêtes Contradictoires & Arbitrage Métier (#07)

Ces combinaisons n'existent pas sur le marché. Le chatbot **ne doit jamais** afficher une page blanche ou une impasse avec zéro résultat, mais expliquer la contradiction et proposer des boutons de choix interactifs.

| # | Phrase de Test | Contradiction Métier | Comportement Attendu |
| :--- | :--- | :--- | :--- |
| 3.1 | `Je veux une citadine avec 7 places` | Une citadine fait 3,8 à 4,1m et ne possède que 4 ou 5 places. | Explication bienveillante + 2 boutons d'arbitrage : **« Voir monospaces / SUV 7 places »** vs **« Garder citadine 5 places »**. |
| 3.2 | `I want a city car for 7 passengers` | City car + 7 seats | Explication didactique en anglais avec options interactives. |
| 3.3 | `Je veux une Ferrari diesel` | Ferrari ne produit aucun moteur diesel. | Explication didactique (moteurs essence/hybrides V6/V8) + boutons : **« Voir Ferrari en essence »** vs **« Berlines sportives diesel (BMW, Audi) »**. |
| 3.4 | `باغي فراري مازوط` | Marque de luxe + Mazout | Explication en Darija/Arabe que Ferrari ne fait pas de diesel + suggestions alternatives. |
| 3.5 | `Voiture neuve 100% électrique budget max 80 000 MAD` | Les VE neufs au Maroc débutent au-delà de 170 000 MAD. | Explication sur les prix du marché VE au Maroc + boutons : **« Citadines diesel/essence économiques »** vs **« Ajuster le budget pour l'électrique »**. |

---

## 4. Usage Familial & Capacité de Coffre

| # | Phrase de Test | Langue | Comportement Attendu |
| :--- | :--- | :---: | :--- |
| 4.1 | `Voiture pour famille avec 3 enfants et poussette` | FR | Détection profil familial : minimum 5 vraies places, coffre >= 450 L, carrosseries SUV / ludospace / break. |
| 4.2 | `Family car with 5 suitcases luggage space` | EN | Détection volume bagages (5 valises ~ 500L), préservation des modèles familiaux. |
| 4.3 | `طوموبيل ديال العائلة واسعة لـ 6 ديال الناس` | Darija | Détection famille nombreuse : véhicules 6 à 7 places (Dacia Jogger, SUV 7 pl). |
| 4.4 | `Besoin de place pour sièges auto Isofix à l'arrière` | FR | Priorisation de la largeur aux coudes arrière et des notes de sécurité enfants Euro NCAP. |

---

## 5. Sécurité & Certifications Euro NCAP

| # | Phrase de Test | Langue | Comportement Attendu |
| :--- | :--- | :---: | :--- |
| 5.1 | `Note NCAP maximale` | FR | Filtrage strict des véhicules ayant obtenu 5 étoiles Euro NCAP. |
| 5.2 | `I want the safest car possible for my daughter` | EN | Priorisation des modèles 5★ NCAP avec aides à la conduite (ADAS) et bon score de protection des occupants. |
| 5.3 | `أكثر سيارة أماناً وسلامة في حدود 250 ألف درهم` | AR | Tri par note de sécurité NCAP décroissante sous le plafond budgétaire de 250k. |
| 5.4 | `Bonne sécurité certifiée` | FR | Filtrage des modèles ayant au moins 4 ou 5 étoiles NCAP. |

---

## 6. Marché Marocain & Réglementation Locale (#09)

Vérifie la bonne compréhension du glossaire automobile marocain par le LLM backend sans confusion avec d'autres pays.

| # | Phrase de Test | Thème | Comportement Attendu |
| :--- | :--- | :--- | :--- |
| 6.1 | `C'est quoi une voiture WW au Maroc ?` | Immatriculation | Expliquer qu'il s'agit d'un véhicule neuf de première main immatriculé provisoirement au Maroc. |
| 6.2 | `Combien coûte la vignette pour une voiture de 8 CV diesel ?` | Taxe / Dariba | Donner le tarif officiel de la taxe spéciale annuelle (1 500 MAD pour 8 à 10 CV diesel). |
| 6.3 | `Chnou hiya l-far9 bin WW w dédouanée ?` | Darija / Douane | Expliquer la différence entre voiture achetée neuve au Maroc (WW) et véhicule d'occasion importé (Diwana acquittée). |
| 6.4 | `Comment fonctionne la reprise d'une ancienne voiture chez un concessionnaire ?` | Transaction | Explication du rachat de l'ancien véhicule déduit du prix du nouveau modèle avec soulte. |
| 6.5 | `Est-ce que les pièces de rechange sont faciles à trouver à la ferraille ?` | Entretien local | Mention des zones spécialisées (Salé, Hay Inara Casablanca) et de la disponibilité selon les marques (Dacia, Renault, Peugeot). |

---

## 7. Questions Techniques & Conseils Mécaniques

Ces questions doivent être traitées comme des **consultations techniques d'expert** et **ne doivent pas** déclencher le questionnaire de recommandation ni forcer une recherche de catalogue.

| # | Phrase de Test | Domaine | Comportement Attendu |
| :--- | :--- | :--- | :--- |
| 7.1 | `Quelle est la différence entre courroie et chaîne de distribution ?` | Mécanique | Explication technique claire des avantages/inconvénients (entretien vs longévité) sans forcer la vente d'une voiture. |
| 7.2 | `Pourquoi mon moteur surchauffe en côte ?` | Diagnostic | Analyse technique (liquide de refroidissement, thermostat, radiateur encrassé, ventilateur). |
| 7.3 | `Comment préserver la batterie d'une voiture électrique en été ?` | Véhicule électrique | Conseils sur la recharge entre 20% et 80%, préconditionnement thermique et stationnement à l'ombre. |
| 7.4 | `C'est quoi un moteur 1.5 dCi et est-il fiable ?` | Moteur | Historique et retour d'expérience sur le bloc Renault/Dacia K9K (injecteurs, consommation, longévité). |
| 7.5 | `Voyant moteur allumé couleur orange : est-ce urgent ?` | Diagnostic sécurité | Différencier voyant orange (alerte antipollution/capteur, rouler modérément) et voyant rouge (arrêt immédiat). |

---

## 8. Comparaisons Directes de Véhicules

| # | Phrase de Test | Modèles Comparés | Comportement Attendu |
| :--- | :--- | :--- | :--- |
| 8.1 | `Compare Dacia Duster et Renault Captur` | Duster vs Captur | Tableau comparatif ou synthèse : habitabilité, garde au sol, équipement, motorisation et écart de prix. |
| 8.2 | `Quelle est la plus sobre entre Peugeot 208 diesel et Renault Clio 5 diesel ?` | 208 vs Clio | Comparaison des consommations réelles mixtes (~4.0 à 4.5 L/100km) et agrément de conduite. |
| 8.3 | `Hyundai Tucson ou Kia Sportage : lequel choisir ?` | Tucson vs Sportage | Comparaison plateforme commune, garantie, design, volume de coffre et décote au Maroc. |
| 8.4 | `Toyota Yaris hybride vs Dacia Sandero essence` | Économie vs Coût initial | Analyse coût total de possession (TCO) : achat moins cher pour Sandero vs conso réduite pour Yaris. |

---

## 9. Darija Marocain & Arabizi Avancé

| # | Phrase de Test | Équivalent | Comportement Attendu |
| :--- | :--- | :--- | :--- |
| 9.1 | `Bghit tomobil jdida dyal l-khdma w l-dar budget 25 mlyon` | Voiture neuve mixte pro/famille 250 000 MAD | Détection de l'intention d'achat, du budget (250 000 MAD) et qualification de l'usage. |
| 9.2 | `Khesni tonobile sghira f l-mdina ma katconsomich bzaf` | Citadine sobre pour la ville | Filtrage citadines essence/hybrides avec consommation < 5.0 L/100km. |
| 9.3 | `Chnou a7san tomobil l wa7ed yallah chad permis ?` | Meilleure voiture pour jeune permis | Recommandation bienveillante de citadines maniables avec bonne visibilité et coût d'entretien modéré. |
| 9.4 | `Wash nakhod essence wla diesel pour 15 000 km par an ?` | Arbitrage carburant | Calcul d'amortissement : à 15 000 km/an, conseil en faveur de l'essence ou de l'hybride vu le surcoût de la vignette et de l'achat diesel. |

---

## 10. Cas Extrêmes, Salutations & Reprise de Session

| # | Phrase de Test | Cas Testé | Comportement Attendu |
| :--- | :--- | :--- | :--- |
| 10.1 | `Salam / Bonjour / Hello / أهلاً` | Salutation multilingue | Accueil chaleureux dans la langue exacte de l'utilisateur avec présentation des capacités de Wakala. |
| 10.2 | `Chokran / Merci beaucoup / Thank you` | Remerciement | Réponse polie de clôture sans relancer de question intempestive. |
| 10.3 | `Quel est le meilleur restaurant de Casablanca ?` | Hors domaine automobile | Réponse cadrée indiquant que Wakala est exclusivement spécialisé dans l'automobile, avec invitation à poser une question voiture. |
| 10.4 | `F5 (Rechargement de page en cours de questionnaire)` | Persistance de session (#06) | La conversation et les voitures sélectionnées réapparaissent à l'identique après rafraîchissement. |
| 10.5 | `Clic sur "Catalogue ↗" depuis la bulle d'accueil (#01)` | Handoff inter-pages | Redirection vers `/catalogue` en injectant automatiquement la dernière recherche de l'utilisateur. |

---

### Résumé des Commandes de Validation Automatisée

Pour vérifier la robustesse avant toute démonstration :

```powershell
# 1. Tests Frontend (132 tests incluant détection d'intention 4 langues)
cd "d:\Projet automobile\vente-auto-platform\frontend"
npm test

# 2. Validation TypeScript
npx tsc --noEmit

# 3. Tests Backend (19 tests ML, Scoring 8D et devises marocaines)
cd "d:\Projet automobile\vente-auto-platform\backend"
.venv\Scripts\python.exe -m pytest tests\test_recommendation.py tests\unit\test_wakala_scoring.py tests\test_wakala_core.py tests\test_multilingual_parser.py
```
