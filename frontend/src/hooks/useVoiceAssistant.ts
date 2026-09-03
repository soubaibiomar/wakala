import { useCallback, useEffect, useRef, useState } from 'react';
import { getSessionToken } from '../services/api';
import type { ChatLanguage, ChatTurn } from '../components/recommendation-experience/recommendationClient';

interface UseVoiceAssistantOptions {
  language: ChatLanguage;
  history: ChatTurn[];
  onResult: (result: { transcript: string; reply: string; language: ChatLanguage }) => void;
}

export function useVoiceAssistant({ language, history, onResult }: UseVoiceAssistantOptions) {
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const onResultRef = useRef(onResult);
  useEffect(() => { onResultRef.current = onResult; }, [onResult]);
  useEffect(() => () => streamRef.current?.getTracks().forEach((track) => track.stop()), []);

  const processRecording = useCallback(async (blob: Blob) => {
    setBusy(true); setError(null);
    try {
      const form = new FormData();
      form.append('audio', blob, 'wakala-voice.webm');
      form.append('language', language);
      form.append('history_json', JSON.stringify(history.slice(-30)));
      const configuredBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
      const endpoint = configuredBase.endsWith('/api') ? `${configuredBase}/voice/assistant` : `${configuredBase}/api/voice/assistant`;
      const token = getSessionToken();
      const response = await fetch(endpoint, { method: 'POST', body: form, headers: token ? { Authorization: `Bearer ${token}` } : undefined });
      if (!response.ok) throw new Error('voice-request-failed');
      const data = await response.json() as { text?: string; reply?: string; language?: ChatLanguage; audio_base64?: string | null };
      const detectedLanguage = data.language && ['fr', 'darija', 'ar', 'en'].includes(data.language) ? data.language : language;
      onResultRef.current({ transcript: data.text?.trim() || '', reply: data.reply?.trim() || '', language: detectedLanguage });
      if (data.audio_base64) await new Audio(`data:audio/mpeg;base64,${data.audio_base64}`).play().catch(() => undefined);
      else if (data.reply && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(data.reply);
        utterance.lang = detectedLanguage === 'ar' || detectedLanguage === 'darija' ? 'ar-MA' : `${detectedLanguage}-MA`;
        window.speechSynthesis.speak(utterance);
      }
    } catch { setError('La réponse vocale est indisponible pour le moment.'); }
    finally { setBusy(false); }
  }, [history, language]);

  const toggle = useCallback(async () => {
    if (busy) return;
    if (recording) { recorderRef.current?.stop(); return; }
    try {
      if (!navigator.mediaDevices?.getUserMedia || !('MediaRecorder' in window)) throw new Error('unsupported');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream); chunksRef.current = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunksRef.current.push(event.data); };
      recorder.onstop = () => { stream.getTracks().forEach((track) => track.stop()); streamRef.current = null; setRecording(false); void processRecording(new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })); };
      recorderRef.current = recorder; streamRef.current = stream; recorder.start(); setRecording(true);
    } catch { setError('Accès au microphone refusé ou non disponible.'); }
  }, [busy, processRecording, recording]);

  return { recording, busy, error, toggle };
}
