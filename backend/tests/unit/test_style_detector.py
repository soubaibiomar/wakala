from app.rag.style_detector import style_detector

def test_style_detector_formal_concise_basic():
    msg = "Bonjour, je cherche une voiture."
    res = style_detector.detect_style(msg)
    assert res["formality"] == "formal"
    assert res["verbosity"] == "concise"
    assert res["technicality"] == "basic"

def test_style_detector_casual_detailed_technical():
    msg = (
        "je veux un suv avec une boite automatique et un faible kilométrage. "
        "il me faut beaucoup de puissance, au moins 150 ch. "
        "que me conseilles tu pour la ville ?"
    )
    res = style_detector.detect_style(msg)
    assert res["formality"] == "casual"
    assert res["verbosity"] == "detailed"
    assert res["technicality"] == "technical"

def test_style_detector_no_hidden_info():
    # Verify it doesn't return anything else than the 3 keys
    msg = "yo frere j'ai 30 ans je veux une m3 e46"
    res = style_detector.detect_style(msg)
    assert set(res.keys()) == {"formality", "verbosity", "technicality"}
    assert res["formality"] == "casual"
    assert res["technicality"] == "basic" # doesn't know e46
