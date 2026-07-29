import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, Float, DateTime, ForeignKey, 
    Text, Numeric, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

Base = declarative_base()

class SourcePlateforme(str, enum.Enum):
    avito = "avito"
    moteur = "moteur"
    wandaloo = "wandaloo"
    global_occaz = "global_occaz"
    otoclic = "otoclic"
    kifal_auto = "kifal_auto"
    spoticar = "spoticar"

class ListingType(str, enum.Enum):
    neuf = "neuf"
    occasion = "occasion"

class TrustSignalType(str, enum.Enum):
    anomalie_prix = "anomalie_prix"
    dommage_photo = "dommage_photo"
    profil_vendeur_suspect = "profil_vendeur_suspect"
    incoherence_titre_description = "incoherence_titre_description"

class ChatRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class UserRole(str, enum.Enum):
    buyer = "buyer"
    seller = "seller"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)  # Adapted from telephone
    city = Column(String(150), nullable=True)  # Adapted from ville
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.buyer, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_pro = Column(Boolean, default=False, nullable=False)
    preferences = Column(JSON, default=dict, nullable=False)
    avatar_url = Column(Text, nullable=True)
    
    # New AI and Persona columns
    persona_dominant = Column(String(100), nullable=True)
    n_interactions = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    chat_sessions = relationship("ChatSession", back_populates="user")


class Seller(Base):
    __tablename__ = "sellers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_affiche = Column(String(255), nullable=False)
    plateforme = Column(String(100), nullable=False)
    date_inscription_plateforme = Column(DateTime(timezone=True), nullable=True)
    nb_annonces_actives = Column(Integer, default=0, nullable=False)
    
    listings = relationship("Listing", back_populates="seller")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_plateforme = Column(SQLEnum(SourcePlateforme), nullable=False)
    type_annonce = Column(SQLEnum(ListingType), nullable=False)
    certifie = Column(Boolean, default=False, nullable=False)
    
    # Adapted from existing vehicles columns where possible
    marque = Column(String(100), nullable=False)
    modele = Column(String(100), nullable=False)
    annee = Column(Integer, nullable=False)
    prix = Column(Numeric(12, 2), nullable=False)
    kilometrage = Column(Integer, nullable=True)
    carburant = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    categorie = Column(String(50), nullable=True)
    
    tags = Column(ARRAY(String), default=list)
    vendeur_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=True)
    
    url_source = Column(String(500), nullable=True)
    date_publication = Column(DateTime(timezone=True), nullable=True)
    score_confiance = Column(Numeric(5, 4), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    seller = relationship("Seller", back_populates="listings")
    trust_signals = relationship("TrustSignal", back_populates="listing", cascade="all, delete-orphan")


class TrustSignal(Base):
    __tablename__ = "trust_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    type_signal = Column(SQLEnum(TrustSignalType), nullable=False)
    severite = Column(Numeric(5, 4), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    listing = relationship("Listing", back_populates="trust_signals")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="SET NULL"), nullable=True)
    langue_detectee = Column(String(10), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(ChatRole), nullable=False)
    contenu = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="messages")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marque = Column(String(100), nullable=False)
    modele = Column(String(100), nullable=False)
    annee = Column(Integer, nullable=False)
    prix_moyen_marche = Column(Numeric(12, 2), nullable=False)
    date_releve = Column(DateTime(timezone=True), nullable=False)
    source_donnee = Column(String(100), nullable=False)
