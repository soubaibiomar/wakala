from functools import lru_cache

from app.ml.graph.graph_service import VehicleGraphService


@lru_cache(maxsize=1)
def get_graph_service() -> VehicleGraphService:
    return VehicleGraphService()


async def enrich_with_graph(
    vehicle_ids: list[str],
    limit: int = 3,
) -> dict[str, dict]:
    if not vehicle_ids:
        return {}

    graph_service = get_graph_service()
    enriched: dict[str, dict] = {}

    for vid in vehicle_ids[:5]:
        similar = await graph_service.get_similar_vehicles(vid, limit=limit)
        enriched[vid] = {
            "similar_vehicles": [
                {
                    "id": s["id"],
                    "title": s.get("title", ""),
                    "popularity_score": s.get("score", 0),
                }
                for s in similar
            ],
        }

    return enriched


async def get_popularity_scores(
    vehicle_ids: list[str],
) -> dict[str, float]:
    if not vehicle_ids:
        return {}

    graph_service = get_graph_service()
    scores: dict[str, float] = {}
    async with graph_service.driver.session() as session:
        for vid in vehicle_ids:
            result = await session.run(
                """
                MATCH (v:Vehicle {id: $vid})
                RETURN v.popularity_score AS score
                """,
                vid=vid,
            )
            row = await result.single()
            scores[vid] = row["score"] if row and row["score"] is not None else 0.0

    return scores
