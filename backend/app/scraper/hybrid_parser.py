import json
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from app.core.config import settings
import time
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scraper import FailedScrape

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.is_open = False

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.is_open = True
            logger.warning("Circuit Breaker OPEN: Trop d'erreurs LLM. Pause du scraper.")

    def record_success(self):
        self.failures = 0
        self.is_open = False

    def can_execute(self):
        if self.is_open:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.is_open = False
                logger.info("Circuit Breaker HALF-OPEN: Tentative de reprise.")
                return True
            return False
        return True

cb = CircuitBreaker()

class ScrapedVehicleData(BaseModel):
    brand: str = Field(description="La marque du véhicule (ex: Peugeot, Renault)")
    model: str = Field(description="Le modèle du véhicule (ex: 208, Clio)")
    year: int = Field(description="L'année de mise en circulation")
    mileage: int = Field(description="Le kilométrage du véhicule")
    price: float = Field(description="Le prix en MAD. Retourner uniquement le nombre sans devise ni séparateur.")
    fuel_type: str = Field(description="Type de carburant: essence, diesel, hybride, electrique")
    transmission: str = Field(description="Boîte de vitesses: manuelle, automatique")
    city: str = Field(description="Ville où se trouve le véhicule")
    description: Optional[str] = Field(description="Description complète de l'annonce", default=None)

def parse_json_ld(html_content: str) -> Optional[ScrapedVehicleData]:
    """
    Tente d'extraire les données depuis la balise <script type="application/ld+json">.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script', type='application/ld+json')
    
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') in ['Car', 'Vehicle', 'Product']:
                        return _map_json_ld_to_model(item)
            elif data.get('@type') in ['Car', 'Vehicle', 'Product']:
                return _map_json_ld_to_model(data)
        except Exception:
            continue
    return None

def _map_json_ld_to_model(data: dict) -> ScrapedVehicleData:
    # Mapping basique schema.org -> ScrapedVehicleData (à affiner selon les sites cibles)
    brand = data.get('brand', {}).get('name', 'Inconnu')
    if isinstance(data.get('brand'), str):
        brand = data['brand']
        
    price = 0.0
    offers = data.get('offers')
    if offers:
        if isinstance(offers, dict):
            price = float(offers.get('price', 0))
        elif isinstance(offers, list) and len(offers) > 0:
            price = float(offers[0].get('price', 0))

    return ScrapedVehicleData(
        brand=brand,
        model=data.get('model', 'Inconnu'),
        year=int(data.get('vehicleModelDate', data.get('productionDate', 2000))),
        mileage=int(data.get('mileageFromOdometer', {}).get('value', 0)),
        price=price,
        fuel_type=data.get('fuelType', 'diesel'),
        transmission='automatique' if 'auto' in str(data.get('vehicleTransmission', '')).lower() else 'manuelle',
        city='Maroc', # Default, JSON-LD usually doesn't have city unless in offers.areaServed
        description=data.get('description')
    )

async def parse_via_llm(html_content: str, url: str, db: AsyncSession) -> Optional[ScrapedVehicleData]:
    """
    Utilise le LLM pour extraire sémantiquement les infos si le JSON-LD échoue.
    """
    # Nettoyage pour économiser les tokens
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    
    text_content = soup.get_text(separator=' ', strip=True)
    # Limiter la taille si la page est immense
    text_content = text_content[:15000]

    if settings.OPENROUTER_API_KEY:
        llm = ChatOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            model=settings.OPENROUTER_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            temperature=0,
            default_headers={"HTTP-Referer": "https://wakala.ma", "X-Title": "Wakala Platform"}
        ).with_structured_output(ScrapedVehicleData)
    else:
        llm = ChatOpenAI(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL_TEXT, openai_api_key=settings.OPENAI_API_KEY, temperature=0).with_structured_output(ScrapedVehicleData)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tu es un extracteur de données expert. Ta tâche est de lire le texte extrait d'une page d'annonce automobile marocaine et d'extraire les informations exactes requises. Si une information est absente, déduis-la intelligemment ou mets une valeur par défaut."),
        ("human", "Voici le texte de l'annonce :\n\n{text}")
    ])
    
    
    if not cb.can_execute():
        logger.warning(f"Circuit Breaker ouvert, annulation du scraping LLM pour {url}")
        return None

    try:
        chain = prompt | llm
        result = await chain.ainvoke({"text": text_content})
        cb.record_success()
        return result
    except Exception as e:
        logger.error(f"Erreur LLM ({type(e).__name__}): {e}")
        cb.record_failure()
        
        # Sauvegarde en base
        failed = FailedScrape(url=url, error_reason=str(e))
        db.add(failed)
        await db.commit()
        return None

async def parse_vehicle_page(html_content: str, url: str, db: AsyncSession) -> Optional[ScrapedVehicleData]:
    """
    Pipeline principal : 1. JSON-LD, 2. LLM Fallback.
    """
    # Priorité 1: JSON-LD
    vehicle_data = parse_json_ld(html_content)
    if vehicle_data and vehicle_data.price > 0 and vehicle_data.brand != 'Inconnu':
        return vehicle_data
        
    # Priorité 2: LLM
    return await parse_via_llm(html_content, url, db)
