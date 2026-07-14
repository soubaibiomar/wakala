from functools import lru_cache
from typing import Optional

import numpy as np
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession


IMPLICIT_WEIGHTS = {
    "view": 0.1,
    "click": 0.2,
    "favorite": 0.5,
    "unfavorite": -0.3,
    "contact": 0.8,
    "share": 0.3,
    "recommendation_click": 0.6,
}

COLD_START_THRESHOLD = 3


async def get_user_interactions(
    db: AsyncSession,
    user_id: str,
    min_interactions: int = COLD_START_THRESHOLD,
) -> tuple[Optional[np.ndarray], Optional[list[str]], Optional[dict[str, float]]]:
    query = text("""
        SELECT
            vehicle_id,
            action,
            COUNT(*) AS action_count
        FROM interactions
        WHERE user_id = :user_id
        GROUP BY vehicle_id, action
        ORDER BY vehicle_id
    """)
    result = await db.execute(query, {"user_id": user_id})
    rows = result.fetchall()

    if not rows:
        return None, None, None

    vehicle_scores: dict[str, float] = {}
    user_actions: dict[str, dict[str, int]] = {}

    for row in rows:
        v_id = str(row[0])
        action = row[1]
        count = row[2]
        weight = IMPLICIT_WEIGHTS.get(action, 0)
        vehicle_scores[v_id] = vehicle_scores.get(v_id, 0) + weight * count

        if v_id not in user_actions:
            user_actions[v_id] = {}
        user_actions[v_id][action] = count

    if len(vehicle_scores) < min_interactions:
        return None, None, vehicle_scores

    vehicle_ids = list(vehicle_scores.keys())
    score_array = np.array([vehicle_scores[v] for v in vehicle_ids], dtype=np.float32)
    score_min, score_max = score_array.min(), score_array.max()
    if score_max > score_min:
        score_array = (score_array - score_min) / (score_max - score_min)
    else:
        score_array = np.ones_like(score_array)

    return score_array, vehicle_ids, vehicle_scores


async def get_similar_users(
    db: AsyncSession,
    user_id: str,
    limit: int = 20,
) -> list[str]:
    query = text("""
        WITH user_vehicles AS (
            SELECT DISTINCT vehicle_id
            FROM interactions
            WHERE user_id = :user_id AND action IN ('favorite', 'contact', 'recommendation_click')
        ),
        similar_users AS (
            SELECT i.user_id, COUNT(DISTINCT i.vehicle_id) AS common_vehicles
            FROM interactions i
            JOIN user_vehicles uv ON i.vehicle_id = uv.vehicle_id
            WHERE i.user_id != :user_id
              AND i.action IN ('favorite', 'contact', 'recommendation_click')
            GROUP BY i.user_id
            ORDER BY common_vehicles DESC
            LIMIT :limit
        )
        SELECT user_id FROM similar_users
    """)
    result = await db.execute(query, {"user_id": user_id, "limit": limit})
    return [str(row[0]) for row in result.fetchall()]


async def compute_collaborative_scores(
    db: AsyncSession,
    target_user_id: str,
    all_vehicle_ids: list[str],
) -> tuple[list[dict], bool]:
    cold_start = False

    scores_array, interacted_ids, raw_scores = await get_user_interactions(
        db, target_user_id
    )

    if scores_array is None:
        cold_start = True
        return _cold_start_result(all_vehicle_ids), cold_start

    interacted_set = set(interacted_ids) if interacted_ids else set()
    vehicle_id_to_idx = {vid: i for i, vid in enumerate(all_vehicle_ids)}

    base_scores = np.zeros(len(all_vehicle_ids), dtype=np.float32)
    if interacted_ids and scores_array is not None:
        for vid, score in zip(interacted_ids, scores_array):
            if vid in vehicle_id_to_idx:
                base_scores[vehicle_id_to_idx[vid]] = score

    similar_users = await get_similar_users(db, target_user_id)
    if similar_users:
        neighbor_scores = await _aggregate_neighbor_scores(
            db, similar_users, all_vehicle_ids, vehicle_id_to_idx
        )
        alpha = min(0.5, len(similar_users) / (len(similar_users) + 5))
        base_scores = (1 - alpha) * base_scores + alpha * neighbor_scores

    if base_scores.max() > 0:
        base_scores = base_scores / base_scores.max()

    results = []
    for i, vid in enumerate(all_vehicle_ids):
        results.append({
            "vehicle_id": vid,
            "collaborative_score": float(base_scores[i]),
        })

    return results, cold_start


async def _aggregate_neighbor_scores(
    db: AsyncSession,
    similar_users: list[str],
    all_vehicle_ids: list[str],
    vehicle_id_to_idx: dict[str, int],
) -> np.ndarray:
    scores = np.zeros(len(all_vehicle_ids), dtype=np.float32)
    if not similar_users:
        return scores

    placeholders = ", ".join(f"'{uid}'" for uid in similar_users)
    query = text(f"""
        SELECT vehicle_id, SUM(
            CASE
                WHEN action = 'favorite' THEN 0.5
                WHEN action = 'contact' THEN 0.8
                WHEN action = 'recommendation_click' THEN 0.6
                WHEN action = 'view' THEN 0.1
                WHEN action = 'click' THEN 0.2
                ELSE 0
            END
        ) AS similarity_score
        FROM interactions
        WHERE user_id IN ({placeholders})
        GROUP BY vehicle_id
        ORDER BY similarity_score DESC
    """)
    result = await db.execute(query)
    for row in result.fetchall():
        vid = str(row[0])
        score = float(row[1])
        if vid in vehicle_id_to_idx:
            scores[vehicle_id_to_idx[vid]] += score

    if scores.max() > 0:
        scores = scores / scores.max()

    return scores


def _cold_start_result(all_vehicle_ids: list[str]) -> list[dict]:
    return [
        {"vehicle_id": vid, "collaborative_score": 0.0}
        for vid in all_vehicle_ids
    ]
