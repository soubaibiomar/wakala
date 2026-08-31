import time
from typing import Optional


MAX_HISTORY_TURNS = 6
SESSION_TTL_SECONDS = 7200  # 2 heures d'inactivité avant expiration
MAX_SESSIONS = 5000         # Plafond anti-saturation RAM


class BaseConversationMemory:
    def get_history(self, session_id: str) -> list[dict]:
        raise NotImplementedError

    def add_turn(self, session_id: str, user_message: str, assistant_reply: str) -> None:
        raise NotImplementedError

    def clear(self, session_id: str) -> None:
        raise NotImplementedError


class InMemoryConversationMemory(BaseConversationMemory):
    def __init__(self):
        self._sessions: dict[str, list[dict]] = {}
        self._timestamps: dict[str, float] = {}

    def _cleanup_expired(self) -> None:
        """Nettoie les sessions expirées pour libérer la mémoire."""
        now = time.time()
        expired_keys = [
            sid for sid, last_active in self._timestamps.items()
            if now - last_active > SESSION_TTL_SECONDS
        ]
        for sid in expired_keys:
            self._sessions.pop(sid, None)
            self._timestamps.pop(sid, None)

        # Si le plafond est toujours dépassé, évincer les plus anciennes
        if len(self._sessions) > MAX_SESSIONS:
            sorted_by_age = sorted(self._timestamps.items(), key=lambda x: x[1])
            excess_count = len(self._sessions) - MAX_SESSIONS
            for sid, _ in sorted_by_age[:excess_count]:
                self._sessions.pop(sid, None)
                self._timestamps.pop(sid, None)

    def get_history(self, session_id: str) -> list[dict]:
        now = time.time()
        last_active = self._timestamps.get(session_id)
        if last_active and (now - last_active > SESSION_TTL_SECONDS):
            self.clear(session_id)
            return []
        
        if session_id in self._timestamps:
            self._timestamps[session_id] = now
        return self._sessions.get(session_id, [])

    def add_turn(self, session_id: str, user_message: str, assistant_reply: str) -> None:
        now = time.time()
        if len(self._sessions) >= MAX_SESSIONS:
            self._cleanup_expired()

        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._timestamps[session_id] = now
        self._sessions[session_id].append({
            "role": "user",
            "content": user_message,
        })
        self._sessions[session_id].append({
            "role": "assistant",
            "content": assistant_reply,
        })
        if len(self._sessions[session_id]) > MAX_HISTORY_TURNS * 2:
            self._sessions[session_id] = self._sessions[session_id][-(MAX_HISTORY_TURNS * 2):]

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        self._timestamps.pop(session_id, None)

    def get_last_user_message(self, session_id: str) -> Optional[str]:
        history = self.get_history(session_id)
        for entry in reversed(history):
            if entry["role"] == "user":
                return entry["content"]
        return None


conversation_memory = InMemoryConversationMemory()
