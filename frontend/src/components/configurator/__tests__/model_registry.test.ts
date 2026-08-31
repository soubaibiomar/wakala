import { describe, it, expect } from 'vitest';
import {
  MODEL_REGISTRY,
  has3DModel,
  getModel3DEntry,
  normalizeModelKey,
} from '../model_registry';

describe('model_registry', () => {
  it('identifie correctement le premier véhicule test configuré (Dacia Sandero Stepway)', () => {
    expect(has3DModel('dacia-sandero-stepway')).toBe(true);
    expect(has3DModel('Dacia Sandero Stepway')).toBe(true);
    expect(has3DModel('sandero-stepway')).toBe(true);

    const entry = getModel3DEntry('dacia-sandero-stepway');
    expect(entry).not.toBeNull();
    expect(entry?.modelPath).toBe('/models/dacia-sandero-stepway/model.glb');
    expect(entry?.materialMapPath).toBe('/models/dacia-sandero-stepway/material_map.json');
  });

  it('gère gracieusement et sans erreur les véhicules absents du registre', () => {
    // Un véhicule non enregistré ne doit jamais lancer d'exception
    expect(has3DModel('peugeot-208-inconnu')).toBe(false);
    expect(has3DModel(null)).toBe(false);
    expect(has3DModel(undefined)).toBe(false);
    expect(has3DModel('')).toBe(false);

    expect(getModel3DEntry('peugeot-208-inconnu')).toBeNull();
    expect(getModel3DEntry(null)).toBeNull();
    expect(getModel3DEntry(undefined)).toBeNull();
  });

  it('normalise les clés de modèles avec espaces, majuscules et caractères spéciaux', () => {
    expect(normalizeModelKey('Dacia Sandero Stepway !')).toBe('dacia-sandero-stepway');
    expect(normalizeModelKey('  Renault_Clio_5  ')).toBe('renault-clio-5');
    expect(normalizeModelKey('')).toBe('');
  });
});
