import { useState, useEffect, useCallback } from 'react';
import Voice, { SpeechResultsEvent, SpeechErrorEvent } from '@react-native-voice/voice';

export type VoiceStatus = 'idle' | 'listening' | 'error';

interface UseVoiceInputOptions {
  defaultLang?: string;
  onTranscript: (text: string) => void;
}

export function useVoiceInput({ defaultLang = 'fr-FR', onTranscript }: UseVoiceInputOptions) {
  const [status, setStatus] = useState<VoiceStatus>('idle');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lang, setLangState] = useState(defaultLang);
  const [isSupported, setIsSupported] = useState(true); // Assuming true, could verify native module

  useEffect(() => {
    Voice.onSpeechStart = () => {
      setStatus('listening');
      setErrorMessage(null);
      setInterimTranscript('');
    };

    Voice.onSpeechRecognized = () => {
      // Reconnu mais pas encore final
    };

    Voice.onSpeechEnd = () => {
      setStatus('idle');
      setInterimTranscript('');
    };

    Voice.onSpeechError = (e: SpeechErrorEvent) => {
      setStatus('error');
      setErrorMessage(e.error?.message || 'Erreur inconnue');
    };

    Voice.onSpeechResults = (e: SpeechResultsEvent) => {
      if (e.value && e.value.length > 0) {
        onTranscript(e.value[0]);
      }
    };

    Voice.onSpeechPartialResults = (e: SpeechResultsEvent) => {
      if (e.value && e.value.length > 0) {
        setInterimTranscript(e.value[0]);
      }
    };

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, [onTranscript]);

  const startListening = useCallback(async () => {
    try {
      setErrorMessage(null);
      await Voice.start(lang);
    } catch (e) {
      console.error(e);
      setStatus('error');
      setErrorMessage(String(e));
    }
  }, [lang]);

  const stopListening = useCallback(async () => {
    try {
      await Voice.stop();
      setStatus('idle');
    } catch (e) {
      console.error(e);
    }
  }, []);

  const toggleListening = useCallback(() => {
    if (status === 'listening') {
      stopListening();
    } else {
      startListening();
    }
  }, [status, startListening, stopListening]);

  const setLang = useCallback(async (newLang: string) => {
    setLangState(newLang);
    if (status === 'listening') {
      await stopListening();
      // On redémarre pas automatiquement pour laisser le choix à l'utilisateur
    }
  }, [status, stopListening]);

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
