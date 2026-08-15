import type { NlpExtractionResult } from '../services/searchParseService';

export const ALL_CRITERIA = [
  { id: 'performance', label: 'Performance', colorClass: 'performance-fill' },
  { id: 'confort', label: 'Confort', colorClass: 'confort-fill' },
  { id: 'economie', label: 'Économie', colorClass: 'economie-fill' },
  { id: 'securite', label: 'Sécurité', colorClass: 'securite-fill' },
  { id: 'fiabilite', label: 'Fiabilité', colorClass: 'fiabilite-fill' },
  { id: 'espace', label: 'Espace', colorClass: 'espace-fill' }
];

const USAGE_CRITERIA: Record<string, string[]> = {
  familial: ['espace', 'securite', 'confort'],
  urbain: ['economie', 'confort', 'fiabilite'],
  longue_distance: ['confort', 'economie', 'fiabilite'],
  professionnel: ['espace', 'economie', 'fiabilite'],
  sportif: ['performance', 'securite', 'fiabilite'],
  utilitaire: ['espace', 'economie', 'fiabilite'],
  tout_terrain: ['performance', 'fiabilite', 'espace'],
  quotidien: ['economie', 'confort', 'fiabilite'],
};

const PROFIL_CRITERIA: Record<string, string[]> = {
  famille: ['espace', 'securite', 'confort'],
  célibataire: ['performance', 'economie', 'confort'],
  couple: ['confort', 'economie', 'performance'],
  jeune_conducteur: ['securite', 'economie', 'fiabilite'],
  retraité: ['confort', 'securite', 'fiabilite'],
};

export function getIntelligentCriteria(nlpResult?: NlpExtractionResult | null) {
  const usage = nlpResult?.usage_prevu?.toLowerCase() || '';
  const profil = nlpResult?.profil_passagers?.toLowerCase() || '';
  const userPriorities = nlpResult?.priorites?.map(p => p.toLowerCase()) || [];
  
  let relevantIds: string[] = [];
  
  if (USAGE_CRITERIA[usage]) relevantIds.push(...USAGE_CRITERIA[usage]);
  if (PROFIL_CRITERIA[profil]) relevantIds.push(...PROFIL_CRITERIA[profil]);
  
  relevantIds = [...new Set(relevantIds)];
  
  if (relevantIds.length === 0) {
    relevantIds = ['performance', 'confort', 'economie', 'securite'];
  }
  
  relevantIds = relevantIds.filter(id => !userPriorities.includes(id));
  
  if (relevantIds.length < 3) {
    const fallback = ['performance', 'confort', 'economie', 'securite', 'fiabilite', 'espace'];
    for (const id of fallback) {
      if (!relevantIds.includes(id) && !userPriorities.includes(id)) {
        relevantIds.push(id);
      }
      if (relevantIds.length >= 4) break;
    }
  }
  
  return ALL_CRITERIA
    .filter(c => relevantIds.includes(c.id))
    .map(c => ({ ...c, value: 50 }));
}
