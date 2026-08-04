/**
 * services/searchParseService.ts — Appel API pour l'extraction NLP et vocale.
 */

import api from './api';

export interface NlpExtractionResult {
  budget: number | null;
  usage_prevu: string | null;
  priorites: string[];
  profil_passagers: string | null;
  erreur: boolean;
  
  // Nouveaux champs pour le multilinguisme et la clarification
  confiance?: 'haute' | 'moyenne' | 'basse' | null;
  langue_detectee?: 'fr' | 'ar' | 'darija' | 'en' | null;
  statut?: string | null;
  question?: string | null;
}

export interface VoiceSearchResponse {
  texte_transcrit: string;
  transcription_editable: boolean;
  resultat_nlp: NlpExtractionResult | null;
}

/**
 * Parse une phrase de recherche en texte libre via le backend NLP.
 */
export async function parseSearchQuery(
  texte: string
): Promise<NlpExtractionResult> {
  try {
    const { data } = await api.post<NlpExtractionResult>(
      '/search/parse',
      { texte }
    );
    return data;
  } catch {
    return {
      budget: null,
      usage_prevu: null,
      priorites: [],
      profil_passagers: null,
      erreur: true,
    };
  }
}

/**
 * Envoie un fichier audio pour transcription Whisper et extraction NLP.
 */
export async function parseVoiceQuery(
  audioFile: File | Blob,
  extension: string = 'webm'
): Promise<VoiceSearchResponse> {
  const formData = new FormData();
  formData.append('file', audioFile, `audio.${extension}`);
  
  try {
    const { data } = await api.post<VoiceSearchResponse>(
      '/search/voice',
      formData
    );
    return data;
  } catch {
    return {
      texte_transcrit: '',
      transcription_editable: true,
      resultat_nlp: {
        budget: null,
        usage_prevu: null,
        priorites: [],
        profil_passagers: null,
        erreur: true,
      },
    };
  }
}
