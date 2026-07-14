from typing import Any, Optional

try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:  # Allows retrieval/no-match routes and unit tests to run in a slim environment.
    ChatGroq = Any
    LANGCHAIN_AVAILABLE = False

    class SystemMessage:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class HumanMessage(SystemMessage):  # type: ignore[no-redef]
        pass

    class ChatPromptTemplate:  # type: ignore[no-redef]
        @classmethod
        def from_messages(cls, messages: list[Any]) -> "ChatPromptTemplate":
            instance = cls()
            instance.messages = messages
            return instance

        def format_messages(self) -> list[Any]:
            return self.messages

from app.core.config import settings
from app.rag.vector_search import search_reviews, search_vehicles
from app.rag.graph_context import enrich_with_graph, get_popularity_scores
from app.rag.conversation_memory import conversation_memory
from app.rag.schemas import ChatResponse, SourceReference


SYSTEM_PROMPT = """Tu es AutoMind, l'assistant intelligent de la marketplace automobile.
Tu aides les utilisateurs a trouver le vehicule ideal au Maroc.

CONTEXTE VEHICULES DISPONIBLES :
{vehicle_context}

CONTEXTE GRAPHE (vehicules similaires et popularite) :
{graph_context}

AVIS CLIENTS PERTINENTS :
{review_context}

HISTORIQUE DE LA CONVERSATION :
{conversation_history}

REGLES STRICTES :
1. Base TOUJOURS tes reponses sur les vehicules listes dans le contexte.
2. Ne invente JAMAIS un vehicule, un prix ou une specification qui n'est pas dans le contexte.
3. Si le contexte ne contient pas la reponse, reponds exactement : "Je n'ai pas trouve de vehicule correspondant dans le catalogue actuel."
4. Cite les prix, annees, kilometres et villes exacts du contexte.
5. Mentionne la popularite (score de confiance) quand elle est disponible.
6. Propose 2-3 alternatives pertinentes si possible.
7. Reponds en francais, de maniere concise et professionnelle.
8. Utilise l'historique pour comprendre les references (ex: "et en diesel ?")."""

NO_MATCH_REPLY = "Je n'ai pas trouve de vehicule correspondant dans le catalogue actuel."


def _format_vehicle_context(vehicles: list[dict]) -> str:
    if not vehicles:
        return "Aucun vehicule trouve dans le catalogue."
    lines = []
    for i, v in enumerate(vehicles, 1):
        meta = v.get("metadata", {})
        title = f"{meta.get('brand', '')} {meta.get('model', '')} ({meta.get('year', '')})"
        price = meta.get("price", "N/A")
        mileage = meta.get("mileage", "N/A")
        fuel = meta.get("fuel_type", "N/A")
        body = meta.get("body_type", "N/A")
        city = meta.get("city", "N/A")
        desc = meta.get("description", "")

        line = (
            f"{i}. {title}\n"
            f"   Prix: {price} MAD | Kilometrage: {mileage} km\n"
            f"   Carburant: {fuel} | Carrosserie: {body}\n"
            f"   Ville: {city} | Score similarite: {v.get('score', 0):.2f}\n"
        )
        if desc:
            line += f"   Description: {desc}\n"
        lines.append(line)
    return "\n".join(lines)


def _format_graph_context(enriched: dict[str, dict], popularity: dict[str, float]) -> str:
    if not enriched:
        return "Aucune donnee graphe disponible."
    lines = []
    for vid, data in enriched.items():
        pop = popularity.get(vid, 0)
        lines.append(f"Vehicule {vid}: popularite_score={pop:.4f}")
        similar = data.get("similar_vehicles", [])
        if similar:
            sim_titles = [s.get("title", s["id"]) for s in similar[:3]]
            lines.append(f"  Vehicules similaires: {', '.join(sim_titles)}")
    return "\n".join(lines) if lines else "Aucune donnee graphe disponible."


def _format_review_context(reviews: list[dict]) -> str:
    if not reviews:
        return "Aucun avis pertinent."
    lines = []
    for r in reviews:
        text = r.get("text", "")[:200]
        lines.append(f"- (Note: {r.get('rating', 'N/A')}/5) {text}...")
    return "\n".join(lines)


def _format_history(history: list[dict]) -> str:
    if not history:
        return "Aucun echange precedent."
    lines = []
    for entry in history[-4:]:
        role = "Utilisateur" if entry["role"] == "user" else "AutoMind"
        content = entry["content"][:300]
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _retrieval_query(message: str, history: list[dict]) -> str:
    """Keep short follow-up questions tied to the user's previous criterion."""
    previous_user_messages = [entry["content"] for entry in history if entry["role"] == "user"]
    if not previous_user_messages:
        return message

    normalized = message.strip().lower()
    is_follow_up = len(normalized.split()) <= 6 or normalized.startswith(("et ", "ceux", "celle", "lequel", "laquelle"))
    if is_follow_up:
        return f"{previous_user_messages[-1]}\n{message}"
    return message


class ChatbotChain:
    def __init__(self):
        self._llm: Optional[Any] = None

    def _get_llm(self) -> Any:
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain/Groq n'est pas installe")
        if self._llm is None:
            self._llm = ChatGroq(
                api_key=settings.groq_api_key,
                model=settings.GROQ_MODEL,
                temperature=0.3,
                max_tokens=600,
            )
        return self._llm

    async def answer(
        self,
        message: str,
        session_id: str,
    ) -> ChatResponse:
        history = conversation_memory.get_history(session_id)

        # The caps here are intentional: never send an unbounded catalogue to the LLM.
        query = _retrieval_query(message, history)
        vehicles = search_vehicles(query, limit=5)[:5]
        reviews = search_reviews(query, limit=3)[:3]

        # Do not let the model turn an empty (or insufficient) retrieval into a guess.
        if not vehicles:
            conversation_memory.add_turn(session_id, message, NO_MATCH_REPLY)
            return ChatResponse(reply=NO_MATCH_REPLY, sources=[], session_id=session_id)

        vehicle_ids = [v["vehicle_id"] for v in vehicles if v.get("vehicle_id")]
        try:
            enriched = await enrich_with_graph(vehicle_ids, limit=3)
            popularity = await get_popularity_scores(vehicle_ids)
        except Exception:
            # Neo4j enrichment is useful but must not make grounded Qdrant answers unavailable.
            enriched, popularity = {}, {}

        vehicle_context = _format_vehicle_context(vehicles)
        graph_context = _format_graph_context(enriched, popularity)
        review_context = _format_review_context(reviews)
        conversation_history = _format_history(history)

        system_message = SYSTEM_PROMPT.format(
            vehicle_context=vehicle_context,
            graph_context=graph_context,
            review_context=review_context,
            conversation_history=conversation_history,
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            HumanMessage(content=message),
        ])

        try:
            llm = self._get_llm()
            response = await llm.ainvoke(prompt.format_messages())

            reply = response.content
        except Exception:
            reply = (
                "Desole, je rencontre une difficulte technique. "
                "Veuillez reformuler votre question ou reessayer."
            )

        sources = [
            SourceReference(
                vehicle_id=v["vehicle_id"],
                vehicle_title=v.get("metadata", {}).get("brand", "")
                + " " + v.get("metadata", {}).get("model", ""),
                relevance_score=v.get("score", 0),
                source_type="vector_search",
            )
            for v in vehicles[:5]
            if v.get("vehicle_id")
        ]

        conversation_memory.add_turn(session_id, message, reply)

        return ChatResponse(
            reply=reply,
            sources=sources,
            session_id=session_id,
        )


chatbot_chain = ChatbotChain()
