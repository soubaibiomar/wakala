/**
 * HeroIntro.tsx — Écran noir avec vraie image de phares
 *
 * Timeline:
 *  0s   → noir total
 *  0.6s → image des phares s'allume (fade in rapide)
 *  1.2s → flash x2
 *  2.0s → phares stables
 *  2.8s → fade out
 *  3.4s → onComplete()
 */

import { useEffect, useState, useRef } from 'react';
import styles from './heroIntro.module.css';

type Phase = 'dark' | 'on' | 'flash' | 'steady' | 'exit';

interface HeroIntroProps {
  onComplete: () => void;
}

const PHARES_IMG = '/assets/phares-intro.jpg';

export default function HeroIntro({ onComplete }: HeroIntroProps) {
  const [phase, setPhase] = useState<Phase>('dark');
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    const t = (fn: () => void, ms: number) => {
      const id = setTimeout(fn, ms);
      timers.current.push(id);
    };

    t(() => setPhase('on'),     600);
    t(() => setPhase('flash'),  1200);
    t(() => setPhase('steady'), 2000);
    t(() => setPhase('exit'),   2800);
    t(onComplete,               3400);

    return () => timers.current.forEach(clearTimeout);
  }, [onComplete]);

  const isExiting = phase === 'exit';
  const isFlash = phase === 'flash';
  const isVisible = phase === 'on' || phase === 'flash' || phase === 'steady';

  return (
    <div className={`${styles.scene} ${isExiting ? styles.sceneExit : ''}`}>
      <img 
        src={PHARES_IMG} 
        alt="Phares" 
        className={`${styles.pharesImg} ${isVisible ? styles.visible : ''} ${isFlash ? styles.flash : ''}`}
        draggable={false}
      />
    </div>
  );
}
