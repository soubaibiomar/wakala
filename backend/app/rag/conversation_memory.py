from typing import Optional


MAX_HISTORY_TURNS = 6


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

    def get_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    def add_turn(self, session_id: str, user_message: str, assistant_reply: str) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []
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

    def get_last_user_message(self, session_id: str) -> Optional[str]:
        history = self._sessions.get(session_id, [])
        for entry in reversed(history):
            if entry["role"] == "user":
                return entry["content"]
        return None


conversation_memory = InMemoryConversationMemory()
