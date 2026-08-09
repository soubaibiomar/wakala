"""
api/routes_search.py — Endpoint d'extraction NLP pour la recherche en texte libre et transcription vocale.

POST /api/search/parse
  Body : {"texte": "je cherche une voiture familiale autour de 200k"}
  Response : {"budget": 200000, "usage": "familial", "priorites": ["économique"], "confiance": "haute", ...}
  
POST /api/search/voice
  Body : form-data avec "file" (audio)
  Response : {"texte_transcrit": "...", "transcription_editable": true, "resultat_nlp": {...}}
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.ml.nlp_pipeline.llm_extractor import extract_search_criteria
from app.ml.nlp_pipeline.schemas import ExtractedCriteria
from app.services.voice_transcription import transcrire_audio

router = APIRouter()

class ParseRequest(BaseModel):
    texte: str = Field(..., description="Texte de recherche libre")

class VoiceSearchResponse(BaseModel):
    texte_transcrit: str
    transcription_editable: bool = True
    resultat_nlp: Optional[ExtractedCriteria]

@router.post("/parse", response_model=ExtractedCriteria)
async def parse_search_query(payload: ParseRequest):
    """
    Analyse une phrase de recherche en texte libre, extrait
    les critères NLP, detecte la langue et gère la boucle de clarification.
    """
    result = await extract_search_criteria(payload.texte)
    return result

@router.post("/voice", response_model=VoiceSearchResponse)
async def parse_voice_query(file: UploadFile = File(...)):
    """
    Transcrit l'audio via le pipeline IA ASR Arabe/Darija :
    1. CohereLabs Arabic Transcribe (CohereLabs/cohere-transcribe-arabic-07-2026)
    2. HuBERT Darija (amineouaki/hubert-darija-combined)
    3. Whisper Groq
    et extrait les critères NLP.
    Retourne également le texte transcrit pour permettre à l'utilisateur de l'éditer.
    """
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Le fichier audio est trop volumineux (maximum 10MB).")
        
    transcription = await transcrire_audio(file)
    
    if transcription and not transcription.startswith("ERROR:"):
        resultat_nlp = await extract_search_criteria(transcription)
    else:
        resultat_nlp = ExtractedCriteria(erreur=True)
        
    return VoiceSearchResponse(
        texte_transcrit=transcription,
        transcription_editable=True,
        resultat_nlp=resultat_nlp
    )
