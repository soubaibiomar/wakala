import { useState, useEffect } from 'react';

export function useHeroSequence() {
  const [isApproaching] = useState(true);
  const [flashState, setFlashState] = useState<'off' | 'flash1' | 'flash2' | 'on'>('off');
  const [plateState, setPlateState] = useState<'plate' | 'morph' | 'expanded'>('plate');
  const [isInteractive, setIsInteractive] = useState(false);

  useEffect(() => {
    // 1. La voiture s'approche pendant ~2.2s (géré par CSS keyframes sur le montage)
    
    // 2. Les phares flashent à ~2.45s
    const t1 = setTimeout(() => {
      setFlashState('flash1');
    }, 2450);

    // Fin du flash 1
    const t2 = setTimeout(() => {
      setFlashState('off');
    }, 2650);

    // Deuxième flash à ~3.0s
    const t3 = setTimeout(() => {
      setFlashState('flash2');
    }, 3000);

    // Les phares restent allumés doucement après le 2ème flash
    const t4 = setTimeout(() => {
      setFlashState('on');
    }, 3200);

    // 3. La plaque commence sa transformation à ~3.05s
    const t5 = setTimeout(() => {
      setPlateState('morph');
    }, 3050);

    // 4. La plaque devient la barre de recherche complète et interactive à ~3.9s
    const t6 = setTimeout(() => {
      setPlateState('expanded');
      setIsInteractive(true);
    }, 3900);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
      clearTimeout(t6);
    };
  }, []);

  return { isApproaching, flashState, plateState, isInteractive };
}
