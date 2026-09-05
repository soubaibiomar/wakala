import { useCallback, useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useVoiceAssistant } from '../../hooks/useVoiceAssistant';
import { chatbotService } from '../../services/chatbotService';
import { ChatBubbleIcon } from './ChatBubbleIcon';
import { ChatPanel } from './ChatPanel';
import { CarResultsPanel } from './CarResultsPanel';
import { recommendationService } from '../../services/recommendationService';
import { vehicleService } from '../../services/vehicleService';
import {
  recommendationClient,
  type Car,
  type ChatLanguage,
  type ChatTurn,
  type RecommendationClient,
  type QuestionOption,
  detectConstraintConflict,
  computeFallback8dScores,
  getUniqueModelCars,
  deduplicateCars,
  informativeRequestPattern,
  alignQuestionOptions,
} from './recommendationClient';
import './recommendation-experience.css';

const SESSION_STORAGE_KEY = 'wakala_recommendation_state';

interface PersistedRecommendationState {
  messages: ChatTurn[];
  language: ChatLanguage | null;
  recommendationActive: boolean;
}

type ExperienceMode = 'launcher' | 'widget' | 'immersive';

function cleanAssistantResponse(response: string): string {
  return response
    .replace(/\b(?:or|ou|and|et)\s+\*{1,2}\s*$/iu, '')
    .replace(/[:\-–]\s*\*{1,2}\s*$/u, '')
    .replace(/\*{1,2}\s*$/u, '')
    .replace(/(?:^|\n)\s*[-*]\s*$/u, '')
    .trim();
}

interface RecommendationExperienceProps {
  client?: RecommendationClient;
  initialCars?: Car[];
}

const DEFAULT_INITIAL_CARS: Car[] = [];

export default function RecommendationExperience({ client = recommendationClient, initialCars = DEFAULT_INITIAL_CARS }: RecommendationExperienceProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const isCatalogue = location.pathname === '/catalogue' || location.pathname === '/admin/catalogue';
  const [mode, setMode] = useState<ExperienceMode>('launcher');
  const [cars, setCars] = useState<Car[]>(initialCars);
  // Keep the complete candidate pool for subsequent answers. `cars` is only
  // the small set rendered in the catalogue, otherwise valid family cars can
  // disappear after the first three semantic-search results.
  const [candidateCars, setCandidateCars] = useState<Car[]>(initialCars);
  const [messages, setMessages] = useState<ChatTurn[]>([]);
  const [language, setLanguage] = useState<ChatLanguage | null>(null);
  const [options, setOptions] = useState<QuestionOption[]>([]);
  const [busy, setBusy] = useState(false);
  const [pendingSearch, setPendingSearch] = useState<string | null>(null);
  const [rangeBounds, setRangeBounds] = useState<{ min: number; max: number; step?: number; label: string } | null>(null);
  const [recommendationActive, setRecommendationActive] = useState(false);

  const [mobileImmersiveTab, setMobileImmersiveTab] = useState<'chat' | 'results'>('chat');
  const resetVersionRef = useRef(0);
  const hasRestoredRef = useRef(false);
  const visibleMessages = deduplicateAssistantQuestions(messages);

  // Restore conversation on page reload (F5) or handoff from ChatbotWidget
  useEffect(() => {
    if (hasRestoredRef.current) return;
    hasRestoredRef.current = true;
    try {
      const raw = typeof window !== 'undefined' ? sessionStorage.getItem(SESSION_STORAGE_KEY) : null;
      if (raw) {
        const parsed = JSON.parse(raw) as PersistedRecommendationState;
        if (parsed.messages && parsed.messages.length > 0) {
          setMessages(parsed.messages);
          if (parsed.language) {
            setLanguage(parsed.language);
            (client as RecommendationClient & { setLanguage?: (value: ChatLanguage) => void }).setLanguage?.(parsed.language);
          }
          if (typeof parsed.recommendationActive === 'boolean') {
            setRecommendationActive(parsed.recommendationActive);
          }
          return;
        }
      }

      // Check for pending intent passed from ChatbotWidget (e.g. from Home or other pages)
      const pendingRaw = typeof window !== 'undefined' ? sessionStorage.getItem('wakala_pending_intent') : null;
      if (pendingRaw) {
        sessionStorage.removeItem('wakala_pending_intent');
        const parsed = JSON.parse(pendingRaw) as { message: string; language?: ChatLanguage };
        if (parsed?.message) {
          const detected = parsed.language || detectLanguage(parsed.message) || 'fr';
          setMode((current) => current === 'immersive' ? current : 'widget');
          setMessages([{ role: 'user', content: parsed.message }]);
          setCandidateCars(initialCars);
          setCars(initialCars.slice(0, 3));
          setOptions([]);
          setPendingSearch(parsed.message);
          setLanguage(detected);
          (client as RecommendationClient & { setLanguage?: (value: ChatLanguage) => void }).setLanguage?.(detected);
        }
      }
    } catch {
      // Storage parsing failed, start fresh
    }
  }, [client, initialCars]);

  // Persist state when conversation advances
  useEffect(() => {
    if (messages.length > 0) {
      try {
        const stateToSave: PersistedRecommendationState = {
          messages,
          language,
          recommendationActive,
        };
        sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(stateToSave));
      } catch {
        // Ignore quota/storage errors
      }
    }
  }, [messages, language, recommendationActive]);

  const resetChat = useCallback(() => {
    try {
      sessionStorage.removeItem(SESSION_STORAGE_KEY);
    } catch {
      // Ignore
    }
    resetVersionRef.current += 1;
    setMessages([]);
    setLanguage(null);
    setOptions([]);
    setRangeBounds(null);
    setPendingSearch(null);
    setRecommendationActive(false);
    setCandidateCars(initialCars);
    setCars(initialCars);
    window.dispatchEvent(new CustomEvent('wakala:recommendation-results', { detail: { reset: true } }));

    // Remove only the assistant's search query. Keep any filters the client
    // may have chosen manually in the catalogue.
    const params = new URLSearchParams(location.search);
    params.delete('q');
    params.delete('query');
    const search = params.toString();
    navigate({ pathname: location.pathname, search: search ? `?${search}` : '' }, { replace: true });
  }, [initialCars, location.pathname, location.search, navigate]);

  const answerGeneral = useCallback(async (message: string, selectedLanguage: ChatLanguage, history: ChatTurn[]) => {
    let response = '';
    try {
      await chatbotService.streamMessage(message, history, (chunk) => { response += chunk; }, undefined, undefined, selectedLanguage);
      const cleanContent = cleanAssistantResponse(response || fallbackHelp(selectedLanguage));
      setMessages((current) => [...current, { role: 'assistant', content: cleanContent }]);
      const extractedOptions = alignQuestionOptions(cleanContent, [], selectedLanguage, candidateCars);
      if (extractedOptions && extractedOptions.length > 0) {
        setOptions(extractedOptions);
        setRecommendationActive(true);
      }
    } catch {
      setMessages((current) => [...current, { role: 'assistant', content: fallbackHelp(selectedLanguage) }]);
    }
  }, [candidateCars]);

  const selectLanguage = useCallback((nextLanguage: ChatLanguage) => {
    setLanguage(nextLanguage);
    const awareClient = client as RecommendationClient & { setLanguage?: (value: ChatLanguage) => void };
    awareClient.setLanguage?.(nextLanguage);
    const greetings: Record<ChatLanguage, string> = isCatalogue ? {
      fr: 'Parfait, vous êtes dans le catalogue. Je vais vous poser quelques questions pour réduire la liste aux voitures les plus adaptées.',
      darija: 'مزيان، نتا دابا فالكتالوغ. غادي نسولك شي أسئلة باش نوصلو للطوموبيلات اللي كيناسبوك أكثر.',
      ar: 'ممتاز، أنت الآن في الكتالوج. سأطرح عليك بعض الأسئلة لتقليص القائمة إلى السيارات الأنسب لك.',
      en: 'Great, you’re in the catalogue. I’ll ask a few questions and narrow the list down to the cars that fit you best.',
    } : {
      fr: 'Bonjour ! Je peux répondre à vos questions et vous aider à trouver la voiture idéale.',
      darija: 'سلام! نقدر نعاونك تلقى الطوموبيل اللي كتناسبك.',
      ar: 'مرحباً! يمكنني الإجابة عن أسئلتك ومساعدتك في العثور على السيارة المناسبة.',
      en: 'Hello! I can answer your questions and help you find the right car.',
    };
    setMessages((current) => current.length ? [...current, { role: 'assistant', content: greetings[nextLanguage] }] : [{ role: 'assistant', content: greetings[nextLanguage] }]);
  }, [client, isCatalogue]);

  const send = useCallback(async (message: string, languageOverride?: ChatLanguage, userMessageAlreadyShown = false) => {
    // Immediately clear options and sliders so chips never linger after clicking or submitting an answer
    setOptions([]);
    setRangeBounds(null);
    const detectedLanguage = detectLanguage(message);
    // Once the user explicitly selected a language, keep the whole
    // questionnaire in that language. Automatic detection is only a
    // fallback for the initial free-text message.
    const activeLanguage = languageOverride || language || detectedLanguage;
    if (!activeLanguage) return;
    if (activeLanguage !== language) {
      setLanguage(activeLanguage);
      const awareClient = client as RecommendationClient & { setLanguage?: (value: ChatLanguage) => void };
      awareClient.setLanguage?.(activeLanguage);
    }
    const nextHistory = userMessageAlreadyShown
      ? messages
      : [...messages, { role: 'user' as const, content: message }];
    if (!userMessageAlreadyShown) setMessages(nextHistory);
    setBusy(true);
    try {
      if (mode === 'widget') {
        const isInformative = informativeRequestPattern.test(message)
          || /\b(?:informations?|infos?|avis\s+sur|que\s+pensez|donne[- ]moi\s+des\s+infos)\b/i.test(message);
        const detectedRecommendation = await client.detectRecommendationIntent(message);
        const isAutomotiveConsultation = /\b(what is|what's|what does|explain|how does|why does|c'est quoi|qu'est[- ]ce que|chnahya|chnhya|chnou|achnahya|achnhya|problem|issue|fault|warning light|maintenance|service|repair|engine|motor|dci|diesel common rail|oil change|brake|brakes|tyre|tire|battery|overheat|consumption|amg)\b|(?:شنو هي|شنو هو|ما هي|ما هو)/i.test(message);
        const isRecommendation = !isInformative && (detectedRecommendation || (recommendationActive && !isAutomotiveConsultation));
        if (!isRecommendation) {
          // Clear any recommendation options so they don't linger under general answers
          setOptions([]);
          setRangeBounds(null);
          // Every automotive answer goes through the API. The complete prior
          // conversation is sent so follow-up questions retain their context.
          await answerGeneral(message, activeLanguage, messages);
          return;
        }
        if (detectedRecommendation) setRecommendationActive(true);
        // A recommendation started from the assistant belongs in the full
        // catalogue view, where the matching vehicles can be browsed.
        if (!isCatalogue) {
          navigate(`/catalogue?q=${encodeURIComponent(message)}`);
        }
        // Keep the catalogue layout visible: filters remain on the left and
        // catalogue vehicles remain in the center while chat sits top-right.
        setMode('widget');
      }
      const isContinuation = /\b(back to|continue|resume|go back|return to|recommendation|recommandation|recommenc|reprendre|retour|toutes? les voitures|tous les v[ée]hicules|all available|show all|wid(?:en)?|[ée]largir|start over)\b/i.test(message)
        || /(?:^|[^\p{L}\p{N}])(نكمل|نرجعو|نعاودو|التوصية|توسيع|إعادة|جميع|ݣاع)(?:$|[^\p{L}\p{N}])/iu.test(message);
      let filtered = isContinuation ? candidateCars : await client.applyAnswer(message, nextHistory, candidateCars);
      // Broad family/use-case requests are discovery starters, not catalogue
      // filters. Preserve the initial catalogue when semantic matching cannot
      // resolve Arabizi such as "tonobile dyal 3a2ila". Strict brand requests
      // still remain strict and may return zero matches.
      const isBroadDiscoveryRequest = /\b(family|famille|familiale|familial|children|kids|3a2ila|l3a2ila)\b|(?:tomobil|tomobile|tonobile)\s+dyal/i.test(message);
      if (!filtered.length && !recommendationActive && isBroadDiscoveryRequest && !candidateCars.length && !initialCars.length) {
        const catalogue = await vehicleService.getVehicles({ page: 1, page_size: 100 });
        filtered = catalogue.items;
      }
      if (!filtered.length && !recommendationActive && isBroadDiscoveryRequest) {
        const discoveryPool = candidateCars.length ? candidateCars : initialCars.length ? initialCars : cars;
        if (discoveryPool.length) filtered = discoveryPool;
      }
      // A range control refines the current shortlist. If the pool is
      // temporarily stale and returns no rows, keep the last valid pool so
      // the questionnaire can continue instead of stopping here.
      const isRangeAnswer = /(?:between|entre|بين)\s*\d[\d\s.,]*\s*(?:and|et|و|[-–])\s*\d[\d\s.,]*/i.test(message);
      if (!filtered.length && candidateCars.length > 0) {
        // If a subsequent subjective preference or transient search returns 0 rows,
        // preserve the prior valid candidate pool instead of wiping out the catalogue.
        filtered = candidateCars;
      }
      if (!filtered.length) {
        // Detect constraint conflict and provide proactive pivot options
        const conflict = detectConstraintConflict(nextHistory, candidateCars.length ? candidateCars : cars);
        if (conflict) {
          setOptions(conflict.options[activeLanguage]);
          setMessages((current) => [
            ...deduplicateAssistantQuestions(current),
            { role: 'assistant', content: conflict.explanation[activeLanguage] },
          ]);
          return;
        }
        // Do not leave the user stranded with an empty catalogue and zero buttons.
        const recoveryOptions: Record<ChatLanguage, QuestionOption[]> = {
          fr: [
            { label: 'Voir tous les véhicules disponibles', value: 'Voir toutes les voitures disponibles' },
            { label: 'Élargir mes critères de recherche', value: 'Élargir les critères' },
            { label: 'Recommencer', value: 'Recommencer' },
          ],
          darija: [
            { label: 'نشوف ݣاع الطوموبيلات المتوفرة', value: 'وريني ݣاع الطوموبيلات' },
            { label: 'نوسع معايير البحث', value: 'نوسع المعايير' },
            { label: 'نعاود من اللول', value: 'نعاود' },
          ],
          ar: [
            { label: 'عرض جميع السيارات المتاحة', value: 'عرض جميع السيارات' },
            { label: 'توسيع معايير البحث', value: 'توسيع المعايير' },
            { label: 'إعادة البدء', value: 'إعادة البدء' },
          ],
          en: [
            { label: 'Show all available vehicles', value: 'Show all available cars' },
            { label: 'Widen search criteria', value: 'Widen criteria' },
            { label: 'Start over', value: 'Start over' },
          ],
        };
        setOptions(recoveryOptions[activeLanguage] || recoveryOptions.fr);
        window.dispatchEvent(new CustomEvent('wakala:recommendation-results', {
          detail: { cars: [], total: 0, empty: true },
        }));
        setMessages((current) => [...deduplicateAssistantQuestions(current), { role: 'assistant', content: noMatchesMessage(activeLanguage) }]);
        return;
      }
      // The number of remaining cars does not mean qualification is complete.
      // A catalogue can legitimately have three matches before the client has
      // answered every preference question, so ask for the next criterion
      // first and only create the final three-car shortlist when there is no
      // question left.
      const question = await client.getNextQuestion(nextHistory, filtered);
      const isFinalRound = !question;
      let finalCars = getUniqueModelCars(filtered, 3);
      if (!finalCars.length) {
        finalCars = filtered.slice(0, 3);
      }
      if (isFinalRound) {
        try {
          const scores = await recommendationService.scoreVehicles8d({
            vehicle_ids: finalCars.map((car) => car.id),
            profile: scoringProfile(nextHistory),
          });
          const scoreById = new Map(scores.map((score) => [score.vehicle_id, score]));
          finalCars = finalCars.map((car) => {
            const score = scoreById.get(car.id);
            return score
              ? {
                  ...car,
                  eight_dimension_scores: score.scores,
                  total_8d_score: score.weighted_total,
                  total_8d_percent: score.weighted_total_percent,
                }
              : car;
          });
        } catch {
          // A scoring outage must not discard an otherwise valid shortlist.
          finalCars = computeFallback8dScores(finalCars, scoringProfile(nextHistory));
        }
      }
      // During discovery, expose the broader compatible set so valid family
      // alternatives are visible while the client answers questions. Once
      // qualification is complete, reduce it to the definitive top three.
      const uniqueVisible = getUniqueModelCars(filtered, 20);
      const visibleCars = isFinalRound ? finalCars : (uniqueVisible.length ? uniqueVisible : filtered.slice(0, 20));
      setCandidateCars(filtered);
      setCars(visibleCars);
      const historyFullText = nextHistory.map((turn) => turn.content).join(' ');
      const extractedFilters = extractFilterSummary(historyFullText);
      window.dispatchEvent(new CustomEvent('wakala:recommendation-results', {
        detail: {
          cars: isFinalRound ? finalCars : filtered,
          total: filtered.length,
          final: isFinalRound,
          filters: extractedFilters,
        },
      }));
      if (isFinalRound) {
        setMobileImmersiveTab('results');
        setOptions([]);
        setRangeBounds(null);
        setMessages((current) => [...deduplicateAssistantQuestions(current), { role: 'assistant', content: finalMatches(activeLanguage, finalCars.length) }]);
      } else {
        setOptions(alignQuestionOptions(question?.question || '', question?.options ?? [], activeLanguage, filtered));
        const questionText = question?.question || nextCriterion(activeLanguage);
        const candidatePrices = filtered
          .map((car) => Number(car.price))
          .filter((price) => Number.isFinite(price) && price > 0);
        const isBudgetQuestion = /budget|prix|price|ميزاني/i.test(questionText);
        let dynamicRange = question?.rangeBounds || null;
        if (isBudgetQuestion && !dynamicRange && candidatePrices.length > 0) {
          const minP = Math.min(...candidatePrices);
          const maxP = Math.max(...candidatePrices);
          const spread = maxP - minP;
          const step = spread > 600000 ? 25000 : spread > 150000 ? 10000 : 5000;
          let min = Math.floor(minP / step) * step;
          let max = Math.ceil(maxP / step) * step;
          if (max <= min || max - min < step * 2) {
            min = Math.max(0, min - step * 2);
            max = max + step * 2;
          }
          dynamicRange = {
            min,
            max,
            step,
            label: activeLanguage === 'en' ? 'Recommended budget' : activeLanguage === 'ar' || activeLanguage === 'darija' ? 'الميزانية الموصى بها' : 'Budget recommandé',
          };
        }
        setRangeBounds(dynamicRange);
        setMessages((current) => appendAssistantQuestion(current, questionText));
      }
    } catch {
      setMessages((current) => [...current, { role: 'assistant', content: retryMessage(activeLanguage) }]);
    } finally {
      setBusy(false);
    }
  }, [answerGeneral, candidateCars, client, isCatalogue, language, messages, mode, navigate, recommendationActive]);

  // The hero search bar and the floating chatbot enter the same conversation.
  // Keep the message pending until the user selects a language first.
  useEffect(() => {
    const handleSearch = (event: Event) => {
      const message = (event as CustomEvent<{ message?: string }>).detail?.message?.trim();
      if (!message) return;
      setMode((current) => current === 'immersive' ? current : 'widget');
        setMessages([{ role: 'user', content: message }]);
        setCandidateCars(initialCars);
        setCars(initialCars.slice(0, 3));
        setOptions([]);
        setPendingSearch(message);
        const detected = detectLanguage(message) || 'fr';
        setLanguage(detected);
        (client as RecommendationClient & { setLanguage?: (value: ChatLanguage) => void }).setLanguage?.(detected);
    };
    window.addEventListener('wakala:recommendation-search', handleSearch);
    return () => window.removeEventListener('wakala:recommendation-search', handleSearch);
  }, [initialCars, client]);

  useEffect(() => {
    const handleOpenChat = () => setMode((current) => current === 'immersive' ? current : 'widget');
    const handleOpenFromHint = () => {
      setMode('widget');
    };
    window.addEventListener('wakala:open-chat', handleOpenChat);
    window.addEventListener('wakala:open-chat-from-hint', handleOpenFromHint);
    return () => {
      window.removeEventListener('wakala:open-chat', handleOpenChat);
      window.removeEventListener('wakala:open-chat-from-hint', handleOpenFromHint);
    };
  }, []);

  useEffect(() => {
    const shouldReserveCatalogueSpace = isCatalogue && mode === 'widget';
    document.body.classList.toggle('catalogue-chat-open', shouldReserveCatalogueSpace);
    return () => document.body.classList.remove('catalogue-chat-open');
  }, [isCatalogue, mode]);

  useEffect(() => {
    if (!language || !pendingSearch) return;
    const message = pendingSearch;
    setPendingSearch(null);
    void send(message, language, true);
  }, [language, pendingSearch, send]);

  const handleVoiceResult = useCallback(async (result: { transcript: string; reply: string; language: ChatLanguage }) => {
    setLanguage(result.language);
    (client as RecommendationClient & { setLanguage?: (value: ChatLanguage) => void }).setLanguage?.(result.language);
    if (!result.transcript) return;
    const isRecommendation = await client.detectRecommendationIntent(result.transcript);
    if (mode === 'widget' && !isRecommendation && result.reply) {
      setMessages((current) => [...current, { role: 'user', content: result.transcript }, { role: 'assistant', content: result.reply }]);
    } else {
      void send(result.transcript);
    }
  }, [client, mode, send]);
  const voice = useVoiceAssistant({ language: language || 'fr', history: messages, onResult: handleVoiceResult });

  const open = () => {
    setMode((current) => current === 'launcher' ? 'widget' : 'launcher');
    window.dispatchEvent(new CustomEvent('wakala:assistant-visibility', { detail: { open: mode === 'launcher' } }));
  };
  const close = useCallback(() => {
    setMode('launcher');
    window.dispatchEvent(new CustomEvent('wakala:assistant-visibility', { detail: { open: false } }));
  }, []);
  return (
    <div className={`recommendation-experience recommendation-experience--${mode}${isCatalogue ? ' recommendation-experience--catalogue' : ''}`}>
      {mode !== 'launcher' && mode !== 'immersive' && (
        <div className="recommendation-experience__widget">
          <ChatPanel
            messages={visibleMessages}
            options={options}
            busy={busy}
            onSend={send}
            language={language}
            onLanguageSelect={selectLanguage}
            onVoiceInput={voice.toggle}
            voiceRecording={voice.recording}
            voiceBusy={voice.busy}
            voiceError={voice.error}
            catalogueMode={isCatalogue}
            rangeBounds={rangeBounds}
            onReset={resetChat}
            onClose={close}
            onRangeSelect={(min, max, label) => language && void send(formatRangeAnswer(language, min, max, label), language)}
          />
        </div>
      )}
      {mode === 'immersive' && (
        <main className="recommendation-experience__immersive">
          <div className="recommendation-experience__mobile-switcher" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={mobileImmersiveTab === 'chat'}
              className={`recommendation-experience__mobile-tab ${mobileImmersiveTab === 'chat' ? 'is-active' : ''}`}
              onClick={() => setMobileImmersiveTab('chat')}
            >
              💬 Conseiller IA
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mobileImmersiveTab === 'results'}
              className={`recommendation-experience__mobile-tab ${mobileImmersiveTab === 'results' ? 'is-active' : ''}`}
              onClick={() => setMobileImmersiveTab('results')}
            >
              🚗 Véhicules ({cars.length})
            </button>
          </div>
          <div className={`recommendation-experience__immersive-panel recommendation-experience__immersive-panel--results ${mobileImmersiveTab === 'results' ? 'is-active' : ''}`}>
            <CarResultsPanel cars={cars} immersive language={language} />
          </div>
          <div className={`recommendation-experience__immersive-panel recommendation-experience__immersive-panel--chat ${mobileImmersiveTab === 'chat' ? 'is-active' : ''}`}>
            <ChatPanel
              messages={visibleMessages}
              options={options}
              busy={busy}
              onSend={send}
              language={language}
              onLanguageSelect={selectLanguage}
              onVoiceInput={voice.toggle}
              voiceRecording={voice.recording}
              voiceBusy={voice.busy}
              voiceError={voice.error}
              catalogueMode={isCatalogue}
              rangeBounds={rangeBounds}
              onReset={resetChat}
              onClose={close}
              onRangeSelect={(min, max, label) => language && void send(formatRangeAnswer(language, min, max, label), language)}
            />
          </div>
        </main>
      )}
      {mode !== 'immersive' && <ChatBubbleIcon open={mode === 'widget'} onClick={open} hasActiveConversation={messages.length > 0} />}
    </div>
  );
}

function detectLanguage(message: string): ChatLanguage | null {
  if (/[؀-ۿ]/.test(message)) return /(?:شنو|بغيت|واش|طوموبيل|ديال|فين)/i.test(message) ? 'darija' : 'ar';
  if (/\b(?:tomobil|tomobile|tonobile|tomobila|dyal|3a2ila|bghit|baghi|ch7al|fin|wach|salam|labas)\b/i.test(message)) return 'darija';
  if (/\b(the|what|which|want|need|car|budget|recommend)\b/i.test(message)) return 'en';
  if (/[àâçéèêëîïôùûüÿœ]|\b(je|cherche|voiture|budget|bonjour|merci|quel)\b/i.test(message)) return 'fr';
  return null;
}

function scoringProfile(history: ChatTurn[]): { usage?: string; priorities: string[] } {
  const text = history
    .filter((turn) => turn.role === 'user')
    .map((turn) => turn.content)
    .join(' ')
    .toLowerCase();
  const priorities: string[] = [];
  if (/safe|safety|security|sécurité|ncap|السلامة|آمن/i.test(text)) priorities.push('securite');
  if (/space|trunk|boot|luggage|suitcase|coffre|bagages|family|famille|حقائب|العائلة/i.test(text)) priorities.push('espace');
  if (/econom|consumption|consommation|cost|coût|conso|استهلاك/i.test(text)) priorities.push('cout_reel');
  if (/performance|power|puissance|acceleration|sport|قوية/i.test(text)) priorities.push('performance');
  if (/hybrid|electric|électrique|ecolog|co2|بيئي/i.test(text)) priorities.push('ecologie');
  if (/4x4|awd|off.?road|terrain|motricité|دفع رباعي/i.test(text)) priorities.push('motricite');

  let usage: string | undefined;
  if (/mostly city|city driving|ville|urbain|commut|مدينة/i.test(text)) usage = 'ville';
  else if (/mostly highway|highway|autoroute|motorway|long trip|طريق/i.test(text)) usage = 'route';
  else if (/both|mixed|mixte|بجوج|مخلط/i.test(text)) usage = 'mixte';

  return { usage, priorities: [...new Set(priorities)] };
}

function fallbackHelp(language: ChatLanguage): string {
  return { fr: 'Je peux vous aider à choisir une voiture, comparer des modèles ou estimer un budget.', darija: 'نقدر نعاونك تختار طوموبيل، تقارن الموديلات، ولا نحسب ليك الميزانية.', ar: 'يمكنني مساعدتك في اختيار سيارة أو مقارنة الطرازات أو تقدير الميزانية.', en: 'I can help you choose a car, compare models, or estimate a budget.' }[language];
}

function finalMatches(language: ChatLanguage, count: number): string {
  return {
    fr: `Voici vos ${count} meilleurs matchs. Je les ai classés selon vos priorités.`,
    darija: `هادو هما أحسن ${count} اختيارات ليك، مرتبين على حساب الأولويات ديالك.`,
    ar: `هذه أفضل ${count} سيارات مناسبة لك، مرتبة حسب أولوياتك.`,
    en: `Here are your ${count} best matches, ranked by your priorities.`,
  }[language];
}

function noMatchesMessage(language: ChatLanguage): string {
  return {
    fr: 'Aucun véhicule ne correspond à tous ces critères. Élargissez la fourchette pour continuer.',
    darija: 'Ma kayna 7ta tomobil katnasab m3a had les critères كاملين. Wesse3 chwiya l-fourchette bach nkemlo.',
    ar: 'لا توجد سيارة تطابق جميع هذه المعايير. وسّع النطاق قليلاً للمتابعة.',
    en: 'No vehicles match all of these criteria. Widen the range slightly to continue.',
  }[language];
}



function nextCriterion(language: ChatLanguage): string {
  return { fr: 'Quel critère compte le plus pour vous ?', darija: 'شنو هو المعيار اللي مهم أكثر بالنسبة ليك؟', ar: 'ما هو المعيار الأهم بالنسبة لك؟', en: 'Which criterion matters most to you?' }[language];
}

function formatRangeAnswer(language: ChatLanguage, min: number, max: number, label: string): string {
  const isBudget = /budget|ميزاني/i.test(label);
  if (language === 'fr') return isBudget ? `budget entre ${min} et ${max} MAD` : `${label} entre ${min} et ${max}`;
  if (language === 'ar') return isBudget ? `الميزانية بين ${min} و${max} درهم` : `${label} بين ${min} و${max}`;
  if (language === 'darija') return isBudget ? `الميزانية بين ${min} و${max} درهم` : `${label} بين ${min} و${max}`;
  return isBudget ? `budget between ${min} and ${max} MAD` : `${label} between ${min} and ${max}`;
}

function retryMessage(language: ChatLanguage): string {
  return { fr: 'Je n’ai pas pu actualiser la sélection. Réessayez dans un instant.', darija: 'ماقدرتش نحدّث ليك الاختيارات. عاود جرّب من بعد شوية.', ar: 'تعذر تحديث الاختيارات. حاول مرة أخرى بعد قليل.', en: 'I could not refresh the selection. Please try again shortly.' }[language];
}

function deduplicateAssistantQuestions(messages: ChatTurn[]): ChatTurn[] {
  const seen = new Set<string>();
  return messages.filter((message) => {
    if (message.role !== 'assistant' || !/[?؟]\s*$/.test(message.content.trim())) return true;
    const key = message.content.trim();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function appendAssistantQuestion(messages: ChatTurn[], question: string): ChatTurn[] {
  const deduplicated = deduplicateAssistantQuestions(messages);
  const alreadyShown = deduplicated.some((message) => message.role === 'assistant' && message.content.trim() === question.trim());
  return alreadyShown ? deduplicated : [...deduplicated, { role: 'assistant', content: question }];
}

function extractFilterSummary(text: string): Record<string, any> {
  const norm = text.toLowerCase();
  const filters: Record<string, any> = {};
  if (/\b(diesel|gazoil|mazout)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])مازوط(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.fuel_type = 'diesel';
  else if (/\b(essence|petrol)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])بنزين(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.fuel_type = 'essence';
  else if (/\b(hybride rechargeable|phev)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])(هجين قابلة? للشحن|إيبريد ريشارجابل)(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.fuel_type = 'hybride_rechargeable';
  else if (/\b(hybrid|hybride)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])هجين(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.fuel_type = 'hybride';
  else if (/\b(electric|electrique|ev)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])(كهربائي|كهربائ)(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.fuel_type = 'electrique';

  if (/\b(suv|4x4)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])دفع رباعي(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.body_type = 'suv';
  else if (/\b(citadine|hatchback)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])(سيتادين|صغيرة)(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.body_type = 'citadine';
  else if (/\b(berline|sedan)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])سيدان(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.body_type = 'berline';
  else if (/\b(monospace|van)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])(مونوسباس|فان)(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.body_type = 'monospace';
  else if (/\b(coupe|coupé)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])(كوبيه|كوبي)(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.body_type = 'coupe';
  else if (/\b(pickup|pick-up|pick up)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])(بيك ?أب|بيك ?اب)(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.body_type = 'pick_up';

  if (/\b(automatique|auto|bva)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])(اوتوماتيك|أوتوماتيك)(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.transmission = 'automatique';
  else if (/\b(manuelle|bvm)\b/i.test(norm) || /(?:^|[^\p{L}\p{N}])يدوي(?:$|[^\p{L}\p{N}])/iu.test(norm)) filters.transmission = 'manuelle';

  const budget = norm.match(/(?:max|plafond|budget|moins de|تحت|أقل من|حتى ل)\s*(\d[\d\s.,]*)\s*(?:mad|dh|درهم)?/iu);
  if (budget) {
    const val = Number(budget[1].replace(/[\s.,]/g, ''));
    if (Number.isFinite(val) && val > 0) filters.price_max = val;
  }
  return filters;
}


