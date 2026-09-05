import { FormEvent, useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { RefreshCw, X, ChevronDown, ChevronUp } from 'lucide-react';
import { LANGUAGE_OPTIONS, type ChatLanguage, type ChatTurn, type QuestionOption, extractBrandPreference, getBrandFallbackBudgetRange } from './recommendationClient';

const FALLBACK_BUDGET_RANGE = { min: 80000, max: 600000, step: 5000, label: 'Budget recommandé' };

interface ChatPanelProps {
  messages: ChatTurn[];
  options: QuestionOption[];
  busy?: boolean;
  onSend: (message: string) => void;
  language: ChatLanguage | null;
  onLanguageSelect: (language: ChatLanguage) => void;
  onVoiceInput?: () => void;
  voiceRecording?: boolean;
  voiceBusy?: boolean;
  voiceError?: string | null;
  catalogueMode?: boolean;
  rangeBounds?: { min: number; max: number; step?: number; label: string } | null;
  onRangeSelect?: (min: number, max: number, label: string) => void;
  onReset?: () => void;
  onClose?: () => void;
  isMinimized?: boolean;
  onToggleMinimize?: () => void;
  candidateCount?: number;
}

export function ChatPanel({
  messages,
  options,
  busy = false,
  onSend,
  language,
  onLanguageSelect,
  onVoiceInput,
  voiceRecording = false,
  voiceBusy = false,
  voiceError,
  catalogueMode = false,
  rangeBounds,
  onRangeSelect,
  onReset,
  onClose,
  isMinimized = false,
  onToggleMinimize,
  candidateCount,
}: ChatPanelProps) {
  const [draft, setDraft] = useState('');
  const [budgetMin, setBudgetMin] = useState(0);
  const [budgetMax, setBudgetMax] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const endRef = useRef<HTMLDivElement>(null);
  const lastAssistantIndex = messages.map((m) => m.role).lastIndexOf('assistant');
  const lastAssistantMessage = lastAssistantIndex >= 0 ? messages[lastAssistantIndex].content : '';
  const hasUserRepliedToLastAssistant = lastAssistantIndex >= 0 && messages.slice(lastAssistantIndex + 1).some((m) => m.role === 'user');
  const isMultiSelectQuestion = /what matters most|which priorities|top priority|quelle est votre priorit[ée]|priorit[ée].*(?:compte|important)|ما الأولوية|الأولوية|أولوية|أولويتكم|awlawiya/i.test(lastAssistantMessage);
  const mentionedBrand = extractBrandPreference(messages.map((m) => m.content).join(' '));
  const fallbackBounds = mentionedBrand ? getBrandFallbackBudgetRange(mentionedBrand.name) : FALLBACK_BUDGET_RANGE;
  const isDirectBudgetQuestion = (
    /(?:quel(?:le)?\s+est\s+votre\s+budget|what\s+is\s+your\s+(?:maximum\s+)?budget|شحال\s+هي\s+الميزانية|ما\s+هي\s+ميزانيتك)/i.test(lastAssistantMessage)
    || (/budget\s+(?:maximum|recommand[ée]|d['’]investissement)/i.test(lastAssistantMessage) && /\?|؟/.test(lastAssistantMessage))
  ) && lastAssistantMessage.length < 250;

  // Keep the fallback object stable. Recreating it on every render caused
  // the synchronization effect below to reset the sliders after every drag.
  // Respect rangeBounds when passed (including null). Only use fallbackBounds if
  // rangeBounds is undefined, the user hasn't already replied, no options exist,
  // and the assistant explicitly asked a direct budget qualification question.
  const effectiveRangeBounds = rangeBounds !== undefined
    ? rangeBounds
    : (!hasUserRepliedToLastAssistant && options.length === 0 && isDirectBudgetQuestion
      ? fallbackBounds
      : null);
  const isBudgetRange = Boolean(effectiveRangeBounds && /budget|ميزاني/i.test(effectiveRangeBounds.label));
  const isSuitcaseRange = Boolean(effectiveRangeBounds && /suitcase|valise|حقائب|فاليزات/i.test(effectiveRangeBounds.label));
  const rangeUnit = isBudgetRange
    ? 'MAD'
    : isSuitcaseRange
      ? language === 'fr'
        ? 'valises'
        : language === 'darija'
          ? 'فاليزات'
          : language === 'ar'
            ? 'حقائب'
            : 'suitcases'
      : '';
  const localizedRangeLabel = effectiveRangeBounds ? rangeLabel(effectiveRangeBounds.label, language || 'fr') : '';
  const rangeNumberLocale = language === 'en' ? 'en-US' : language === 'ar' ? 'ar-MA' : 'fr-MA';
  const isRtl = language === 'ar' || (language === 'darija' && /[\u0600-\u06ff]/.test(lastAssistantMessage));
  // Use the bounds supplied by the recommendation client, even for a narrow
  // brand-specific price band. Falling back to a global threshold made a
  // Mercedes (or any other brand) request show unrelated catalogue prices.
  const showRangeSlider = Boolean(effectiveRangeBounds && effectiveRangeBounds.max > effectiveRangeBounds.min && (isBudgetRange ? true : isSuitcaseRange ? effectiveRangeBounds.max - effectiveRangeBounds.min > 2 : effectiveRangeBounds.max - effectiveRangeBounds.min > 150));

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, busy]);
  useEffect(() => {
    if (effectiveRangeBounds) {
      setBudgetMin((current) => current === effectiveRangeBounds.min ? current : effectiveRangeBounds.min);
      setBudgetMax((current) => current === effectiveRangeBounds.max ? current : effectiveRangeBounds.max);
    }
  }, [effectiveRangeBounds?.min, effectiveRangeBounds?.max, effectiveRangeBounds?.step, effectiveRangeBounds?.label]);
  useEffect(() => {
    setSelectedOptions([]);
  }, [lastAssistantMessage, options]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const value = draft.trim();
    if (!value || busy) return;
    setDraft('');
    onSend(value);
  };

  return (
    <section className="recommendation-experience__chat" dir={isRtl ? 'rtl' : 'ltr'} aria-label={assistantAriaLabel(language)}>
      <header 
        className="recommendation-experience__titlebar"
        onClick={isMinimized && onToggleMinimize ? onToggleMinimize : undefined}
        style={isMinimized ? { cursor: 'pointer' } : undefined}
      >
        <div className="recommendation-experience__drag-handle" aria-hidden="true" />
        <div className="recommendation-experience__header-main">
          <div className="recommendation-experience__avatar" aria-hidden="true"><img src="/assets/chatlogo.png" alt="Wakala" /></div>
          <div className="recommendation-experience__identity">
            <div className="recommendation-experience__identity-title-row">
              <strong>{assistantTitle(language)}</strong>
              {!isMinimized && (
                <span className="recommendation-experience__status"><i aria-hidden="true" /> <span>{onlineLabel(language)}</span></span>
              )}
            </div>
            <small>{isMinimized ? expandLabel(language) : assistantSubtitle(language)}</small>
          </div>
          <div className="recommendation-experience__header-actions">
            {onToggleMinimize && (
              <button
                type="button"
                className="recommendation-experience__minimize-btn"
                onClick={(e) => { e.stopPropagation(); onToggleMinimize(); }}
                aria-label={isMinimized ? expandLabel(language) : minimizeLabel(language, candidateCount)}
                title={isMinimized ? expandLabel(language) : minimizeLabel(language, candidateCount)}
              >
                {isMinimized ? <ChevronUp size={15} aria-hidden="true" /> : <ChevronDown size={15} aria-hidden="true" />}
                <span className="recommendation-experience__minimize-text">
                  {isMinimized ? 'Ouvrir' : minimizeLabel(language, candidateCount)}
                </span>
              </button>
            )}
            {!isMinimized && onReset && <button type="button" className="recommendation-experience__reset" onClick={onReset} disabled={busy} aria-label={resetLabel(language)} title={resetLabel(language)}><RefreshCw size={14} aria-hidden="true" /></button>}
            {onClose && <button type="button" className="recommendation-experience__close" onClick={(e) => { e.stopPropagation(); onClose(); }} aria-label={closeLabel(language)} title={closeLabel(language)}><X size={16} aria-hidden="true" /></button>}
          </div>
        </div>
      </header>
      {!isMinimized && (
        <>
          <div className="recommendation-experience__messages" aria-live="polite">
        {!messages.length && !busy && <div className="recommendation-experience__welcome" aria-hidden="true"><span>✦</span><strong>{catalogueMode ? catalogueWelcomeTitle(language) : 'Trouvez la voiture qui vous ressemble'}</strong><p>{catalogueMode ? catalogueWelcomeText(language) : 'Répondez naturellement. Je m’adapte à votre langue et à vos besoins.'}</p></div>}
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`recommendation-experience__message recommendation-experience__message--${message.role}`}>
            {message.role === 'assistant' ? (
              <div className="recommendation-experience__message-markdown">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
              </div>
            ) : message.content}
          </div>
        ))}
        {busy && (
          <div className="recommendation-experience__message recommendation-experience__message--assistant recommendation-experience__typing" aria-label={typingLabel(language)}>
            <span className="recommendation-experience__typing-label">{typingLabel(language)}</span>
            <span className="recommendation-experience__typing-dots" aria-hidden="true"><i /><i /><i /></span>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div className="recommendation-experience__controls">
        {!language && !busy && (
          <div className="recommendation-experience__language-choices" aria-label="Choisissez votre langue">
            <span className="recommendation-experience__control-label">{languageChoiceLabel(language)}</span>
            {LANGUAGE_OPTIONS.map((option) => <button key={option.value} onClick={() => onLanguageSelect(option.value)}>{option.nativeLabel}</button>)}
          </div>
        )}
        {language && options.length > 0 && !busy && (!effectiveRangeBounds || !showRangeSlider) && (
          <div className="recommendation-experience__chips" aria-label="Réponses rapides">
            {options.map((option) => {
              const optionValue = option.value || option.label;
              const isSelected = selectedOptions.includes(optionValue);
              return (
                <button
                  key={`${option.label}-${option.value}`}
                  type="button"
                  className={isMultiSelectQuestion && isSelected ? 'is-selected' : ''}
                  aria-pressed={isMultiSelectQuestion ? isSelected : undefined}
                  disabled={busy}
                  onClick={() => {
                    if (!isMultiSelectQuestion) {
                      onSend(optionValue);
                      return;
                    }
                    setSelectedOptions((current) => current.includes(optionValue)
                      ? current.filter((value) => value !== optionValue)
                      : [...current, optionValue]);
                  }}
                >
                  {option.label}
                </button>
              );
            })}
            {isMultiSelectQuestion && selectedOptions.length > 0 && (
              <button
                type="button"
                className="recommendation-experience__chips-confirm"
                onClick={() => {
                  onSend(selectedOptions.join(', '));
                  setSelectedOptions([]);
                }}
              >
                {confirmSelectionLabel(language)}
              </button>
            )}
          </div>
        )}
        {language && effectiveRangeBounds && showRangeSlider && !busy && onRangeSelect && (
          <div className="recommendation-experience__budget-range" dir="ltr" aria-label={localizedRangeLabel}>
            <div className="recommendation-experience__budget-range-heading" style={isRtl ? { direction: 'rtl' } : undefined}><span>{localizedRangeLabel}</span><strong>{rangeUnit} {budgetMin.toLocaleString(rangeNumberLocale)} – {budgetMax.toLocaleString(rangeNumberLocale)}</strong></div>
            <div className="recommendation-experience__budget-range-inputs">
              <span style={isRtl ? { textAlign: 'start' } : undefined}>{rangeMinLabel(language)}</span>
              <span style={isRtl ? { textAlign: 'end' } : { textAlign: 'end' }}>{rangeMaxLabel(language)}</span>
              <div className="recommendation-experience__budget-track">
                <span className="recommendation-experience__budget-track-fill" style={{ left: `${((budgetMin - effectiveRangeBounds.min) / (effectiveRangeBounds.max - effectiveRangeBounds.min)) * 100}%`, right: `${100 - ((budgetMax - effectiveRangeBounds.min) / (effectiveRangeBounds.max - effectiveRangeBounds.min)) * 100}%` }} />
                <input aria-label={rangeMinLabel(language)} type="range" min={effectiveRangeBounds.min} max={effectiveRangeBounds.max} step={effectiveRangeBounds.step || 5000} value={budgetMin} onChange={(event) => setBudgetMin(Math.min(Number(event.target.value), budgetMax))} onInput={(event) => setBudgetMin(Math.min(Number(event.currentTarget.value), budgetMax))} />
                <input aria-label={rangeMaxLabel(language)} type="range" min={effectiveRangeBounds.min} max={effectiveRangeBounds.max} step={effectiveRangeBounds.step || 5000} value={budgetMax} onChange={(event) => setBudgetMax(Math.max(Number(event.target.value), budgetMin))} onInput={(event) => setBudgetMax(Math.max(Number(event.currentTarget.value), budgetMin))} />
              </div>
            </div>
            <button type="button" onClick={() => onRangeSelect(budgetMin, budgetMax, effectiveRangeBounds.label)}>{rangeConfirmLabel(language)}</button>
          </div>
        )}
        <form className="recommendation-experience__composer" onSubmit={submit}>
          <input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder={language ? responsePlaceholder(language) : languageChoiceLabel(language)} aria-label={responseAriaLabel(language)} disabled={busy || !language} />
          {language && onVoiceInput && <button type="button" className={voiceRecording ? 'is-recording' : ''} onClick={onVoiceInput} disabled={busy || voiceBusy} aria-label={voiceRecording ? 'Arrêter l’enregistrement' : 'Répondre avec le microphone'}>{voiceBusy ? '…' : voiceRecording ? '■' : '🎙'}</button>}
          <button type="submit" disabled={!draft.trim() || busy} aria-label="Envoyer">↑</button>
        </form>
        <p className="recommendation-experience__hint">{voiceError || (language ? languageHint(language) : languageChoiceLabel(language))}</p>
      </div>
        </>
      )}
    </section>
  );
}

function typingLabel(language: ChatLanguage | null): string {
  return {
    en: 'I’m preparing your answer',
    ar: 'أحضّر إجابتك',
    darija: 'كنوجد ليك الجواب',
    fr: 'Je prépare votre réponse',
  }[language || 'fr'];
}

function assistantTitle(language: ChatLanguage | null): string {
  return { en: 'Wakala Assistant', fr: 'Assistant Wakala', ar: 'مساعد وكالة', darija: 'مساعد وكالة' }[language || 'fr'];
}

function assistantAriaLabel(language: ChatLanguage | null): string {
  return { en: 'Wakala automotive advisor', fr: 'Conseiller automobile Wakala', ar: 'مستشار السيارات في وكالة', darija: 'المستشار ديال السيارات فوكالة' }[language || 'fr'];
}

function assistantSubtitle(language: ChatLanguage | null): string {
  return { en: 'Your automotive advisor', fr: 'Votre conseiller automobile', ar: 'مستشارك في السيارات', darija: 'المستشار ديالك فالطوموبيلات' }[language || 'fr'];
}

function onlineLabel(language: ChatLanguage | null): string {
  return { en: 'Online', fr: 'En ligne', ar: 'متصل', darija: 'متصل' }[language || 'fr'];
}

function resetLabel(language: ChatLanguage | null): string {
  return { en: 'Refresh assistant', fr: 'Réinitialiser l’assistant', ar: 'إعادة تشغيل المساعد', darija: 'عاود بدا المساعد' }[language || 'fr'];
}

function languageChoiceLabel(language: ChatLanguage | null): string {
  return { en: 'Choose your language', fr: 'Choisissez votre langue', ar: 'اختر لغتك', darija: 'ختار اللغة ديالك' }[language || 'fr'];
}

function responsePlaceholder(language: ChatLanguage): string {
  return { en: 'Type your answer…', fr: 'Écrivez votre réponse…', ar: 'اكتب إجابتك…', darija: 'كتب الجواب ديالك…' }[language];
}

function responseAriaLabel(language: ChatLanguage | null): string {
  return { en: 'Your answer', fr: 'Votre réponse', ar: 'إجابتك', darija: 'الجواب ديالك' }[language || 'fr'];
}

function languageHint(language: ChatLanguage): string {
  return { en: 'You can change language at any time.', fr: 'Vous pouvez changer de langue à tout moment.', ar: 'يمكنك تغيير اللغة في أي وقت.', darija: 'تقدر تبدل اللغة ف أي وقت.' }[language];
}

function confirmSelectionLabel(language: ChatLanguage | null): string {
  return language === 'en' ? 'Continue' : 'Confirmer';
}

function rangeLabel(label: string, language: ChatLanguage): string {
  if (!/budget catalogue/i.test(label)) return label;
  return {
    en: 'Catalogue budget',
    fr: 'Budget catalogue',
    ar: 'ميزانية الكتالوج',
    darija: 'الميزانية ديال الكتالوج',
  }[language];
}

function rangeMinLabel(language: ChatLanguage): string {
  return { en: 'Min', fr: 'Min', ar: 'الحد الأدنى', darija: 'الأدنى' }[language];
}

function rangeMaxLabel(language: ChatLanguage): string {
  return { en: 'Max', fr: 'Max', ar: 'الحد الأقصى', darija: 'الأقصى' }[language];
}

function rangeConfirmLabel(language: ChatLanguage): string {
  return {
    en: 'Use this range',
    fr: 'Utiliser cette fourchette',
    ar: 'استخدم هذا النطاق',
    darija: 'استعمل هاد النطاق',
  }[language];
}

function catalogueWelcomeTitle(language: ChatLanguage | null): string {
  return {
    en: 'Let’s find the cars that suit you best',
    fr: 'Trouvons les voitures qui vous correspondent',
    ar: 'لنجد السيارات التي تناسبك أكثر',
    darija: 'نقلبو على الطوموبيلات اللي كيناسبوك أكثر',
  }[language || 'fr'];
}

function catalogueWelcomeText(language: ChatLanguage | null): string {
  return {
    en: 'I’ll ask a few questions and narrow the catalogue down to the cars that fit your needs.',
    fr: 'Je vais vous poser quelques questions pour réduire le catalogue aux voitures adaptées à vos besoins.',
    ar: 'سأطرح عليك بعض الأسئلة لتقليص القائمة إلى السيارات التي تناسب احتياجاتك.',
    darija: 'غادي نسولك شي أسئلة باش نقصّو الكاتالوغ للطوموبيلات اللي كيناسبوك.',
  }[language || 'fr'];
}

function closeLabel(language: ChatLanguage | null): string {
  return {
    fr: 'Fermer',
    darija: 'سد',
    ar: 'إغلاق',
    en: 'Close',
  }[language || 'fr'];
}

function minimizeLabel(language: ChatLanguage | null, count?: number): string {
  const c = typeof count === 'number' && count > 0 ? ` (${count})` : '';
  if (language === 'en') return `Cars${c}`;
  if (language === 'ar') return `السيارات${c}`;
  if (language === 'darija') return `السيارات${c}`;
  return `Véhicules${c}`;
}

function expandLabel(language: ChatLanguage | null): string {
  if (language === 'en') return 'Tap to open assistant';
  if (language === 'ar') return 'اضغط لفتح المساعد';
  if (language === 'darija') return 'برك باش تفتح المساعد';
  return 'Appuyez pour ouvrir l’assistant';
}

