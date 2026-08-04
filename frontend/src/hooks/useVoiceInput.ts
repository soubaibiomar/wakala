/**
 * hooks/useVoiceInput.ts — Hook réutilisable pour la saisie vocale
 * via la Web Speech API native du navigateur.
 *
 * Comportement :
 * - Vérifie la disponibilité au montage (`isSupported`)
 * - Expose un état clair : idle | listening | error
 * - Langue par défaut : fr-FR (meilleur support natif)
 * - Coupure automatique après silence (comportement natif)
 * - onresult injecte le texte via callback `onTranscript`
 * - onerror / onend remet l'état proprement
 *
 * Limitation connue :
 * - Firefox ne supporte pas la Web Speech API → isSupported = false
 * - Le darija / arabe marocain n'est pas supporté nativement →
 *   rester en fr-FR et documenter comme limitation
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export type VoiceStatus = 'idle' | 'listening' | 'error';

interface UseVoiceInputOptions {
  /** Langue par défaut (ex: 'fr-FR'). */
  defaultLang?: string;
  /** Callback appelé avec le texte transcrit final. */
  onTranscript: (text: string) => void;
  /** Reconnaissance continue (true) ou one-shot (false, défaut). */
  continuous?: boolean;
}

interface UseVoiceInputReturn {
  /** false si le navigateur ne supporte pas la Web Speech API */
  isSupported: boolean;
  /** État courant de la reconnaissance vocale */
  status: VoiceStatus;
  /** Texte en cours de transcription (résultats intermédiaires) */
  interimTranscript: string;
  /** Message d'erreur lisible si status === 'error' */
  errorMessage: string | null;
  /** Langue actuellement sélectionnée */
  lang: string;
  /** Change la langue d'écoute */
  setLang: (lang: string) => void;
  /** Démarre l'écoute */
  startListening: () => void;
  /** Arrête l'écoute manuellement */
  stopListening: () => void;
  /** Bascule écoute on/off */
  toggleListening: () => void;
}

// Détection de la Web Speech API (Chrome, Edge, Safari 14.1+)
const SpeechRecognitionAPI =
  typeof window !== 'undefined'
    ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    : null;

export function useVoiceInput({
  defaultLang = 'fr-FR',
  onTranscript,
  continuous = false,
}: UseVoiceInputOptions): UseVoiceInputReturn {
  const [isSupported] = useState(() => !!SpeechRecognitionAPI);
  const [status, setStatus] = useState<VoiceStatus>('idle');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lang, setLangState] = useState(defaultLang);

  const recognitionRef = useRef<any>(null);
  const onTranscriptRef = useRef(onTranscript);

  // Garder la ref du callback à jour sans recréer l'instance
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  // Si on change la langue pendant l'écoute, on relance
  const setLang = useCallback((newLang: string) => {
    setLangState(newLang);
    if (recognitionRef.current && status === 'listening') {
      recognitionRef.current.stop();
      // Le redémarrage sera géré manuellement par l'utilisateur ou on pourrait l'automatiser
    }
  }, [status]);

  // Créer l'instance SpeechRecognition une seule fois, ou la recréer si la langue change ?
  // La plupart des navigateurs acceptent le changement de .lang sur une instance existante
  useEffect(() => {
    if (!SpeechRecognitionAPI) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      let interim = '';
      let finalText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      setInterimTranscript(interim);

      if (finalText) {
        setInterimTranscript('');
        onTranscriptRef.current(finalText.trim());
      }
    };

    recognition.onerror = (event: any) => {
      const code: string = event.error;

      if (code === 'no-speech' || code === 'aborted') {
        setStatus('idle');
        setErrorMessage(null);
        return;
      }
      
      if (code === 'language-not-supported') {
        if (lang !== 'fr-FR') {
            setLangState('fr-FR');
            setErrorMessage("Langue non supportée, passage au Français par défaut.");
            setStatus('idle');
            return;
        }
      }

      const messages: Record<string, string> = {
        'not-allowed': 'Accès au microphone refusé. Vérifiez les permissions.',
        'audio-capture': 'Aucun microphone détecté.',
        'network': 'Erreur réseau — connexion instable ou navigateur non supporté (privilégiez Chrome).',
        'service-not-allowed': 'Service de reconnaissance vocale non disponible.',
        'language-not-supported': 'La langue sélectionnée n\'est pas supportée par votre navigateur.'
      };

      setStatus('error');
      setErrorMessage(messages[code] || `Erreur de reconnaissance vocale (${code})`);
    };

    recognition.onend = () => {
      // Si on n'est pas en erreur, on remet idle
      setStatus((prev) => (prev === 'error' ? prev : 'idle'));
      setInterimTranscript('');
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.abort();
      } catch {
        // ignore
      }
    };
  }, [continuous]);

  // Update language without recreating the entire recognition instance
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = lang;
    }
  }, [lang]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;
    setErrorMessage(null);
    setInterimTranscript('');
    try {
      recognitionRef.current.start();
      setStatus('listening');
    } catch (err) {
      console.warn('SpeechRecognition.start() error:', err);
    }
  }, []);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return;
    try {
      recognitionRef.current.stop();
    } catch {
      // ignore
    }
    setStatus('idle');
    setInterimTranscript('');
  }, []);

  const toggleListening = useCallback(() => {
    if (status === 'listening') {
      stopListening();
    } else {
      startListening();
    }
  }, [status, startListening, stopListening]);

  return {
    isSupported,
    status,
    interimTranscript,
    errorMessage,
    lang,
    setLang,
    startListening,
    stopListening,
    toggleListening,
  };
}
