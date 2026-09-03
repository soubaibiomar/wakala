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

    if graph_service.driver is None:
        return {vid: {"similar_vehicles": []} for vid in vehicle_ids[:5]}

    # Batch query: fetch similar vehicles for all IDs in a single Cypher call
    try:
        async with graph_service.driver.session() as session:
            result = await session.run(
                """
                UNWIND $vids AS vid
                MATCH (v:Vehicle {id: vid})
                OPTIONAL MATCH (v)-[r:SIMILAR_TO]-(other:Vehicle)
                WITH vid, other, r
                ORDER BY r.score DESC
                WITH vid, collect({
                    id: other.id,
                    title: coalesce(other.brand, '') + ' ' + coalesce(other.model, ''),
                    score: coalesce(r.score, 0)
                })[0..$limit] AS similar
                RETURN vid, similar
                """,
                vids=vehicle_ids[:5],
                limit=limit,
            )
            async for record in result:
                vid = record["vid"]
                similar_raw = record["similar"]
                enriched[vid] = {
                    "similar_vehicles": [
                        {
                            "id": s["id"],
                            "title": s["title"],
                            "popularity_score": s["score"],
                        }
                        for s in similar_raw
                        if s.get("id") is not None
                    ],
                }
    except Exception:
        # Graceful fallback: return empty enrichment if Neo4j is unavailable
        for vid in vehicle_ids[:5]:
            enriched[vid] = {"similar_vehicles": []}

    return enriched


async def get_popularity_scores(
    vehicle_ids: list[str],
) -> dict[str, float]:
    if not vehicle_ids:
        return {}

    graph_service = get_graph_service()
    scores: dict[str, float] = {}

    if graph_service.driver is None:
        return {vid: 0.0 for vid in vehicle_ids}

    # Batch query: fetch all popularity scores in a single Cypher call
    try:
        async with graph_service.driver.session() as session:
            result = await session.run(
                """
                UNWIND $vids AS vid
                MATCH (v:Vehicle {id: vid})
                RETURN vid, coalesce(v.popularity_score, 0.0) AS score
                """,
                vids=vehicle_ids,
            )
            async for record in result:
                scores[record["vid"]] = record["score"]
    except Exception:
        pass

    # Fill missing IDs with 0.0
    for vid in vehicle_ids:
        if vid not in scores:
            scores[vid] = 0.0

    return scores
