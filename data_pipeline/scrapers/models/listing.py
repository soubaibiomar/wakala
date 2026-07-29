from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field


class RawListing(BaseModel):
    """
    Sortie brute de parse_listing(), avant normalisation Ollama.
    Schéma commun à toutes les plateformes, quelle que soit la source.
    """
    model_config = ConfigDict(populate_by_name=True)

    source_plateforme: str        # "avito", "moteur", "wandaloo", "otoclic", "spoticar", "kifal_auto", "global_occaz"
    type_annonce: str             # "neuf" ou "occasion"
    titre_brut: str
    prix_brut: str                # Prix tel qu'affiché sur le site (ex: "80 000 DH")
    description_brute: str
    photos_urls: List[str] = Field(default_factory=list)
    vendeur_info: Dict[str, Any] = Field(default_factory=dict)  # Vide {} pour catalogues constructeur
    date_publication: Optional[str] = None
    url_source: str
    certifie: bool = False        # True pour Kifal Auto, Spoticar

    # Champs techniques enrichis par le scraper
    marque_brute: Optional[str] = None
    modele_brut: Optional[str] = None
    annee_brute: Optional[str] = None
    kilometrage_brut: Optional[str] = None
    carburant_brut: Optional[str] = None
    transmission_brute: Optional[str] = None
    ville_brute: Optional[str] = None

    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class Listing(BaseModel):
    """
    Unified schema for individual vehicle listings from marketplaces.
    Produced after normalization (Ollama or rule-based).
    """
    model_config = ConfigDict(populate_by_name=True)

    source_site: str
    listing_id: str
    url: str
    title: str

    brand: str
    model: str
    year: int
    price_mad: int
    mileage_km: Optional[int] = None
    fuel_type: str              # essence, diesel, hybride, electrique
    transmission: str           # manuelle, automatique
    condition: str              # new, used
    city: str

    seller_type: Optional[str] = None  # particulier, professionnel, concessionnaire
    images: List[str] = Field(default_factory=list)
    local_images: List[str] = Field(default_factory=list)
    image_count: int = 0
    description: Optional[str] = None

    certifie: bool = False
    sources_multiples: List[str] = Field(default_factory=list)

    posted_date: Optional[date] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class ModelCatalogEntry(BaseModel):
    """
    Schema for official concessionaire brand catalogs (new cars without individual VINs).
    """
    model_config = ConfigDict(populate_by_name=True)

    source_site: str
    brand: str
    model: str

    starting_price_mad: Optional[int] = None
    fuel_options: List[str] = Field(default_factory=list)
    body_type: Optional[str] = None
    promo_text: Optional[str] = None

    source_url: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
