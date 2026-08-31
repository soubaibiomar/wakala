import { useCallback, useEffect, useRef, useState } from 'react';

export type VoiceStatus = 'idle' | 'listening' | 'error' | 'processing';

interface UseVoiceInputOptions {
  defaultLang?: string;
  onTranscript: (text: string) => void;
  continuous?: boolean;
}

interface UseVoiceInputReturn {
  isSupported: boolean;
  status: VoiceStatus;
  interimTranscript: string;
  errorMessage: string | null;
  lang: string;
  setLang: (lang: string) => void;
  startListening: () => void;
  stopListening: () => void;
  toggleListening: () => void;
}

const SpeechRecognitionAPI =
  typeof window !== 'undefined'
    ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    : null;

export function useVoiceInput({
  defaultLang = 'fr-FR',
  onTranscript,
  continuous = false,
}: UseVoiceInputOptions): UseVoiceInputReturn {
  const [status, setStatus] = useState<VoiceStatus>('idle');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lang, setLangState] = useState(defaultLang);
  const [useFallback, setUseFallback] = useState(!SpeechRecognitionAPI);

  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const onTranscriptRef = useRef(onTranscript);

  // Synchronise le callback de transcription
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  // Synchronise la langue dynamique (quand l'utilisateur change de langue dans l'UI)
  useEffect(() => {
    if (defaultLang && defaultLang !== lang) {
      setLangState(defaultLang);
      if (recognitionRef.current) {
        recognitionRef.current.lang = defaultLang;
      }
    }
  }, [defaultLang]);

  const setLang = useCallback(
    (newLang: string) => {
      setLangState(newLang);
      if (recognitionRef.current && status === 'listening' && !useFallback) {
        recognitionRef.current.stop();
      }
    },
    [status, useFallback]
  );

  // --- NATIVE SPEECH API (Web Speech API) ---
  useEffect(() => {
    if (!SpeechRecognitionAPI || useFallback) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = lang;

    recognition.onresult = (event: any) => {
      let interim = '';
      let finalText = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalText += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      setInterimTranscript(interim);
      if (finalText) {
        setInterimTranscript('');
        onTranscriptRef.current(finalText.trim());
      }
    };

    recognition.onerror = (event: any) => {
      const code = event.error;
      if (code === 'no-speech' || code === 'aborted') {
        setStatus('idle');
        return;
      }
      // Bascule automatique vers le fallback backend si le réseau du navigateur bloque
      if (code === 'network') {
        console.warn('Native Speech API network error. Bascule sur la transcription IA backend.');
        setUseFallback(true);
        setStatus('idle');
        return;
      }
      setStatus('error');
      setErrorMessage(`Microphone : ${code}`);
    };

    recognition.onend = () => {
      setStatus((prev) => (prev === 'error' ? prev : 'idle'));
      setInterimTranscript('');
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.abort();
      } catch {}
    };
  }, [continuous, useFallback, lang]);

  // --- FALLBACK MULTI-MODÈLES BACKEND (Cohere Arabic / HuBERT / Groq) ---
  const handleAudioUpload = async (audioBlob: Blob) => {
    setStatus('processing');
    setInterimTranscript('Transcription vocale en cours...');

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('language', lang);

      const apiBase = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiBase}/api/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();

      if (data && data.text) {
        onTranscriptRef.current(data.text.trim());
      }
      setStatus('idle');
      setInterimTranscript('');
    } catch (err) {
      console.error('[Voice] Erreur backend:', err);
      setStatus('error');
      setErrorMessage('La transcription vocale a échoué.');
      setInterimTranscript('');
    }
  };

  const startListening = useCallback(async () => {
    setErrorMessage(null);
    setInterimTranscript('');

    if (useFallback) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          stream.getTracks().forEach((track) => track.stop());
          handleAudioUpload(audioBlob);
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        setStatus('listening');
      } catch (err) {
        setStatus('error');
        setErrorMessage('Accès au microphone refusé.');
      }
    } else {
      if (!recognitionRef.current) return;
      try {
        recognitionRef.current.lang = lang;
        recognitionRef.current.start();
        setStatus('listening');
      } catch (err) {
        console.warn('SpeechRecognition.start() error:', err);
      }
    }
  }, [useFallback, lang]);

  const stopListening = useCallback(() => {
    if (useFallback) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
    } else {
      if (!recognitionRef.current) return;
      try {
        recognitionRef.current.stop();
      } catch {}
      setStatus('idle');
    }
  }, [useFallback]);

  const toggleListening = useCallback(() => {
    if (status === 'listening') {
      stopListening();
    } else {
      startListening();
    }
  }, [status, startListening, stopListening]);

  return {
    isSupported: true,
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
