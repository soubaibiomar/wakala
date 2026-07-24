/**
 * services/searchParseService.ts — Appel API pour l'extraction NLP.
 *
 * Envoie une phrase de recherche en texte libre au backend
 * et récupère les critères structurés (budget, usage, priorités, profil).
 */

import api from './api';

export interface NlpExtractionResult {
  /** Budget en MAD (entier), ou null si non mentionné / hors plage */
  budget: number | null;
  /** Usage principal du véhicule (ex: "familial", "urbain") */
  usage: string | null;
  /** Liste des priorités utilisateur (ex: ["économique", "fiabilité"]) */
  priorites: string[];
  /** Profil passagers / type d'acheteur (ex: "famille") */
  profil_passagers: string | null;
  /** True si l'extraction a échoué */
  erreur: boolean;
}

/**
 * Parse une phrase de recherche en texte libre via le backend NLP.
 *
 * @param texte - La phrase utilisateur (FR/darija/arabizi)
 * @returns Les critères de recherche extraits
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
      usage: null,
      priorites: [],
      profil_passagers: null,
      erreur: true,
    };
  }
}
