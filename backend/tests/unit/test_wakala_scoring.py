# tests/unit/test_wakala_scoring.py — Tests unitaires complets du système de notation et classement Wakala.
from app.ml.scoring.criteria_ranker import CriteriaRanker, criteria_ranker

from app.ml.scoring.wakala_scorer import WakalaScorer, wakala_scorer
from app.ml.scoring.top3_aggregator import Top3Aggregator, top3_aggregator


class MockVehicle:
    def __init__(self, id, brand, model, version, price, year, trunk_capacity_l, seats, body_type, fuel_type, engine_power_hp, consumption_l_100=5.0, transmission="automatique", description="Pack Sécurité 6 airbags climatisation carplay camera recul"):
        self.id = id
        self.brand = brand
        self.model = model
        self.version = version
        self.price = price
        self.year = year
        self.trunk_capacity_l = trunk_capacity_l
        self.seats = seats
        self.body_type = body_type
        self.fuel_type = fuel_type
        self.engine_power_hp = engine_power_hp
        self.consumption_l_100 = consumption_l_100
        self.transmission = transmission
        self.description = description
        self.equipment_list = {}
        self.images = []


def test_criteria_ranker_honesty_rule():
    """Vérifie que fiabilite et design restent None (Règle d'honnêteté)."""
    v = MockVehicle(
        id="1", brand="Dacia", model="Duster", version="Prestige",
        price=180000, year=2022, trunk_capacity_l=478, seats=5,
        body_type="suv", fuel_type="diesel", engine_power_hp=115, consumption_l_100=4.9
    )
    scores = criteria_ranker.compute_criteria_scores(v)

    assert scores["fiabilite"] is None
    assert scores["design"] is None
    assert 0 <= scores["espace_coffre"] <= 100
    assert 0 <= scores["economie_usage"] <= 100
    assert 0 <= scores["performance"] <= 100
    assert 0 <= scores["securite"] <= 100
    assert 0 <= scores["confort"] <= 100
    assert 0 <= scores["technologie"] <= 100
    assert 0 <= scores["robustesse"] <= 100


def test_criteria_ranker_key_facts():
    """Vérifie l'extraction de faits tangibles chiffrés."""
    v = MockVehicle(
        id="1", brand="Hyundai", model="Tucson", version="Shine",
        price=320000, year=2023, trunk_capacity_l=598, seats=5,
        body_type="suv", fuel_type="hybride", engine_power_hp=230, consumption_l_100=5.6
    )
    scores = criteria_ranker.compute_criteria_scores(v)
    facts = criteria_ranker.extract_key_facts(v, scores)

    assert len(facts) >= 1
    assert any("Coffre" in f or "ch" in f or "Consommation" in f or "Sécurité" in f for f in facts)


def test_wakala_scorer_weight_profiles_and_redistribution():
    """Vérifie le calcul et la redistribution des poids sur les critères disponibles."""
    weights_bebe = wakala_scorer.compute_user_weights(usage="bebe")
    # Vérifie que la somme des poids vaut exactement 1.0
    assert abs(sum(weights_bebe.values()) - 1.0) < 1e-5
    # La sécurité et l'espace doivent être prépondérants pour bébé
    assert weights_bebe["securite"] > weights_bebe["performance"]
    assert weights_bebe["espace_coffre"] > weights_bebe["performance"]

    weights_ville = wakala_scorer.compute_user_weights(usage="urbain")
    assert weights_ville["economie_usage"] > weights_ville["espace_coffre"]


def test_wakala_scorer_budget_tiers():
    """Vérifie la notation de l'adéquation au budget (Ingrédient 2)."""
    budget = 200000.0

    # 1. 80% du budget (zone idéale 70-100%) -> 100/100
    assert wakala_scorer.compute_budget_score(160000.0, budget) == 100.0

    # 2. 60% du budget (50-70%) -> 88/100
    assert wakala_scorer.compute_budget_score(120000.0, budget) == 88.0

    # 3. Dépassement léger (+10%) -> score > 0
    score_over = wakala_scorer.compute_budget_score(220000.0, budget)
    assert 0.0 < score_over < 100.0

    # 4. Dépassement excessif (+35%) -> 0/100
    assert wakala_scorer.compute_budget_score(270000.0, budget) == 0.0


def test_wakala_scorer_practical_penalties():
    """Vérifie les pénalités multiplicatives pratiques."""
    v_coupe_2places = MockVehicle(
        id="2", brand="Mazda", model="MX-5", version="RF",
        price=300000, year=2021, trunk_capacity_l=130, seats=2,
        body_type="coupe", fuel_type="essence", engine_power_hp=184
    )
    # Famille demande un coupé 2 places -> forte pénalité
    score_famille = wakala_scorer.compute_practical_score(v_coupe_2places, usage="famille", places_requises=5)
    assert score_famille <= 50.0


def test_wakala_filter_and_cascade():
    """Vérifie la cascade de relâchement automatique quand < 3 véhicules correspondent."""
    v1 = MockVehicle("1", "Renault", "Clio", "Life", 150000, 2021, 300, 5, "citadine", "essence", 90)
    v2 = MockVehicle("2", "Peugeot", "208", "Allure", 180000, 2022, 311, 5, "citadine", "essence", 100)
    v3 = MockVehicle("3", "Dacia", "Sandero", "Stepway", 140000, 2022, 328, 5, "citadine", "essence", 90)
    v4 = MockVehicle("4", "Hyundai", "Tucson", "Prestige", 340000, 2023, 598, 5, "suv", "diesel", 136)

    vehicles = [v1, v2, v3, v4]

    # Demande stricte : SUV diesel sous 170k MAD -> Aucun résultat strict, doit relâcher la carrosserie ou énergie
    candidates, relaxed = wakala_scorer.filter_and_cascade(
        vehicles=vehicles,
        budget_max=170000,
        body_type="suv",
        fuel_type="diesel"
    )

    assert len(candidates) >= 3
    assert relaxed is not None


def test_top3_aggregator_model_and_brand_diversity():
    """Vérifie qu'un modèle n'apparaît qu'une seule fois (meilleure version) et max 1 voiture par marque."""
    v1_finish_a = MockVehicle("1", "Dacia", "Duster", "Access", 160000, 2022, 478, 5, "suv", "diesel", 95)
    v1_finish_b = MockVehicle("2", "Dacia", "Duster", "Prestige+", 190000, 2022, 478, 5, "suv", "diesel", 115)
    v2_other_dacia = MockVehicle("3", "Dacia", "Sandero", "Stepway", 145000, 2022, 328, 5, "citadine", "essence", 90)
    v3_renault = MockVehicle("4", "Renault", "Captur", "Intens", 210000, 2022, 422, 5, "suv", "essence", 130)
    v4_peugeot = MockVehicle("5", "Peugeot", "2008", "GT", 230000, 2022, 434, 5, "suv", "diesel", 130)

    vehicles_map = {
        "1": v1_finish_a,
        "2": v1_finish_b,
        "3": v2_other_dacia,
        "4": v3_renault,
        "5": v4_peugeot
    }

    scored_list = [
        {"vehicle_id": "1", "final_score": 82.0, "score_breakdown": {}, "key_facts": ["Coffre 478 L"], "budget_margin": 10000},
        {"vehicle_id": "2", "final_score": 89.0, "score_breakdown": {}, "key_facts": ["Coffre 478 L", "115 ch"], "budget_margin": -10000},
        {"vehicle_id": "3", "final_score": 84.0, "score_breakdown": {}, "key_facts": ["Economique"], "budget_margin": 25000},
        {"vehicle_id": "4", "final_score": 86.0, "score_breakdown": {}, "key_facts": ["Moteur 130 ch"], "budget_margin": -20000},
        {"vehicle_id": "5", "final_score": 85.0, "score_breakdown": {}, "key_facts": ["Pack GT"], "budget_margin": -40000},
    ]

    response = top3_aggregator.aggregate_top3(
        scored_vehicles=scored_list,
        vehicles_map=vehicles_map,
        limit=3
    )

    items = response.items
    assert len(items) == 3
    # 1 seule Dacia (la meilleure version : Prestige+ avec score 89.0)
    dacia_items = [item for item in items if item.brand.lower() == "dacia"]
    assert len(dacia_items) == 1
    assert dacia_items[0].vehicle_id == "2"

    # Vérification de la diversité des marques dans le Top 3
    brands = [item.brand.lower() for item in items]
    assert len(set(brands)) == 3
