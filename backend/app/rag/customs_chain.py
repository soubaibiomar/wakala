import os
import logging
from typing import Any

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    ChatOpenAI = Any
    PromptTemplate = Any
    LANGCHAIN_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)

class CustomsChain:
    def __init__(self):
        self._chain = None
        self._initialized = False

    def _init_chain(self):
        """Lazy initialization to avoid crashes at import time."""
        if self._initialized:
            return
        self._initialized = True

        if not LANGCHAIN_AVAILABLE:
            logger.warning("langchain_groq non disponible — verdict IA désactivé.")
            return

        try:
            self.llm = ChatOpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key=settings.OPENAI_API_KEY,
                model=settings.OLLAMA_MODEL_TEXT,
                temperature=0.2,
                max_tokens=350,
            )
            

            self.prompt = PromptTemplate(
                input_variables=[
                    "brand", "model", "year", "fuel_type", "fiscal_power",
                    "purchase_price", "total_customs_fees", "total_cost", "local_market_price"
                ],
                template="""
Tu es un expert automobile et conseiller financier au Maroc (Wakala).
Ton rôle est d'analyser la rentabilité de l'importation d'un véhicule depuis l'étranger vers le Maroc.

DONNÉES DU VÉHICULE :
- Marque/Modèle : {brand} {model}
- Année : {year}
- Carburant : {fuel_type} (Puissance : {fiscal_power} CV)

DONNÉES FINANCIÈRES :
- Prix d'achat origine : {purchase_price} MAD
- Total Frais de Douane (TVA incluse) : {total_customs_fees} MAD
- Coût de revient TOTAL (Achat + Douane) : {total_cost} MAD
- Prix estimé sur le marché local marocain (Argus Wakala) : {local_market_price} MAD

INSTRUCTIONS :
1. Compare le "Coût de revient TOTAL" au "Prix estimé sur le marché local".
2. Détermine si l'importation est une "Bonne Affaire" ou "Non Rentable".
3. Rédige un verdict clair, professionnel, et concis (maximum 2 paragraphes courts) en français.
4. Précise les risques liés à l'importation pour nuancer ton conseil.

RÉPONSE (Pas de blabla introductif, va droit au but) :
"""
            )
            
            self._chain = self.prompt | self.llm
        except Exception as e:
            logger.error(f"Erreur initialisation CustomsChain: {e}")

    async def generate_verdict(self, vehicle_data: dict, financial_data: dict, local_market_price: float) -> str:
        """Génère le verdict de rentabilité IA."""
        self._init_chain()

        if self._chain is None:
            # Fallback sans IA
            total_cost = financial_data.get("total_cost", 0)
            if total_cost <= local_market_price:
                return f"Bonne affaire potentielle : le coût total importé ({total_cost:,.0f} MAD) est inférieur au prix local estimé ({local_market_price:,.0f} MAD). Attention toutefois aux risques liés à l'historique du véhicule."
            else:
                return f"Importation non rentable : le coût total ({total_cost:,.0f} MAD) dépasse le prix du marché local ({local_market_price:,.0f} MAD). Préférez un achat local."

        try:
            response = await self._chain.ainvoke({
                "brand": vehicle_data.get("brand", "Véhicule"),
                "model": vehicle_data.get("model", ""),
                "year": vehicle_data.get("year", 2020),
                "fuel_type": vehicle_data.get("fuel_type", "Diesel"),
                "fiscal_power": vehicle_data.get("fiscal_power", 8),
                "purchase_price": financial_data.get("purchase_price"),
                "total_customs_fees": financial_data.get("total_customs_fees"),
                "total_cost": financial_data.get("total_cost"),
                "local_market_price": local_market_price
            })
            return response.content.strip()
        except Exception as e:
            logger.error(f"Erreur Groq lors du verdict douane : {e}")
            return "Verdict indisponible pour le moment. Veuillez vérifier les chiffres manuellement."

customs_chain = CustomsChain()
