# Brand Coverage — Marché Automobile Marocain

> Tableau de suivi de la couverture par marque pour le scraping de véhicules neufs.
> Mis à jour à chaque marque traitée.

## Légende statuts
- 🔍 **À investiguer** — URL du distributeur non confirmée
- 🌐 **URL confirmée** — URL trouvée, robots.txt OK, en attente de sélecteurs
- ✅ **Actif** — Scraper opérationnel, données collectées
- ⛔ **Pas de catalogue** — Site purement vitrine, pas de stock/prix en ligne
- 🔒 **robots.txt bloquant** — Scraping interdit par le site

## Couverture Actuelle

| Marque | Groupe/Distributeur | Entrée dealers.yaml | Scraper dédié | Statut |
|---|---|---|---|---|
| Renault | M-Automotiv | `m_automotiv` | — | 🔍 À investiguer |
| Dacia | M-Automotiv | `m_automotiv` | — | 🔍 À investiguer |
| Soueast | M-Automotiv | `m_automotiv` | — | 🔍 À investiguer |
| KGM | M-Automotiv | `m_automotiv` | — | 🔍 À investiguer |
| Exeed | M-Automotiv | `m_automotiv` | — | 🔍 À investiguer |
| JAC Motors | M-Automotiv | `m_automotiv` | — | 🔍 À investiguer |
| Ford | Auto Hall | `auto_hall` | — | 🔍 À investiguer |
| Opel | Auto Hall | `auto_hall` | — | 🔍 À investiguer |
| Nissan | Auto Hall | `auto_hall` | — | 🔍 À investiguer |
| Mitsubishi | Auto Hall | `auto_hall` | — | 🔍 À investiguer |
| Fiat | Auto Hall / Alliance | `auto_hall` / `alliance_automotive` | — | 🔍 À investiguer |
| Jeep | Auto Hall / Alliance | `auto_hall` / `alliance_automotive` | — | 🔍 À investiguer |
| Alfa Romeo | Auto Hall / Alliance | `auto_hall` / `alliance_automotive` | — | 🔍 À investiguer |
| Maserati | Auto Hall | `auto_hall` | — | 🔍 À investiguer |
| Chery | Auto Hall / chery_maroc | `auto_hall` / `chery_maroc` | — | 🔍 À investiguer |
| DFSK | Auto Hall | `auto_hall` | — | 🔍 À investiguer |
| Seres | Auto Hall | `auto_hall` | — | 🔍 À investiguer |
| Volkswagen | CAC | `cac_volkswagen_group` | — | ⛔ Pas de catalogue |
| Audi | CAC | `cac_volkswagen_group` | — | ⛔ Pas de catalogue |
| Porsche | CAC | `cac_volkswagen_group` | — | ⛔ Pas de catalogue |
| Bentley | CAC | `cac_volkswagen_group` | — | ⛔ Pas de catalogue |
| SEAT | CAC | `seat_cac_network` | — | 🔍 À investiguer |
| Cupra | CAC | `cac_volkswagen_group` | — | ⛔ Pas de catalogue |
| Skoda | CAC | `cac_volkswagen_group` | — | ⛔ Pas de catalogue |
| Great Wall / GWM | Tractafric Motors | `tractafric_motors` | — | ⛔ Pas de catalogue |
| Mercedes-Benz | Tractafric Motors | `tractafric_motors` | — | ⛔ Pas de catalogue |
| Toyota | TDM | `toyota_maroc` | — | 🔍 À investiguer |
| Hyundai | Hyundai Maroc | `hyundai_maroc` | — | 🔍 À investiguer |
| Kia | Kia Maroc | `kia_maroc` | — | 🔍 À investiguer |
| BMW | SMEIA | `smeia` | — | 🔍 À investiguer |
| MINI | SMEIA | `smeia` | — | 🔍 À investiguer |
| Land Rover | SMEIA | `smeia` | — | 🔍 À investiguer |
| Jaguar | SMEIA | `smeia` | — | 🔍 À investiguer |
| Peugeot | Sopriam | `sopriam` | — | 🔍 À investiguer |
| Citroën | Sopriam | `sopriam` | — | 🔍 À investiguer |
| DS | Sopriam | `sopriam` | — | 🔍 À investiguer |
| BYD | BYD Maroc | `byd_maroc` | — | 🔍 À investiguer |
| MG Motor | MG Maroc | `mg_maroc` | — | 🔍 À investiguer |
| Suzuki | Suzuki Maroc | `suzuki_maroc` | — | 🔍 À investiguer |
| Honda | Honda Maroc | `honda_maroc` | — | 🔍 À investiguer |

## Couverture par Scrapers Généralistes (véhicules neufs uniquement)

| Source | Scraper | Statut pivot |
|---|---|---|
| Wandaloo | `wandaloo_scraper.py` | ✅ New-only — inchangé |
| Kifal Auto | `kifal_scraper.py` | ✅ New-focused — inchangé |
| Moteur.ma | `moteur_scraper.py` | 🔧 Mixed — restreint aux sections neuves |
| LeGuideAuto | `leguideauto_scraper.py` | 🔧 Mixed — restreint aux sections neuves |
| Otoclic | `otoclic_scraper.py` | 🔧 Mixed — restreint aux sections neuves |

## Scrapers Désactivés (pivot neuf)

| Source | Scraper | Raison |
|---|---|---|
| Avito | `avito_scraper.py` | Marketplace occasion uniquement |
| GlobalOccaz | `global_occaz_scraper.py` | Marketplace occasion uniquement |
| Spoticar | `spoticar_scraper.py` | Véhicules d'occasion certifiés |
| Carz | `carz_scraper.py` | Marketplace occasion uniquement |
