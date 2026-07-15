from typing import Any, Optional

try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
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

COMPARE_SYSTEM_PROMPT = """Tu es Wakala, l'expert conseiller automobile de la plateforme marocaine Wakala.
Ton objectif est de comparer les véhicules fournis et de conseiller l'acheteur.
Tu parles en français, avec quelques termes en Darija (phonétique) pour être empathique et chaleureux.
Fais ressortir les points forts (confort, ville, autoroute, consommation, coût de possession/TCO, état) de chacun.

CONTRAINTES STRICTES :
1. Sois TRÈS CONCIS : maximum 3 petits paragraphes. Pas de long discours.
2. N'invente jamais de données, base-toi UNIQUEMENT sur les véhicules fournis ci-dessous.
3. Si un véhicule est clairement meilleur (rapport qualité/prix), tu peux donner une recommandation "Coup de coeur".
4. Les prix sont en MAD.

VÉHICULES À COMPARER :
{vehicles_context}
"""

def _format_vehicles_for_compare(vehicles: list[dict]) -> str:
    if not vehicles:
        return "Aucun véhicule sélectionné."
    
    lines = []
    for i, v in enumerate(vehicles, 1):
        lines.append(f"Véhicule {i} ({v.get('brand')} {v.get('model')} - {v.get('year')}):")
        lines.append(f"  - Prix: {v.get('price')} MAD")
        lines.append(f"  - Kilométrage: {v.get('mileage')} km")
        lines.append(f"  - Carburant: {v.get('fuel_type')}")
        lines.append(f"  - Score IA État (0-100): {v.get('condition_score', 'Non évalué')}")
        lines.append(f"  - Description courte: {str(v.get('description', ''))[:100]}...")
        lines.append("")
    return "\n".join(lines)


class CompareChain:
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
                max_tokens=500,
            )
        return self._llm

    async def generate_comparison(self, vehicles: list[dict]) -> str:
        """
        Génère un verdict IA court et percutant comparant les véhicules fournis.
        """
        if len(vehicles) < 2:
            return "Veuillez sélectionner au moins 2 véhicules pour obtenir une comparaison IA."

        if not LANGCHAIN_AVAILABLE:
            return "Le service d'analyse IA n'est pas disponible pour le moment."

        context = _format_vehicles_for_compare(vehicles)
        system_msg = COMPARE_SYSTEM_PROMPT.format(vehicles_context=context)

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_msg),
            HumanMessage(content="Fais-moi un résumé comparatif clair et concis de ces véhicules.")
        ])

        try:
            llm = self._get_llm()
            response = await llm.ainvoke(prompt.format_messages())
            return response.content.strip()
        except Exception as e:
            return f"Désolé, je ne peux pas générer la comparaison pour l'instant ({str(e)})."

compare_chain = CompareChain()
