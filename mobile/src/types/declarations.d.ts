declare module '@react-native-voice/voice' {
  export interface SpeechResultsEvent {
    value?: string[];
  }
  export interface SpeechErrorEvent {
    error?: {
      message?: string;
      code?: string;
    };
  }

  interface VoiceStatic {
    onSpeechStart?: () => void;
    onSpeechRecognized?: () => void;
    onSpeechEnd?: () => void;
    onSpeechError?: (e: SpeechErrorEvent) => void;
    onSpeechResults?: (e: SpeechResultsEvent) => void;
    onSpeechPartialResults?: (e: SpeechResultsEvent) => void;
    start: (locale: string) => Promise<void>;
    stop: () => Promise<void>;
    destroy: () => Promise<void>;
    removeAllListeners: () => void;
    isAvailable: () => Promise<0 | 1>;
  }

  const Voice: VoiceStatic;
  export default Voice;
}
