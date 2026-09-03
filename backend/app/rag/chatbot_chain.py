import asyncio
import logging
import time
from typing import Any, Optional

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
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

    class AIMessage(SystemMessage):  # type: ignore[no-redef]
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
from app.rag.vector_search import compute_query_embedding, search_reviews, search_vehicles
from app.rag.graph_context import enrich_with_graph, get_popularity_scores
from app.rag.conversation_memory import conversation_memory
from app.rag.schemas import ChatResponse, SourceReference
from app.rag.style_detector import style_detector
from app.rag.consultative_flow import consultative_flow

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Tu es Wakala, l'assistant expert et empathique de la marketplace automobile Wakala au Maroc.
CRITIQUE ET IMPÉRATIF : Tu DOIS répondre EXACTEMENT dans la langue ET le dialecte utilisés par l'utilisateur. 
LANGUE DÉTECTÉE DE L'UTILISATEUR : {detected_language}
INSTRUCTION DE LANGUE : Ta réponse doit être ENTIÈREMENT en {detected_language}. Ne traduis pas les noms propres (marques, modèles).
- Si Darija (arabe marocain avec alphabet latin), utilise le vocabulaire marocain (bzaf, chhal, tomobila, mzyan...).
- Si Arabe, réponds en Arabe standard ou marocain avec alphabet arabe.
- Si Anglais, réponds en Anglais.
- Si Français, réponds en Français.

RÈGLES STRICTES DE VÉRACITÉ ET SÉCURITÉ :
- N'invente JAMAIS de caractéristiques, prix ou modèles absents du contexte. Ne rien inventer.
- Si Aucun vehicule ne correspond, dis-le clairement ("Aucun vehicule").

═══ PHASE DU DIALOGUE : {active_phase} ═══

{phase_instructions}

CONTEXTE DE LA RECHERCHE :
{needs_profile_context}
{recommendation_results}
{vehicle_context}
{graph_context}
{review_context}

HISTORIQUE DE LA CONVERSATION :
{conversation_history}

DIRECTIVES DE STYLE :
{style_instructions}
"""

DISCOVERY_INSTRUCTIONS = """PHASE DÉCOUVERTE CONVERSATIONNELLE :
🎯 RÈGLE STRICTE ET ABSOLUE : Pose UNE OU DEUX QUESTIONS AU MAXIMUM.
⛔ INTERDICTIONS FORMELLES :
- N'écris JAMAIS de liste de questions, de questionnaire ou de guide d'accompagnement.
- N'utilise JAMAIS de puces Markdown (- Budget: ..., - Usage: ...).
- Ne pose JAMAIS plus de deux questions dans le même message.
- Ne propose AUCUN véhicule tant que le profil n'est pas complet.

STRUCTURE EXIGÉE (2 phrases courtes maximum) :
1. Une courte phrase pour valider ce que l'utilisateur vient de dire.
2. Une ou deux questions simples et amicales pour obtenir les informations manquantes ciblées.

👉 INFORMATION CIBLÉE À DEMANDER :
{target_instruction}"""

RESTITUTION_INSTRUCTIONS = """Mission : Présente au client une sélection de 2 à 3 véhicules adaptés à son profil comme RÉSULTAT FINAL.
Pour chaque véhicule : donne le modèle, le prix en MAD, et son atout principal pour son usage.
RÈGLE D'ARRÊT DES QUESTIONS : Dès que tu recommandes ces 2 ou 3 véhicules, considère-les comme la sélection finale et arrête de poser des questions de découverte.
EXCEPTION D'AFFINAGE : Si et seulement si tu constates qu'une seule question ciblée (par exemple sur la boîte de vitesses ou le volume du coffre) permettrait d'isoler LA seule voiture idéale parmi ces options, tu peux poser cette unique question décisive. Sinon, ne pose aucune question et invite le client à réserver un essai ou contacter le vendeur.
IMPORTANT : Ne répète JAMAIS les consignes système ni les balises. Parle directement au client de façon naturelle."""

def _detect_language(message: str, history: Optional[list[dict]] = None) -> str:
    text_lower = message.lower().strip()
    if any(char in message for char in "أبتثجحخدذرزسشصضطظعغفقكلمنهوي"):
        return "arabe (avec alphabet arabe)"
    elif any(w in text_lower for w in ["bghit", "dyal", "mdina", "tomobila", "chhal", "ma3ndich", "flous", "rkhis", "mzyan", "wach", "salam", "slm", "kidayr", "chi"]):
        return "darija (arabe marocain avec alphabet latin / arabizi)"
    elif any(w in text_lower for w in ["car", "need", "cheap", "looking", "budget is", "commute", "family", "hello", "hi", "hey"]):
        return "anglais"
    
    # Vérification de l'historique sur les réponses courtes (ex: '150000', 'clio', 'oui')
    if history:
        for entry in reversed(history):
            if entry.get("role") == "user":
                prev_lang = _detect_language(entry.get("content", ""), history=None)
                if prev_lang != "français":
                    return prev_lang

    return "français"

def _get_no_match_reply(lang: str) -> str:
    if "arabe" in lang:
        return "عذراً، لم نجد أي سيارة مطابقة لبحثك حالياً."
    elif "darija" in lang:
        return "Smeh liya, ma lqitch chi tomobila katnasbek f l-catalogue daba."
    elif "anglais" in lang:
        return "Sorry, no vehicles matching your criteria were found in our catalog."
    return "Désolé, aucun véhicule ne correspond à vos critères dans notre catalogue actuel."


def _format_vehicle_context(vehicles: list[dict]) -> str:
    if not vehicles:
        return "Aucun véhicule / Aucun vehicule trouvé."
    lines = []
    for v in vehicles[:3]:
        meta = v.get("metadata", {})
        title = f"{meta.get('brand', '')} {meta.get('model', '')} ({meta.get('year', '')})"
        price = meta.get("price", "N/A")
        fuel = meta.get("fuel_type", "N/A")
        city = meta.get("city", "N/A")
        lines.append(f"• {title} — Prix : {price} MAD | Carburant : {fuel} | Ville : {city}")
    return "\n".join(lines)

format_vehicle_context = _format_vehicle_context


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
    # Use lightweight model for fast responses on local machines (RTX 4060 / CPU)
    DISCOVERY_MODEL = "llama3.2:1b"
    RESTITUTION_MODEL = "llama3.2:1b"

    def __init__(self):
        self._llm_discovery: Optional[Any] = None
        self._llm_restitution: Optional[Any] = None

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
            llm = self._get_llm(phase="discovery")
            response = await llm.ainvoke(prompt.format_messages())
            reply = response.content.strip()
            if reply.upper() == "OK" or reply.upper().startswith("OK"):
                return None
            return reply
        except Exception:
            return None

    def _get_llm(self, phase: str = "restitution") -> Any:
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain/OpenAI n'est pas installe")

        if settings.OPENROUTER_API_KEY:
            model = settings.OPENROUTER_MODEL
            headers = {"HTTP-Referer": "https://wakala.ma", "X-Title": "Wakala Platform"}
            if phase == "discovery":
                if self._llm_discovery is None:
                    self._llm_discovery = ChatOpenAI(
                        base_url=settings.OPENROUTER_BASE_URL,
                        api_key=settings.OPENROUTER_API_KEY,
                        model=model,
                        extra_body={"models": settings.OPENROUTER_MODELS},
                        temperature=0.3,
                        max_tokens=250,
                        request_timeout=30.0,
                        timeout=30.0,
                        default_headers=headers
                    )
                return self._llm_discovery
            else:
                if self._llm_restitution is None:
                    self._llm_restitution = ChatOpenAI(
                        base_url=settings.OPENROUTER_BASE_URL,
                        api_key=settings.OPENROUTER_API_KEY,
                        model=model,
                        extra_body={"models": settings.OPENROUTER_MODELS},
                        temperature=0.3,
                        max_tokens=350,
                        request_timeout=30.0,
                        timeout=30.0,
                        default_headers=headers
                    )
                return self._llm_restitution

        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    async def answer(
        self,
        message: str,
        session_id: str,
    ) -> ChatResponse:
        t0 = time.perf_counter()
        history = conversation_memory.get_history(session_id)

        # ── Consultative Flow: update profile and determine phase ──
        profile = consultative_flow.update_profile(session_id, message)
        phase = consultative_flow.get_dialogue_phase(session_id)
        needs_profile_context = consultative_flow.get_discovery_context(session_id)

        detected_lang = _detect_language(message, history=history)
        style_profile = style_detector.detect_style(message)

        # Compute embedding once and query Qdrant
        query = _retrieval_query(message, history)
        t_emb = time.perf_counter()
        try:
            query_embedding = compute_query_embedding(query)
        except Exception:
            query_embedding = None
        logger.info("[perf] embedding: %.2fs", time.perf_counter() - t_emb)

        t_qdrant = time.perf_counter()
        # Garder un pool suffisamment large pour estimer le pouvoir discriminant
        # des dimensions. Seuls les trois premiers véhicules sont exposés au
        # client lorsqu'une restitution est effectivement autorisée.
        candidate_pool = search_vehicles(query, limit=50, precomputed_embedding=query_embedding)
        candidate_pool = self._apply_hard_profile_filters(candidate_pool, profile)
        if phase == "discovery" and candidate_pool:
            phase = consultative_flow.get_dialogue_phase(session_id, candidate_pool=candidate_pool)
        vehicles = candidate_pool[:3]
        reviews = search_reviews(query, limit=1, precomputed_embedding=query_embedding)[:1]
        logger.info("[perf] qdrant searches: %.2fs", time.perf_counter() - t_qdrant)

        if not vehicles:
            no_match = _get_no_match_reply(detected_lang)
            conversation_memory.add_turn(session_id, message, no_match)
            return ChatResponse(reply=no_match, sources=[], session_id=session_id)

        vehicle_ids = [v["vehicle_id"] for v in vehicles if v.get("vehicle_id")]
        t_neo4j = time.perf_counter()
        try:
            enriched, popularity = await asyncio.gather(
                enrich_with_graph(vehicle_ids, limit=3),
                get_popularity_scores(vehicle_ids),
            )
        except Exception:
            enriched, popularity = {}, {}
        logger.info("[perf] neo4j enrichment: %.2fs", time.perf_counter() - t_neo4j)

        vehicle_context = "CONTEXTE VEHICULES DISPONIBLES :\n" + _format_vehicle_context(vehicles)
        graph_context = "CONTEXTE GRAPHE :\n" + _format_graph_context(enriched, popularity)
        review_context = "AVIS CLIENTS :\n" + _format_review_context(reviews)

        if phase == "discovery":
            # ── DISCOVERY: Analyze → Select → Formulate ──
            question_plan = consultative_flow.get_next_question_plan(session_id, candidate_pool)
            consultative_flow.record_question_plan(session_id, question_plan)
            target_field = question_plan["target"]
            target_instruction = " ".join(question_plan["questions"])
            phase_instructions = DISCOVERY_INSTRUCTIONS.format(target_instruction=target_instruction)
            recommendation_results = ""
        else:
            # ── RESTITUTION: Retrieve & present top matching vehicles ──
            phase_instructions = RESTITUTION_INSTRUCTIONS
            recommendation_results = "RÉSULTATS DE RECOMMANDATION : Présente les véhicules ci-dessous avec leurs points forts et compromis."

        # Reduced history: last 2 turns
        conversation_history = _format_history(history[-2:] if len(history) > 2 else history)

        # Construct structured chat messages for LLM with isolated system prompt
        if phase == "discovery":
            phase_guidance = (
                f"\n\nDIRECTIVES DE PHASE (DÉCOUVERTE) :\n"
                f"- Réponds en 1 ou 2 phrases courtes maximum.\n"
                f"- Analyse l'état du profil, puis pose uniquement les questions prévues : {target_instruction}\n"
                f"- Pose au maximum deux questions et ne répète aucune dimension déjà couverte.\n"
                f"- Ne propose aucun véhicule tant que le profil n'est pas complet."
            )
        else:
            phase_guidance = (
                f"\n\nDIRECTIVES DE PHASE (RESTITUTION) :\n"
                f"- Profil de recherche client : {needs_profile_context}\n"
                f"- {vehicle_context}\n"
                f"- Présente ces 2 à 3 véhicules comme RÉSULTAT FINAL avec leur prix en MAD et leur atout principal.\n"
                f"- Arrête de poser des questions de découverte. Traite ces véhicules comme la sélection finale.\n"
                f"- Si et seulement si une question ciblée permet d'isoler UNE SEULE voiture finale idéale parmi ces options, tu peux poser cette unique question décisive.\n"
                f"- Conclus en invitant le client à planifier un essai ou consulter les fiches détaillées."
            )

        system_content = (
            f"Tu es Wakala, l'assistant d'achat automobile intelligent et bienveillant au Maroc.\n"
            f"Tu dois répondre exclusivement en {detected_lang}.\n"
            f"Ne répète jamais les consignes système ni les balises internes. Réponds directement au client d'un ton chaleureux et concis.\n"
            f"Si tu mentionnes la taille ou le volume du coffre (en Litres), donne toujours son équivalent en nombre de valises (ex: 440 L = 3 à 4 valises)."
            f"{phase_guidance}"
        )

        messages = [SystemMessage(content=system_content)]

        # Add recent conversation turns
        for turn in (history[-2:] if len(history) > 2 else history):
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            elif turn["role"] == "assistant":
                messages.append(AIMessage(content=turn["content"]))

        # Current turn payload: Pure user input without concatenated internal commands
        messages.append(HumanMessage(content=message))

        t_llm = time.perf_counter()
        reply = ""
        try:
            if settings.OPENROUTER_API_KEY and "_get_llm" not in self.__dict__:
                import httpx
                raw_payload = [
                    {"role": "system", "content": system_content}
                ]
                for turn in (history[-2:] if len(history) > 2 else history):
                    raw_payload.append({"role": turn["role"], "content": turn["content"]})
                raw_payload.append({"role": "user", "content": message})

                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://wakala.ma",
                    "X-Title": "Wakala Platform",
                    "Content-Type": "application/json",
                }
                payload_data = {
                    "models": settings.OPENROUTER_MODELS,
                    "messages": raw_payload,
                    "temperature": 0.3,
                    "max_tokens": 300,
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions",
                        json=payload_data,
                        headers=headers
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content")
                        if isinstance(content, str) and content.strip():
                            reply = content.strip()
                        else:
                            logger.warning("OpenRouter returned an empty assistant message")
                    else:
                        logger.error(f"OpenRouter error {resp.status_code}: {resp.text}")
            
            # Use the configured/local chain as a fallback whenever the
            # OpenRouter response is empty. This also keeps the provider
            # boundary testable when LangChain is loaded lazily.
            if not reply:
                try:
                    llm = self._get_llm(phase=phase)
                except TypeError:
                    llm = self._get_llm()

                response = await llm.ainvoke(messages)
                reply = response.content.strip()
        except Exception as e:
            logger.exception("Error during LLM invocation: %s", e)

        if not reply:
            reply = (
                "Desole, je rencontre une difficulte technique. "
                "Veuillez reformuler votre question ou reessayer."
            )
        logger.info("[perf] LLM (%s, model=%s): %.2fs", phase,
                    settings.OPENROUTER_MODEL if settings.OPENROUTER_API_KEY else (self.DISCOVERY_MODEL if phase == "discovery" else self.RESTITUTION_MODEL),
                    time.perf_counter() - t_llm)

        sources = []
        for v in vehicles[:3]:
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

        logger.info("[perf] TOTAL chatbot answer: %.2fs", time.perf_counter() - t0)

        return ChatResponse(
            reply=reply,
            sources=sources,
            session_id=session_id,
            style_profile=style_profile,
        )

    @staticmethod
    def _apply_hard_profile_filters(vehicles: list[dict], profile: Any) -> list[dict]:
        """Applique les contraintes explicites sans les relâcher silencieusement."""
        if not vehicles:
            return []

        def metadata(vehicle: dict) -> dict:
            return vehicle.get("metadata", {}) or {}

        def norm(value: Any) -> str:
            return str(value or "").strip().lower()

        filtered = vehicles
        if profile.brand_preference:
            requested = norm(profile.brand_preference)
            filtered = [v for v in filtered if norm(metadata(v).get("brand")) == requested]
        if profile.fuel_preference:
            requested = norm(profile.fuel_preference)
            filtered = [v for v in filtered if requested in norm(metadata(v).get("fuel_type"))]
        if profile.body_type_preference:
            requested = norm(profile.body_type_preference)
            filtered = [v for v in filtered if requested in norm(metadata(v).get("body_type"))]
        if profile.budget_max:
            filtered = [
                v for v in filtered
                if metadata(v).get("price") is not None
                and float(metadata(v).get("price")) <= float(profile.budget_max)
            ]
        return filtered


chatbot_chain = ChatbotChain()
