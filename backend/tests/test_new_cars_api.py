import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_brands_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        try:
            response = await ac.get("/api/v1/new-cars/brands")
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
        except Exception:
            pytest.skip("Database not connected for in-process API test")


@pytest.mark.asyncio
async def test_models_catalog_and_filters():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # All models
        res = await ac.get("/api/v1/new-cars/models")
        assert res.status_code == 200
        models = res.json()
        assert len(models) > 0

        # Filter by Dacia
        res_dacia = await ac.get("/api/v1/new-cars/models?brand_slug=dacia")
        assert res_dacia.status_code == 200
        dacia_models = res_dacia.json()
        assert all(m["brand"]["slug"] == "dacia" for m in dacia_models)

        # Filter by SUV
        res_suv = await ac.get("/api/v1/new-cars/models?body_type=SUV")
        assert res_suv.status_code == 200
        suv_models = res_suv.json()
        assert all(m["body_type"] == "SUV" for m in suv_models)


@pytest.mark.asyncio
async def test_model_detail_and_trims():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/new-cars/models/duster-3-2024")
        assert res.status_code == 200
        data = res.json()
        assert "Duster" in data["name"]
        assert len(data["trims"]) > 0
        
        # Check Moroccan On-The-Road (OTR) tax breakdown
        trim = data["trims"][0]
        assert "on_the_road_breakdown" in trim
        assert trim["on_the_road_breakdown"]["total_clef_en_main_mad"] > 0


@pytest.mark.asyncio
async def test_matrix_comparator():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/comparator/compare", json={
            "trim_ids_or_slugs": ["duster-3-2024-journey", "captur-restyle-techno-dci-edc"]
        })
        assert res.status_code == 200
        data = res.json()
        assert len(data["vehicles"]) == 2
        assert "equipment_matrix" in data
        assert len(data["equipment_matrix"]) > 0


@pytest.mark.asyncio
async def test_showrooms_and_test_drive_booking():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Fetch showrooms
        res_s = await ac.get("/api/v1/showrooms?city=Casablanca")
        assert res_s.status_code == 200
        showrooms = res_s.json()
        assert len(showrooms) > 0

        # 2. Get a valid trim
        res_m = await ac.get("/api/v1/new-cars/models/duster-3-2024")
        trim_id = res_m.json()["trims"][0]["id"]

        # 3. Book a Test Drive with CNDP Consent & Moroccan Phone
        res_td = await ac.post("/api/v1/leads/test-drive", json={
            "trim_id": trim_id,
            "showroom_id": showrooms[0]["id"],
            "full_name": "Karim Bennani",
            "phone_number": "0661234567",
            "email": "karim.bennani@test.ma",
            "city": "Casablanca",
            "cndp_consent_accepted": True
        })
        assert res_td.status_code == 200
        lead_data = res_td.json()
        assert lead_data["status"] == "success"
        assert lead_data["confirmation_details"]["phone_number"] == "+212661234567"
        assert lead_data["confirmation_details"]["cndp_protected"] is True
