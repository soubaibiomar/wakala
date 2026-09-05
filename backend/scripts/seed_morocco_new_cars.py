import asyncio
import uuid
import re
from sqlalchemy import select, delete, text
from app.core.database import async_session_factory, engine, Base
from app.models.catalog import BrandCatalog, ModelCatalog, PowertrainCatalog, TrimCatalog
from app.models.equipment import EquipmentCategory, EquipmentFeature, TrimEquipmentMapping
from app.models.dealership import Dealership, Showroom


import unicodedata

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text


NEW_CARS_DATA = [
    # ─── DACIA ─────────────────────────────────────────────────────────────
    {
        "brand": "Dacia",
        "origin": "Roumanie / Maroc (Usine Somaca & Tanger)",
        "logo": "https://raw.githubusercontent.com/filippofinke/car-logos/master/logos/optimized/dacia.svg",
        "models": [
            {
                "name": "Sandero Streetway",
                "body_type": "Citadine",
                "year_start": 2024,
                "image": "https://cdn.group.renault.com/dac/fr/vehicules/sandero/sandero-streetway-bji-ph1/decouverte/dacia-sandero-streetway-bji-ph1-001.jpg",
                "powertrains": [
                    {
                        "name": "1.0 TCe 90",
                        "fuel_type": "ESSENCE",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 90,
                        "torque_nm": 160,
                        "transmission": "MANUELLE",
                        "consumption_l_100": 5.2,
                        "co2": 118,
                        "trims": [
                            {"name": "Essential", "price": 145000, "promo": 139900, "trunk": 328, "stars": 3},
                            {"name": "Expression", "price": 160000, "promo": 154900, "trunk": 328, "stars": 3},
                        ]
                    },
                    {
                        "name": "1.5 dCi 95",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 95,
                        "torque_nm": 220,
                        "transmission": "MANUELLE",
                        "consumption_l_100": 4.1,
                        "co2": 108,
                        "trims": [
                            {"name": "Expression dCi", "price": 175000, "promo": 169900, "trunk": 328, "stars": 3},
                            {"name": "Journey dCi", "price": 189000, "promo": 183900, "trunk": 328, "stars": 3},
                        ]
                    },
                ]
            },
            {
                "name": "Sandero Stepway",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://cdn.group.renault.com/dac/fr/vehicules/sandero/sandero-stepway-bji-ph1/decouverte/dacia-sandero-stepway-bji-ph1-001.jpg",
                "powertrains": [
                    {
                        "name": "1.5 dCi 102",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 102,
                        "torque_nm": 240,
                        "transmission": "MANUELLE",
                        "consumption_l_100": 4.4,
                        "co2": 115,
                        "trims": [
                            {"name": "Expression", "price": 182000, "promo": 176900, "trunk": 328, "stars": 3},
                            {"name": "Extreme", "price": 198000, "promo": 192900, "trunk": 328, "stars": 3},
                        ]
                    },
                    {
                        "name": "1.0 TCe 90 CVT",
                        "fuel_type": "ESSENCE",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 90,
                        "torque_nm": 142,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.8,
                        "co2": 131,
                        "trims": [
                            {"name": "Expression BVA", "price": 189000, "promo": 183000, "trunk": 328, "stars": 3},
                            {"name": "Extreme BVA", "price": 205000, "promo": 199900, "trunk": 328, "stars": 3},
                        ]
                    }
                ]
            },
            {
                "name": "Duster 3 (2024+)",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://cdn.group.renault.com/dac/fr/vehicules/duster/duster-iii-p1310/decouverte/dacia-nouveau-duster-p1310-001.jpg",
                "powertrains": [
                    {
                        "name": "1.5 dCi 115 4x2",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 115,
                        "torque_nm": 260,
                        "transmission": "MANUELLE",
                        "consumption_l_100": 4.8,
                        "co2": 126,
                        "trims": [
                            {"name": "Expression", "price": 225000, "promo": 218900, "trunk": 472, "stars": 4},
                            {"name": "Journey", "price": 249000, "promo": 242000, "trunk": 472, "stars": 4},
                            {"name": "Extreme", "price": 259000, "promo": 252000, "trunk": 472, "stars": 4},
                        ]
                    },
                    {
                        "name": "Hybrid 140 Automatique",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 5,
                        "engine_power_hp": 140,
                        "torque_nm": 205,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.5,
                        "co2": 102,
                        "trims": [
                            {"name": "Journey Hybrid", "price": 285000, "promo": 275000, "trunk": 430, "stars": 4},
                            {"name": "Extreme Hybrid", "price": 298000, "promo": 289000, "trunk": 430, "stars": 4},
                        ]
                    }
                ]
            }
        ]
    },

    # ─── RENAULT ───────────────────────────────────────────────────────────
    {
        "brand": "Renault",
        "origin": "France",
        "logo": "https://raw.githubusercontent.com/filippofinke/car-logos/master/logos/optimized/renault.svg",
        "models": [
            {
                "name": "Clio 5 Restylée",
                "body_type": "Citadine",
                "year_start": 2024,
                "image": "https://cdn.group.renault.com/ren/fr/vehicules/clio/clio-v-ph2/decouverte/renault-clio-v-ph2-001.jpg",
                "powertrains": [
                    {
                        "name": "1.5 Blue dCi 100",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 100,
                        "torque_nm": 260,
                        "transmission": "MANUELLE",
                        "consumption_l_100": 4.1,
                        "co2": 108,
                        "trims": [
                            {"name": "Evolution", "price": 202000, "promo": 195000, "trunk": 391, "stars": 5},
                            {"name": "Techno", "price": 222000, "promo": 215000, "trunk": 391, "stars": 5},
                            {"name": "Esprit Alpine", "price": 242000, "promo": 235000, "trunk": 391, "stars": 5},
                        ]
                    },
                    {
                        "name": "E-Tech full hybrid 145",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 5,
                        "engine_power_hp": 145,
                        "torque_nm": 205,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.2,
                        "co2": 95,
                        "trims": [
                            {"name": "Techno E-Tech", "price": 265000, "promo": 255000, "trunk": 300, "stars": 5},
                            {"name": "Esprit Alpine E-Tech", "price": 289000, "promo": 279000, "trunk": 300, "stars": 5},
                        ]
                    }
                ]
            },
            {
                "name": "Captur Restylé",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://cdn.group.renault.com/ren/fr/vehicules/captur/captur-ii-ph2/decouverte/renault-captur-ii-ph2-001.jpg",
                "powertrains": [
                    {
                        "name": "1.5 Blue dCi 115 EDC",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 115,
                        "torque_nm": 260,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.7,
                        "co2": 124,
                        "trims": [
                            {"name": "Evolution dCi EDC", "price": 265000, "promo": 257000, "trunk": 422, "stars": 5},
                            {"name": "Techno dCi EDC", "price": 289000, "promo": 279000, "trunk": 422, "stars": 5},
                        ]
                    },
                    {
                        "name": "E-Tech full hybrid 145",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 5,
                        "engine_power_hp": 145,
                        "torque_nm": 205,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.6,
                        "co2": 105,
                        "trims": [
                            {"name": "Esprit Alpine Hybrid", "price": 335000, "promo": 322000, "trunk": 326, "stars": 5},
                        ]
                    }
                ]
            },
            {
                "name": "Austral",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://cdn.group.renault.com/ren/fr/vehicules/austral/austral-hhn/decouverte/renault-austral-hhn-001.jpg",
                "powertrains": [
                    {
                        "name": "E-Tech full hybrid 200",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 7,
                        "engine_power_hp": 200,
                        "torque_nm": 410,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.6,
                        "co2": 104,
                        "trims": [
                            {"name": "Techno", "price": 415000, "promo": 399000, "trunk": 430, "stars": 5},
                            {"name": "Esprit Alpine", "price": 465000, "promo": 449000, "trunk": 430, "stars": 5},
                            {"name": "Iconic Esprit Alpine", "price": 499000, "promo": 485000, "trunk": 430, "stars": 5},
                        ]
                    }
                ]
            }
        ]
    },

    # ─── PEUGEOT ───────────────────────────────────────────────────────────
    {
        "brand": "Peugeot",
        "origin": "France / Maroc (Usine Stellantis Kénitra)",
        "logo": "https://raw.githubusercontent.com/filippofinke/car-logos/master/logos/optimized/peugeot.svg",
        "models": [
            {
                "name": "208 Restylée",
                "body_type": "Citadine",
                "year_start": 2024,
                "image": "https://www.peugeot.fr/content/dam/peugeot/master/b2c/open/showroom/208/208-restylee/visuals/peugeot-208-restylee-vue-3-4-avant.jpg",
                "powertrains": [
                    {
                        "name": "1.5 BlueHDi 100",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 100,
                        "torque_nm": 250,
                        "transmission": "MANUELLE",
                        "consumption_l_100": 4.0,
                        "co2": 106,
                        "trims": [
                            {"name": "Active", "price": 195000, "promo": 188000, "trunk": 311, "stars": 4},
                            {"name": "Allure", "price": 218000, "promo": 209900, "trunk": 311, "stars": 4},
                            {"name": "GT", "price": 245000, "promo": 236000, "trunk": 311, "stars": 4},
                        ]
                    },
                    {
                        "name": "Hybrid 100 e-DCS6",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 5,
                        "engine_power_hp": 100,
                        "torque_nm": 205,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.5,
                        "co2": 101,
                        "trims": [
                            {"name": "Allure Hybrid", "price": 239000, "promo": 229900, "trunk": 311, "stars": 4},
                            {"name": "GT Hybrid", "price": 265000, "promo": 255000, "trunk": 311, "stars": 4},
                        ]
                    }
                ]
            },
            {
                "name": "2008 Restylé",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://www.peugeot.fr/content/dam/peugeot/master/b2c/open/showroom/2008/2008-restyle/visuals/peugeot-2008-restyle-vue-3-4-avant.jpg",
                "powertrains": [
                    {
                        "name": "1.5 BlueHDi 130 EAT8",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 130,
                        "torque_nm": 300,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.8,
                        "co2": 127,
                        "trims": [
                            {"name": "Allure Pack HDi", "price": 299000, "promo": 289000, "trunk": 434, "stars": 4},
                            {"name": "GT HDi", "price": 329000, "promo": 319000, "trunk": 434, "stars": 4},
                        ]
                    },
                    {
                        "name": "Hybrid 136 e-DCS6",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 136,
                        "torque_nm": 230,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.9,
                        "co2": 111,
                        "trims": [
                            {"name": "Allure Hybrid", "price": 315000, "promo": 305000, "trunk": 434, "stars": 4},
                            {"name": "GT Hybrid", "price": 345000, "promo": 332000, "trunk": 434, "stars": 4},
                        ]
                    }
                ]
            },
            {
                "name": "3008 (Nouveau)",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://www.peugeot.fr/content/dam/peugeot/master/b2c/open/showroom/3008/nouveau-3008/visuals/peugeot-nouveau-3008-vue-3-4-avant.jpg",
                "powertrains": [
                    {
                        "name": "Hybrid 136 e-DCS6",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 7,
                        "engine_power_hp": 136,
                        "torque_nm": 230,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.5,
                        "co2": 124,
                        "trims": [
                            {"name": "Allure Hybrid", "price": 389000, "promo": 375000, "trunk": 520, "stars": 5},
                            {"name": "GT Hybrid", "price": 439000, "promo": 422000, "trunk": 520, "stars": 5},
                        ]
                    }
                ]
            }
        ]
    },

    # ─── HYUNDAI ───────────────────────────────────────────────────────────
    {
        "brand": "Hyundai",
        "origin": "Corée du Sud",
        "logo": "https://raw.githubusercontent.com/filippofinke/car-logos/master/logos/optimized/hyundai.svg",
        "models": [
            {
                "name": "Tucson Restylé",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://www.hyundai.com/content/dam/hyundai/ww/en/images/find-a-car/all-vehicles/tucson-2024/highlights/hyundai-tucson-2024-highlights-kv-m.jpg",
                "powertrains": [
                    {
                        "name": "1.6 CRDi 136 DCT",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 136,
                        "torque_nm": 320,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.3,
                        "co2": 139,
                        "trims": [
                            {"name": "Attractive", "price": 335000, "promo": 325000, "trunk": 546, "stars": 5},
                            {"name": "Inventive", "price": 375000, "promo": 362000, "trunk": 546, "stars": 5},
                            {"name": "Prestige", "price": 415000, "promo": 399000, "trunk": 546, "stars": 5},
                        ]
                    },
                    {
                        "name": "1.6 T-GDi Hybrid 230 BVA",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 7,
                        "engine_power_hp": 230,
                        "torque_nm": 350,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.6,
                        "co2": 127,
                        "trims": [
                            {"name": "Premium Hybrid", "price": 445000, "promo": 429000, "trunk": 616, "stars": 5},
                            {"name": "Luxe Hybrid 4x4", "price": 499000, "promo": 479000, "trunk": 616, "stars": 5},
                        ]
                    }
                ]
            },
            {
                "name": "i20",
                "body_type": "Citadine",
                "year_start": 2024,
                "image": "https://www.hyundai.com/content/dam/hyundai/ww/en/images/find-a-car/all-vehicles/i20-2023/highlights/hyundai-i20-2023-highlights-kv-m.jpg",
                "powertrains": [
                    {
                        "name": "1.0 T-GDi 100 DCT",
                        "fuel_type": "ESSENCE",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 100,
                        "torque_nm": 172,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.4,
                        "co2": 123,
                        "trims": [
                            {"name": "Attractive", "price": 185000, "promo": 179000, "trunk": 352, "stars": 4},
                            {"name": "Inventive", "price": 209000, "promo": 199900, "trunk": 352, "stars": 4},
                        ]
                    }
                ]
            }
        ]
    },

    # ─── TOYOTA ────────────────────────────────────────────────────────────
    {
        "brand": "Toyota",
        "origin": "Japon",
        "logo": "https://raw.githubusercontent.com/filippofinke/car-logos/master/logos/optimized/toyota.svg",
        "models": [
            {
                "name": "Yaris Cross Hybrid",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://scene7.toyota.eu/is/image/toyotaeurope/Yaris-Cross-2024-gallery-01?wid=1280&fit=constrain",
                "powertrains": [
                    {
                        "name": "1.5 Hybrid 116h e-CVT",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 5,
                        "engine_power_hp": 116,
                        "torque_nm": 141,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 4.4,
                        "co2": 100,
                        "trims": [
                            {"name": "Dynamic", "price": 275000, "promo": 265000, "trunk": 397, "stars": 5},
                            {"name": "Lounge", "price": 309000, "promo": 299000, "trunk": 397, "stars": 5},
                            {"name": "GR Sport", "price": 339000, "promo": 325000, "trunk": 397, "stars": 5},
                        ]
                    }
                ]
            },
            {
                "name": "RAV4 Hybrid",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://scene7.toyota.eu/is/image/toyotaeurope/RAV4-gallery-01?wid=1280&fit=constrain",
                "powertrains": [
                    {
                        "name": "2.5 Hybrid 218h 4x2",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 9,
                        "engine_power_hp": 218,
                        "torque_nm": 221,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.6,
                        "co2": 126,
                        "trims": [
                            {"name": "Dynamic", "price": 435000, "promo": 419000, "trunk": 580, "stars": 5},
                            {"name": "Lounge", "price": 495000, "promo": 479000, "trunk": 580, "stars": 5},
                        ]
                    }
                ]
            }
        ]
    },

    # ─── VOLKSWAGEN ────────────────────────────────────────────────────────
    {
        "brand": "Volkswagen",
        "origin": "Allemagne",
        "logo": "https://raw.githubusercontent.com/filippofinke/car-logos/master/logos/optimized/volkswagen.svg",
        "models": [
            {
                "name": "T-Roc Restylé",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://www.volkswagen.fr/content/dam/onehub_pkw/importers/fr/modeles/t-roc/t-roc-pa/highlights/t-roc-pa-highlights-16-9-1.jpg",
                "powertrains": [
                    {
                        "name": "2.0 TDI 150 DSG7",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 8,
                        "engine_power_hp": 150,
                        "torque_nm": 360,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.0,
                        "co2": 131,
                        "trims": [
                            {"name": "Life", "price": 345000, "promo": 335000, "trunk": 445, "stars": 5},
                            {"name": "Style", "price": 389000, "promo": 375000, "trunk": 445, "stars": 5},
                            {"name": "R-Line", "price": 435000, "promo": 419000, "trunk": 445, "stars": 5},
                        ]
                    }
                ]
            },
            {
                "name": "Tiguan (Nouveau)",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://www.volkswagen.fr/content/dam/onehub_pkw/importers/fr/modeles/tiguan/tiguan-3/highlights/tiguan-3-highlights-16-9-1.jpg",
                "powertrains": [
                    {
                        "name": "2.0 TDI 150 DSG7",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 8,
                        "engine_power_hp": 150,
                        "torque_nm": 360,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.3,
                        "co2": 139,
                        "trims": [
                            {"name": "Life Plus", "price": 449000, "promo": 435000, "trunk": 652, "stars": 5},
                            {"name": "Elegance", "price": 509000, "promo": 489000, "trunk": 652, "stars": 5},
                            {"name": "R-Line", "price": 559000, "promo": 539000, "trunk": 652, "stars": 5},
                        ]
                    }
                ]
            }
        ]
    },

    # ─── KIA ───────────────────────────────────────────────────────────────
    {
        "brand": "Kia",
        "origin": "Corée du Sud",
        "logo": "https://raw.githubusercontent.com/filippofinke/car-logos/master/logos/optimized/kia.svg",
        "models": [
            {
                "name": "Sportage",
                "body_type": "SUV",
                "year_start": 2024,
                "image": "https://www.kia.com/content/dam/kwcms/kme/global/en/assets/vehicles/sportage-nq5/discover/kia-sportage-nq5-front-quarter-driving-profile.jpg",
                "powertrains": [
                    {
                        "name": "1.6 CRDi 136 DCT7",
                        "fuel_type": "DIESEL",
                        "fiscal_power_cv": 6,
                        "engine_power_hp": 136,
                        "torque_nm": 320,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.2,
                        "co2": 136,
                        "trims": [
                            {"name": "Active", "price": 339000, "promo": 325000, "trunk": 571, "stars": 5},
                            {"name": "Design", "price": 379000, "promo": 365000, "trunk": 571, "stars": 5},
                            {"name": "GT Line", "price": 425000, "promo": 409000, "trunk": 571, "stars": 5},
                        ]
                    },
                    {
                        "name": "1.6 T-GDi Hybrid 230 BVA",
                        "fuel_type": "HYBRIDE",
                        "fiscal_power_cv": 7,
                        "engine_power_hp": 230,
                        "torque_nm": 350,
                        "transmission": "AUTOMATIQUE",
                        "consumption_l_100": 5.5,
                        "co2": 125,
                        "trims": [
                            {"name": "GT Line Hybrid", "price": 465000, "promo": 449000, "trunk": 587, "stars": 5},
                        ]
                    }
                ]
            }
        ]
    }
]

STANDARD_EQUIPMENT_FEATURES = [
    # Sécurité & ADAS
    {"category": "Sécurité & ADAS", "icon": "shield", "name": "Freinage autonome d'urgence (AEB)", "description": "Détection piétons, cyclistes et véhicules"},
    {"category": "Sécurité & ADAS", "icon": "shield", "name": "Aide au maintien dans la voie (LKA)", "description": "Correction active de trajectoire"},
    {"category": "Sécurité & ADAS", "icon": "shield", "name": "Régulateur de vitesse adaptatif (ACC)", "description": "Maintien automatique de la distance de sécurité"},
    {"category": "Sécurité & ADAS", "icon": "shield", "name": "Surveillance des angles morts (BSM)", "description": "Alerte visuelle et sonore dans les rétroviseurs"},
    {"category": "Sécurité & ADAS", "icon": "shield", "name": "Airbags frontaux, latéraux et rideaux (6-8)", "description": "Protection intégrale des occupants"},
    
    # Confort & Vie à bord
    {"category": "Confort & Vie à bord", "icon": "user", "name": "Climatisation automatique bi-zone", "description": "Réglage séparé conducteur et passager"},
    {"category": "Confort & Vie à bord", "icon": "user", "name": "Accès & Démarrage mains libres (Keyless)", "description": "Carte ou clé intelligente avec bouton Start"},
    {"category": "Confort & Vie à bord", "icon": "user", "name": "Sièges avant chauffants", "description": "Chauffage réglable multi-niveaux"},
    {"category": "Confort & Vie à bord", "icon": "user", "name": "Toit ouvrant panoramique en verre", "description": "Grande luminosité avec rideau occultant électrique"},
    {"category": "Confort & Vie à bord", "icon": "user", "name": "Sellerie cuir / Alcantara", "description": "Finition premium surpiquée"},

    # Multimédia & Connectivité
    {"category": "Multimédia & Connectivité", "icon": "wifi", "name": "Écran tactile HD 10\" avec Navigation GPS Maroc", "description": "Cartographie marocaine intégrée avec POIs"},
    {"category": "Multimédia & Connectivité", "icon": "wifi", "name": "Apple CarPlay & Android Auto sans fil", "description": "Duplication smartphone par Wi-Fi sans câble"},
    {"category": "Multimédia & Connectivité", "icon": "wifi", "name": "Chargeur à induction pour smartphone", "description": "Recharge sans fil rapide dans la console"},
    {"category": "Multimédia & Connectivité", "icon": "wifi", "name": "Système audio premium (Bose / Focal / Harman Kardon)", "description": "Son haute fidélité avec caisson de basses"},

    # Design & Extérieur
    {"category": "Design & Extérieur", "icon": "eye", "name": "Phares 100% Full LED automatiques", "description": "Éclairage dynamique avec commutation feux de route"},
    {"category": "Design & Extérieur", "icon": "eye", "name": "Jantes alliage diamantées 17\" à 19\"", "description": "Design bi-ton premium sport"},
    {"category": "Design & Extérieur", "icon": "eye", "name": "Caméra de recul & Vision 360°", "description": "4 caméras avec vue aérienne pour le stationnement"},
    {"category": "Design & Extérieur", "icon": "eye", "name": "Barres de toit modulables & Vitres surteintées", "description": "Style baroudeur et isolation thermique"},
]

DEALERSHIPS_SEED = [
    {
        "name": "Renault Commerce Maroc (RCM)",
        "slug": "renault-commerce-maroc",
        "website": "https://www.renault.ma",
        "headquarters_city": "Casablanca",
        "showrooms": [
            {"name": "Succursale Ain Sebaa", "city": "Casablanca", "address": "Km 10, Route de Rabat, Ain Sebaa", "phone": "+212522668800", "lat": 33.6012, "lon": -7.5341, "brands": ["Renault", "Dacia"]},
            {"name": "Succursale Bd Zerktouni", "city": "Casablanca", "address": "44 Bd Zerktouni", "phone": "+212522223344", "lat": 33.5891, "lon": -7.6321, "brands": ["Renault", "Dacia"]},
            {"name": "Showroom Hay Riad", "city": "Rabat", "address": "Avenue Annakhil, Hay Riad", "phone": "+212537718000", "lat": 33.9682, "lon": -6.8791, "brands": ["Renault", "Dacia"]},
            {"name": "Showroom Tanger Med", "city": "Tanger", "address": "Zone Franche TFZ, Route de Rabat", "phone": "+212539393000", "lat": 35.7594, "lon": -5.8339, "brands": ["Renault", "Dacia"]},
            {"name": "Showroom Marrakech Guéliz", "city": "Marrakech", "address": "Boulevard Abdelkrim Al Khattabi", "phone": "+212524430000", "lat": 31.6441, "lon": -8.0125, "brands": ["Renault", "Dacia"]},
        ]
    },
    {
        "name": "Auto Hall",
        "slug": "auto-hall",
        "website": "https://www.autohall.ma",
        "headquarters_city": "Casablanca",
        "showrooms": [
            {"name": "Auto Hall Siège Lissasfa", "city": "Casablanca", "address": "Km 12, Route d'El Jadida, Lissasfa", "phone": "+212522678000", "lat": 33.5321, "lon": -7.6890, "brands": ["Peugeot", "Citroën", "Opel", "Nissan", "Ford"]},
            {"name": "Auto Hall Rabat", "city": "Rabat", "address": "Avenue Hassan II, Route de Casablanca", "phone": "+212537699000", "lat": 33.9921, "lon": -6.8450, "brands": ["Peugeot", "Citroën", "Nissan"]},
            {"name": "Auto Hall Agadir", "city": "Agadir", "address": "Zone Industrielle Tassila", "phone": "+212528330000", "lat": 30.3950, "lon": -9.5420, "brands": ["Peugeot", "Citroën", "Nissan", "Ford"]},
        ]
    },
    {
        "name": "Global Engines (Hyundai Maroc)",
        "slug": "global-engines-hyundai",
        "website": "https://www.hyundai.ma",
        "headquarters_city": "Casablanca",
        "showrooms": [
            {"name": "Hyundai Showroom Corniche", "city": "Casablanca", "address": "Boulevard de la Corniche, Ain Diab", "phone": "+212522799999", "lat": 33.5950, "lon": -7.6680, "brands": ["Hyundai"]},
            {"name": "Hyundai Sidi Maarouf", "city": "Casablanca", "address": "Boulevard Abou Bakr El Kadiri, Sidi Maarouf", "phone": "+212522970000", "lat": 33.5350, "lon": -7.6400, "brands": ["Hyundai"]},
            {"name": "Hyundai Rabat Souissi", "city": "Rabat", "address": "Avenue Mohammed VI, Souissi", "phone": "+212537750000", "lat": 33.9720, "lon": -6.8290, "brands": ["Hyundai"]},
        ]
    },
    {
        "name": "Toyota du Maroc",
        "slug": "toyota-du-maroc",
        "website": "https://www.toyota.ma",
        "headquarters_city": "Casablanca",
        "showrooms": [
            {"name": "Toyota Showroom Sidi Maarouf", "city": "Casablanca", "address": "Parc d'Activité Sidi Maarouf", "phone": "+212522588888", "lat": 33.5380, "lon": -7.6450, "brands": ["Toyota"]},
            {"name": "Toyota Rabat Agdal", "city": "Rabat", "address": "Avenue de France, Agdal", "phone": "+212537770000", "lat": 33.9980, "lon": -6.8520, "brands": ["Toyota"]},
        ]
    },
    {
        "name": "Centrale Automobile Chérifienne (CAC)",
        "slug": "cac-volkswagen",
        "website": "https://www.volkswagen.ma",
        "headquarters_city": "Casablanca",
        "showrooms": [
            {"name": "CAC Showroom Ain Sebaa", "city": "Casablanca", "address": "66 Boulevard Moulay Slimane, Ain Sebaa", "phone": "+212522677700", "lat": 33.6030, "lon": -7.5410, "brands": ["Volkswagen", "Audi", "Skoda", "Porsche"]},
            {"name": "CAC Rabat", "city": "Rabat", "address": "Avenue Allal Ben Abdellah", "phone": "+212537200000", "lat": 34.0150, "lon": -6.8350, "brands": ["Volkswagen", "Audi", "Skoda"]},
        ]
    }
]


async def seed_new_cars_database():
    print("[+] Initializing 100% New Car Moroccan Digital Showroom Seed...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # 1. Seed Equipment Categories & Features
        print("[+] Seeding Equipment Categories & Features...")
        cat_cache = {}
        feat_cache = {}

        for item in STANDARD_EQUIPMENT_FEATURES:
            cat_name = item["category"]
            cat_slug = slugify(cat_name)
            
            if cat_slug not in cat_cache:
                stmt = select(EquipmentCategory).where(EquipmentCategory.slug == cat_slug)
                res = await session.execute(stmt)
                cat = res.scalar_one_or_none()
                if not cat:
                    cat = EquipmentCategory(
                        name=cat_name,
                        slug=cat_slug,
                        icon=item["icon"],
                        display_order=len(cat_cache)
                    )
                    session.add(cat)
                    await session.flush()
                cat_cache[cat_slug] = cat

            feat_slug = slugify(item["name"])
            stmt_f = select(EquipmentFeature).where(EquipmentFeature.slug == feat_slug)
            res_f = await session.execute(stmt_f)
            feat = res_f.scalar_one_or_none()
            if not feat:
                feat = EquipmentFeature(
                    category_id=cat_cache[cat_slug].id,
                    name=item["name"],
                    slug=feat_slug,
                    description=item.get("description")
                )
                session.add(feat)
                await session.flush()
            feat_cache[feat_slug] = feat

        # 2. Seed Dealerships & Showrooms
        print("[+] Seeding Dealerships & Official Moroccan Showrooms...")
        for dealer_data in DEALERSHIPS_SEED:
            stmt_d = select(Dealership).where(Dealership.slug == dealer_data["slug"])
            res_d = await session.execute(stmt_d)
            dealer = res_d.scalar_one_or_none()
            if not dealer:
                dealer = Dealership(
                    name=dealer_data["name"],
                    slug=dealer_data["slug"],
                    website=dealer_data.get("website"),
                    headquarters_city=dealer_data.get("headquarters_city", "Casablanca")
                )
                session.add(dealer)
                await session.flush()

            for s_data in dealer_data["showrooms"]:
                stmt_s = select(Showroom).where(
                    Showroom.dealership_id == dealer.id,
                    Showroom.name == s_data["name"]
                )
                res_s = await session.execute(stmt_s)
                showroom = res_s.scalar_one_or_none()
                if not showroom:
                    showroom = Showroom(
                        dealership_id=dealer.id,
                        name=s_data["name"],
                        city=s_data["city"],
                        address=s_data["address"],
                        phone=s_data.get("phone"),
                        latitude=s_data.get("lat"),
                        longitude=s_data.get("lon"),
                        brand_affiliations=s_data.get("brands", [])
                    )
                    session.add(showroom)

        # 3. Seed 4-Tier New Car Catalog Hierarchy
        print("[+] Seeding 4-tier Catalog (Brands, Models, Powertrains, Trims)...")
        all_features = list(feat_cache.values())

        for b_data in NEW_CARS_DATA:
            b_slug = slugify(b_data["brand"])
            stmt_b = select(BrandCatalog).where(BrandCatalog.slug == b_slug)
            res_b = await session.execute(stmt_b)
            brand = res_b.scalar_one_or_none()
            if not brand:
                brand = BrandCatalog(
                    name=b_data["brand"],
                    slug=b_slug,
                    logo_url=b_data["logo"],
                    country_of_origin=b_data.get("origin")
                )
                session.add(brand)
                await session.flush()

            for m_data in b_data["models"]:
                m_slug = slugify(m_data["name"])
                stmt_m = select(ModelCatalog).where(
                    ModelCatalog.brand_id == brand.id,
                    ModelCatalog.slug == m_slug
                )
                res_m = await session.execute(stmt_m)
                model = res_m.scalar_one_or_none()
                if not model:
                    model = ModelCatalog(
                        brand_id=brand.id,
                        name=m_data["name"],
                        slug=m_slug,
                        body_type=m_data["body_type"],
                        year_start=m_data.get("year_start", 2024),
                        hero_image_url=m_data.get("image")
                    )
                    session.add(model)
                    await session.flush()

                for p_data in m_data["powertrains"]:
                    stmt_p = select(PowertrainCatalog).where(
                        PowertrainCatalog.model_id == model.id,
                        PowertrainCatalog.name == p_data["name"]
                    )
                    res_p = await session.execute(stmt_p)
                    pt = res_p.scalar_one_or_none()
                    if not pt:
                        pt = PowertrainCatalog(
                            model_id=model.id,
                            name=p_data["name"],
                            fuel_type=p_data["fuel_type"],
                            fiscal_power_cv=p_data["fiscal_power_cv"],
                            engine_power_hp=p_data.get("engine_power_hp"),
                            torque_nm=p_data.get("torque_nm"),
                            transmission=p_data["transmission"],
                            consumption_l_100=p_data.get("consumption_l_100"),
                            co2_emissions_g_km=p_data.get("co2")
                        )
                        session.add(pt)
                        await session.flush()

                    for t_data in p_data["trims"]:
                        t_slug = slugify(f"{m_slug}-{t_data['name']}")
                        stmt_t = select(TrimCatalog).where(
                            TrimCatalog.model_id == model.id,
                            TrimCatalog.slug == t_slug
                        )
                        res_t = await session.execute(stmt_t)
                        trim = res_t.scalar_one_or_none()
                        if not trim:
                            trim = TrimCatalog(
                                model_id=model.id,
                                powertrain_id=pt.id,
                                name=t_data["name"],
                                slug=t_slug,
                                price_new_mad=t_data["price"],
                                promo_price_mad=t_data.get("promo"),
                                is_promo=bool(t_data.get("promo")),
                                warranty_years=3 if "Dacia" in b_data["brand"] or "Renault" in b_data["brand"] else 5,
                                warranty_km=100000,
                                trunk_capacity_l=t_data.get("trunk", 380),
                                euro_ncap_stars=t_data.get("stars", 4),
                                image_url=m_data.get("image"),
                                available_colors=[
                                    {"name": "Blanc Glacier", "hex": "#F4F4F4", "price_mad": 0},
                                    {"name": "Gris Schiste", "hex": "#4A4F55", "price_mad": 3500},
                                    {"name": "Noir Nacré", "hex": "#1A1A1A", "price_mad": 4000},
                                    {"name": "Bleu Iron", "hex": "#1B3B6F", "price_mad": 4500},
                                ],
                                is_available_in_morocco=True
                            )
                            session.add(trim)
                            await session.flush()

                            # Map equipment features based on trim hierarchy (GT / Extreme / Prestige gets more standard features)
                            is_top_trim = any(w in t_data["name"].lower() for w in ["extreme", "journey", "gt", "prestige", "luxe", "lounge", "r-line", "esprit"])
                            
                            for idx, feat in enumerate(all_features):
                                if idx < 8 or is_top_trim:
                                    status = "SERIE"
                                    opt_price = 0
                                elif idx < 14:
                                    status = "OPTION"
                                    opt_price = 4500.0
                                else:
                                    status = "NON_DISPO"
                                    opt_price = 0

                                map_obj = TrimEquipmentMapping(
                                    trim_id=trim.id,
                                    feature_id=feat.id,
                                    status=status,
                                    option_price_mad=opt_price
                                )
                                session.add(map_obj)

        await session.commit()
        print("[SUCCESS] Moroccan Digital Showroom Catalog & Dealerships seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_new_cars_database())
