import json
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from app.core.config import settings

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

async def parse_via_llm(html_content: str) -> ScrapedVehicleData:
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

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=settings.OPENAI_API_KEY, temperature=0).with_structured_output(ScrapedVehicleData)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tu es un extracteur de données expert. Ta tâche est de lire le texte extrait d'une page d'annonce automobile marocaine et d'extraire les informations exactes requises. Si une information est absente, déduis-la intelligemment ou mets une valeur par défaut."),
        ("human", "Voici le texte de l'annonce :\n\n{text}")
    ])
    
    chain = prompt | llm
    result = await chain.ainvoke({"text": text_content})
    return result

async def parse_vehicle_page(html_content: str) -> ScrapedVehicleData:
    """
    Pipeline principal : 1. JSON-LD, 2. LLM Fallback.
    """
    # Priorité 1: JSON-LD
    vehicle_data = parse_json_ld(html_content)
    if vehicle_data and vehicle_data.price > 0 and vehicle_data.brand != 'Inconnu':
        return vehicle_data
        
    # Priorité 2: LLM
    return await parse_via_llm(html_content)
