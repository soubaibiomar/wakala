from typing import Any, Optional

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:  # Allows retrieval/no-match routes and unit tests to run in a slim environment.
    class ChatOpenAI:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
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
from app.rag.style_detector import style_detector


SYSTEM_PROMPT = """Tu es Wakala, l'assistant expert et empathique de la marketplace automobile Wakala au Maroc.
CRITIQUE ET IMPÉRATIF : Tu DOIS répondre EXACTEMENT dans la langue ET le dialecte utilisés par l'utilisateur. 
LANGUE DÉTECTÉE DE L'UTILISATEUR : {detected_language}
INSTRUCTION DE LANGUE : Ta réponse doit être ENTIÈREMENT en {detected_language}. Ne traduis pas les noms propres (marques, modèles).
- Si Darija (arabe marocain avec alphabet latin), utilise le vocabulaire marocain (bzaf, chhal, tomobila, mzyan...).
- Si Arabe, réponds en Arabe standard ou marocain avec alphabet arabe.
- Si Anglais, réponds en Anglais.
- Si Français, réponds en Français.
Tu es un expert automobile : tu expliques les avantages/inconvénients (consommation, coût, revente).
Tes connaissances sont limitées aux données fournies. Tu n'inventes JAMAIS de véhicules. Si Aucun vehicule n'est pertinent, dis le dans la bonne langue.
Tu exprimes les prix en MAD.
Si l'utilisateur est vague, pose une question pertinente sur son budget ou son usage dans SA langue ({detected_language}).
DIRECTIVE LOI 09-08 : Tu ne dois JAMAIS demander, stocker ou exposer des données personnelles sensibles.
OBLIGATION DE FORMATAGE : Sois EXTRÊMEMENT CONCIS. Formate les véhicules sous forme de liste à puces courte en Markdown. Évite le blabla pour répondre plus vite.

CONTEXTE VEHICULES DISPONIBLES :
{vehicle_context}

CONTEXTE GRAPHE (vehicules similaires et popularite) :
{graph_context}

AVIS CLIENTS PERTINENTS :
{review_context}

HISTORIQUE DE LA CONVERSATION :
{conversation_history}

DIRECTIVES DE STYLE :
{style_instructions}
"""

def _detect_language(message: str) -> str:
    text_lower = message.lower()
    if any(char in message for char in "أبتثجحخدذرزسشصضطظعغفقكلمنهوي"):
        return "arabe (avec alphabet arabe)"
    elif any(w in text_lower for w in ["bghit", "dyal", "mdina", "tomobila", "chhal", "ma3ndich", "flous", "rkhis", "mzyan", "wach"]):
        return "darija (arabe marocain avec alphabet latin / arabizi)"
    elif any(w in text_lower for w in ["car", "need", "cheap", "looking", "budget is", "commute", "family"]):
        return "anglais"
    else:
        return "français"

def _get_no_match_reply(lang: str) -> str:
    if "arabe" in lang:
        return "عذراً، لم أجد أي سيارة مطابقة في الكتالوج الحالي."
    elif "darija" in lang:
        return "Smeh lia, malqitch chi tomobila katnasb talab dyalek f l'catalogue db."
    elif "anglais" in lang:
        return "Sorry, I couldn't find a matching vehicle in the current catalog."
    else:
        return "Je n'ai pas trouvé de véhicule correspondant dans le catalogue actuel."


def _format_vehicle_context(vehicles: list[dict]) -> str:
    if not vehicles:
        return "Aucun vehicule trouve dans le catalogue."
    lines = []
    for i, v in enumerate(vehicles, 1):
        meta = v.get("metadata", {})
        title = f"{meta.get('brand', '')} {meta.get('model', '')} ({meta.get('year', '')})"
        price = meta.get("price", "N/A")
        fuel = meta.get("fuel_type", "N/A")
        body = meta.get("body_type", "N/A")
        city = meta.get("city", "N/A")
        desc = meta.get("description", "")

        line = (
            f"{i}. {title}\n"
            f"   Prix: {price} MAD\n"
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
        role = "Utilisateur" if entry["role"] == "user" else "Wakala"
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

    async def _validate_query(self, message: str, history: list[dict]) -> Optional[str]:
        """Returns a clarification question if the query is vague, else None."""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        history_text = _format_history(history)
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=(
                "Analyse l'historique et la demande de l'utilisateur. S'il cherche un véhicule mais "
                "qu'AUCUN budget, NI ville, NI modèle précis n'a été mentionné (ni avant, ni maintenant), "
                "formule une courte question polie dans la même langue que l'utilisateur demandant ces précisions (ex: 'Chhal le budget dyalek ?', 'What is your budget?', etc.). "
                "Si les critères sont suffisants, réponds EXACTEMENT 'OK'."
                f"\nHISTORIQUE:\n{history_text}"
            )),
            HumanMessage(content=message)
        ])
        try:
            llm = self._get_llm()
            response = await llm.ainvoke(prompt.format_messages())
            reply = response.content.strip()
            if reply.upper() == "OK" or reply.upper().startswith("OK"):
                return None
            return reply
        except Exception:
            return None

    def _get_llm(self) -> Any:
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain/OpenAI n'est pas installe")
        if self._llm is None:
            self._llm = ChatOpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key=settings.OPENAI_API_KEY,
                model=settings.OLLAMA_MODEL_TEXT,
                temperature=0.3,
                max_tokens=600,
                model_kwargs={
                    "frequency_penalty": 1.2,
                    "presence_penalty": 0.5
                }
            )
        return self._llm

    async def answer(
        self,
        message: str,
        session_id: str,
    ) -> ChatResponse:
        history = conversation_memory.get_history(session_id)

        # Validation step: intercept vague queries
        clarification = await self._validate_query(message, history)
        if clarification:
            conversation_memory.add_turn(session_id, message, clarification)
            return ChatResponse(reply=clarification, sources=[], session_id=session_id)

        detected_lang = _detect_language(message)

        # The caps here are intentional: never send an unbounded catalogue to the LLM.
        query = _retrieval_query(message, history)
        vehicles = search_vehicles(query, limit=5)[:5]
        reviews = search_reviews(query, limit=3)[:3]

        # Do not let the model turn an empty (or insufficient) retrieval into a guess.
        if not vehicles:
            no_match = _get_no_match_reply(detected_lang)
            conversation_memory.add_turn(session_id, message, no_match)
            return ChatResponse(reply=no_match, sources=[], session_id=session_id)

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

        style_profile = style_detector.detect_style(message)
        style_instructions = ""
        if style_profile["formality"] == "casual":
            style_instructions += "- Ton: Direct, détendu et chaleureux (sans familiarité excessive).\n"
        else:
            style_instructions += "- Ton: Poli, vouvoiement de rigueur.\n"
            
        if style_profile["verbosity"] == "concise":
            style_instructions += "- Format: Réponses ultra-courtes et directes (1 phrase max).\n"
        else:
            style_instructions += "- Format: Réponses courtes et directes (2 phrases max) pour garantir une réponse rapide.\n"
            
        if style_profile["technicality"] == "technical":
            style_instructions += "- Technicité: Vocabulaire automobile expert, ne pas vulgariser les termes évidents.\n"
        else:
            style_instructions += "- Technicité: Vulgariser les concepts (ex: expliquer ce qu'est une DSG si mentionnée).\n"

        system_message = SYSTEM_PROMPT.format(
            detected_language=detected_lang,
            vehicle_context=vehicle_context,
            graph_context=graph_context,
            review_context=review_context,
            conversation_history=conversation_history,
            style_instructions=style_instructions,
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

        sources = []
        for v in vehicles[:5]:
            if not v.get("vehicle_id"):
                continue
            
            meta = v.get("metadata", {})
            title = meta.get("brand", "") + " " + meta.get("model", "")
            
            images = meta.get("images", [])
            image_url = images[0] if isinstance(images, list) and images else (images if isinstance(images, str) else None)
            
            price_val = meta.get("price")
            price_str = str(price_val) if price_val is not None else None
            
            sources.append(
                SourceReference(
                    vehicle_id=v["vehicle_id"],
                    vehicle_title=title.strip(),
                    relevance_score=v.get("score", 0),
                    source_type="vector_search",
                    image_url=image_url,
                    price=price_str
                )
            )

        conversation_memory.add_turn(session_id, message, reply)

        return ChatResponse(
            reply=reply,
            sources=sources,
            session_id=session_id,
            style_profile=style_profile,
        )


chatbot_chain = ChatbotChain()
