# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Any, AsyncIterable

import re
import json
import asyncio
import httpx
from typing import AsyncIterable, List, Dict, Any, Optional
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    class ChatOpenAI:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def bind(self, *args: Any, **kwargs: Any) -> Any: return self
    class SystemMessage:  # type: ignore[no-redef]
        def __init__(self, content: str): self.content = content
    class HumanMessage(SystemMessage): pass  # type: ignore[no-redef]
    class AIMessage(SystemMessage): pass    # type: ignore[no-redef]
    class ChatPromptTemplate:  # type: ignore[no-redef]
        @classmethod
        def from_messages(cls, messages: list[Any]) -> "ChatPromptTemplate":
            instance = cls()
            instance.messages = messages
            return instance

try:
    from qdrant_client import models as qmodels
except ImportError:
    qmodels = None  # type: ignore[assignment]

from app.core.config import settings
from app.services.ai.qdrant import get_qdrant_client

async def _stream_openrouter_direct(messages_payload: list[dict], fallback_text: str, detected_lang: str = "french", query_text: str = "") -> AsyncIterable[str]:
    """Stream des tokens depuis Groq puis OpenRouter de façon hautement résiliente avec fallback garanti."""
    yielded_any = False

    # 1. Priorité à Groq ultra-rapide (< 1s) si clé configurée
    groq_key = getattr(settings, "GROQ_API_KEY", None)
    if groq_key:
        groq_models = getattr(settings, "GROQ_MODELS", [
            getattr(settings, "GROQ_MODEL", "openai/gpt-oss-120b"),
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
        ])
        groq_headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
        }
        for g_model in groq_models:
            if yielded_any:
                break
            groq_payload = {
                "model": g_model,
                "messages": messages_payload,
                "stream": True,
                "temperature": 0.2,
                "max_tokens": 400,
            }
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=3.0)) as groq_client:
                    async with groq_client.stream("POST", "https://api.groq.com/openai/v1/chat/completions", json=groq_payload, headers=groq_headers) as groq_res:
                        if groq_res.status_code == 200:
                            async for line in groq_res.aiter_lines():
                                if line.startswith("data: "):
                                    data_str = line[6:].strip()
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        data = json.loads(data_str)
                                        delta = data["choices"][0].get("delta", {}).get("content", "")
                                        if delta:
                                            yielded_any = True
                                            yield delta
                                    except Exception:
                                        pass
                            if yielded_any:
                                return
                        else:
                            print(f"[Groq Status {groq_res.status_code} on {g_model}]")
            except Exception as ge:
                print(f"[Groq Exception on {g_model}: {ge}]")

    # 2. OpenRouter provider
    openrouter_key = getattr(settings, "OPENROUTER_API_KEY", None)
    if not yielded_any and openrouter_key:
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "HTTP-Referer": "https://wakala.ma",
            "X-Title": "Wakala Platform",
            "Content-Type": "application/json",
        }
        payload = {
            "models": getattr(settings, "OPENROUTER_MODELS", ["minimax/minimax-m3:free", "z-ai/glm-5.2:free", "liquid/lfm-2.5-2.6b:free"]),
            "messages": messages_payload,
            "stream": True,
            "temperature": 0.2,
            "max_tokens": 400,
            "reasoning": {"exclude": True},
        }
        url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(14.0, connect=4.0)) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    delta = data["choices"][0].get("delta", {}).get("content", "")
                                    if delta:
                                        yielded_any = True
                                        yield delta
                                except Exception:
                                    pass
                    else:
                        print(f"[OpenRouter Status {response.status_code}]")
        except Exception as e:
            print(f"[OpenRouter Stream Exception: {e}]")

    # 3. Knowledge fallback or text fallback
    if not yielded_any:
        knowledge = get_automotive_knowledge_fallback(detected_lang, query_text)
        yield knowledge if knowledge else fallback_text

def get_llm():
    groq_key = getattr(settings, "GROQ_API_KEY", None)
    if groq_key:
        return ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            model=getattr(settings, "GROQ_MODEL", "openai/gpt-oss-120b"),
            api_key=groq_key,
            temperature=0.2,
            max_tokens=450,
            request_timeout=15.0,
            timeout=15.0,
        )
    if getattr(settings, "OPENROUTER_API_KEY", None):
        return ChatOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            model=settings.OPENROUTER_MODEL,
            extra_body={"models": settings.OPENROUTER_MODELS},
            api_key=settings.OPENROUTER_API_KEY,
            temperature=0.2,
            max_tokens=450,
            request_timeout=15.0,
            timeout=15.0,
            default_headers={
                "HTTP-Referer": "https://wakala.ma",
                "X-Title": "Wakala Platform",
            }
        )
    # Return dummy harmless fallback instead of throwing uncaught RuntimeError
    return ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        model="openai/gpt-oss-120b",
        api_key="disabled",
    )

EMOJI_PATTERN = re.compile(
    r'[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2B50\u2B55\u2934\u2935\u25AA\u25AB\u25FE\u25FD\u25FB\u25FC\u25B6\u25C0\u3030\u303D\u3297\u3299\uFE0F]'
)

def remove_emojis(text: str) -> str:
    if not text:
        return ""
    cleaned = EMOJI_PATTERN.sub('', text)
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    return cleaned

def scrub_thinking(text: str) -> str:
    if not text:
        return ""
    if "<think>" in text:
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        if "<think>" in text:
            text = text.split("<think>")[0]

    thinking_markers = [
        "Here's a thinking process:",
        "Here is a thinking process:",
        "Thinking Process:",
        "Thinking process:",
        "Thought process:",
        "Thought:",
        "Reasoning Process:"
    ]
    for marker in thinking_markers:
        if marker in text:
            after = text.split(marker, 1)[1]
            parts = re.split(r'\n\n(?=[A-Z\*\#\-\u0600-\u06FF])', after)
            real_parts = []
            for p in parts:
                p_str = p.strip()
                if not p_str:
                    continue
                if re.match(r'^\d+\.\s*(?:\*\*)?(?:Analyze|Determine|Formulate|Identify|Review|Understand|Draft|Recall|Check|Acknowledge)', p_str, re.I):
                    continue
                real_parts.append(p_str)
            text = '\n\n'.join(real_parts)

    return text.strip()

DARIJA_LATIN_KEYWORDS = {
    'salam', 'slm', 'labas', 'kidayr', 'ki', 'dayr', 'kidayra', 'chno', 'chnou',
    'ashno', 'ashnou', 'achno', 'achnou', 'ach', 'ash', 'chmen', 'ashmen', 'achmen',
    'fin', 'fayn', 'kifach', 'kifash', 'kifech', 'chhal', 'ch7al', 'bchhal', 'bshhal',
    'wach', 'wesh', '3lach', '3lash', 'imta', 'chkoun', 'chkon', 'homa', 'houma',
    'hiya', 'howa', 'ana', 'nta', 'nti', 'ntoma', 'hna', 'dyal', 'dial', 'dyali',
    'dyalha', 'dyalo', 'dyalhom', 'fih', 'fiha', 'fihom', 'lifih', 'lifiha', 'lifihom',
    'fhad', 'hada', 'hadi', 'hadou', 'daba', 'db', 'ghadi', 'm3a', '3la', 'tomobil',
    'tomobila', 'tomobilat', 'tomobilate', 'tonobil', 'tonobila', 'tonobilat',
    'tonobilate', 'sayara', 'sayarat', 'n9iya', 'nqi', 'rkhis', 'rkhisa', 'jdida',
    'jdid', 'mazot', 'lisans', 'mzyan', 'mzyana', 'khayb', 'khayba', 'sah', 's7i7',
    'machakil', 'mashakil', 'lmachakil', 'moshkil', 'moshkila', '3oyob', 'katkonsomi',
    'katkhser', 'bghit', 'baghi', 'bghina', 'kanqleb', 'kan9leb', 'kanchof', '3tini',
    'gol', 'lia', 'goul', 'khassni', 'khesni', '3ndkom', '3andkom', 'kayn', 'kayna',
    'kaynin', 'makaynch', '3afak', 'afak', 'mlyon', 'melyon', 'flous', 'chokran'
}

DARIJA_ARABIC_KEYWORDS = [
    'واش', 'بغيت', 'بْغيت', 'كاين', 'كاينة', 'كاينين', 'ديال', 'ديالي', 'ديالها', 'ديالهم',
    'طوموبيل', 'طوموبيلا', 'طوموبيلات', 'شحال', 'بشحال', 'مزيان', 'مزيانة',
    'لاباس', 'كي داير', 'خويا', 'أشمن', 'فين', 'بلاصة', 'فلوس', 'سنتيم',
    'ديك', 'هاد', 'هادو', 'عفاك', 'زوينة', 'زوين', 'شنو', 'فاليز', 'فاليزات'
]

FRENCH_KEYWORDS = {
    'bonjour', 'salut', 'coucou', 'bonsoir', 'cherche', 'recherche', 'trouver', 'voiture',
    'voitures', 'vehicule', 'vehicules', 'auto', 'moteur', 'conseillez', 'conseil', 'conseils',
    'prix', 'budget', 'fiable', 'fiabilite', 'probleme', 'problemes', 'panne', 'pannes',
    'achat', 'acheter', 'vendre', 'automatique', 'manuelle', 'essence', 'diesel', 'hybride',
    'electrique', 'consommation', 'entretien', 'vidange', 'merci', 'svp', 'quels', 'quel',
    'quelle', 'quelles', 'pourquoi', 'comment', 'combien', 'est', 'sont', 'dans', 'avec',
    'pour', 'sur', 'une', 'des', 'les', 'pas', 'plus', 'tres', 'neuf', 'maroc', 'avis',
    'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'mon', 'ma', 'mes', 'votre', 'vos'
}

ENGLISH_KEYWORDS = {
    'the', 'what', 'which', 'where', 'when', 'who', 'why', 'how', 'can', 'could', 'should',
    'would', 'vehicle', 'automotive', 'engine', 'transmission', 'gearbox', 'fuel', 'petrol',
    'gasoline', 'electric', 'hybrid', 'battery', 'price', 'cost', 'buy', 'used', 'new', 'mileage',
    'reliable', 'reliability', 'problem', 'problems', 'issue', 'issues', 'maintenance',
    'oil', 'change', 'service', 'brake', 'brakes', 'customs', 'duty', 'import', 'tax',
    'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'thank you', 'thanks',
    'looking for', 'want to buy', 'i want', 'i need', 'please', 'budget'
}

SPANISH_KEYWORDS = {
    'coche', 'coches', 'auto', 'automóvil', 'vehículo', 'motor', 'gasolina', 'diésel',
    'híbrido', 'eléctrico', 'precio', 'comprar', 'usado', 'segunda mano', 'nuevo', 'kilometraje',
    'fiabilidad', 'problema', 'problemas', 'mantenimiento', 'aceite', 'aduanas', 'arancel',
    'hola', 'buenos días', 'buenas tardes', 'muchas gracias', 'por favor'
}

GERMAN_KEYWORDS = {
    'der', 'die', 'das', 'und', 'ist', 'sind', 'wie', 'was', 'wo', 'warum', 'wann',
    'ein', 'eine', 'auto', 'autos', 'wagen', 'fahrzeug', 'motor', 'benzin', 'diesel',
    'hybrid', 'elektro', 'batterie', 'preis', 'kaufen', 'gebraucht', 'neu', 'kilometerstand',
    'zuverlässigkeit', 'problem', 'probleme', 'wartung', 'ölwechsel', 'zoll', 'hallo', 'danke'
}

ITALIAN_KEYWORDS = {
    'automobile', 'macchina', 'veicolo', 'motore', 'benzina', 'diesel', 'ibrido', 'elettrico',
    'prezzo', 'comprare', 'usata', 'usato', 'nuovo', 'chilometraggio', 'affidabilità',
    'problema', 'problemi', 'manutenzione', 'olio', 'dogana', 'ciao', 'grazie'
}

PORTUGUESE_KEYWORDS = {
    'carro', 'carros', 'veículo', 'automóvel', 'motor', 'gasolina', 'diesel', 'híbrido',
    'elétrico', 'preço', 'comprar', 'usado', 'novo', 'quilometragem', 'confiabilidade',
    'problema', 'problemas', 'manutenção', 'óleo', 'alfândega', 'olá', 'obrigado'
}

TURKISH_KEYWORDS = {
    'bir', 'bu', 'ne', 'nasıl', 'nerede', 'neden', 'ne zaman', 'araba', 'arabalar',
    'araç', 'otomobil', 'motor', 'benzin', 'dizel', 'hibrit', 'elektrikli', 'fiyat',
    'satın', 'almak', 'ikinci', 'el', 'yeni', 'kilometre', 'güvenilirlik', 'sorun',
    'sorunlar', 'bakım', 'yağ', 'gümrük', 'merhaba', 'teşekkürler'
}

RUSSIAN_KEYWORDS = {
    'как', 'что', 'где', 'почему', 'когда', 'машина', 'машины', 'авто', 'автомобиль',
    'двигатель', 'мотор', 'бензин', 'дизель', 'гибрид', 'электромобиль', 'цена',
    'купить', 'бу', 'новый', 'пробег', 'надежность', 'проблема', 'проблемы',
    'обслуживание', 'масло', 'таможня', 'привет', 'здравствуйте', 'спасибо'
}

def detect_language(text: str, history: Optional[List[Dict[str, str]]] = None, explicit_language: Optional[str] = None) -> str:
    lang_code_map = {
        "en": "english",
        "english": "english",
        "fr": "french",
        "french": "french",
        "ar": "arabic",
        "arabic": "arabic",
        "darija": "darija_ar",
        "darija_ar": "darija_ar",
        "darija_lat": "darija_lat",
        "es": "spanish",
        "de": "german",
        "it": "italian",
        "pt": "portuguese",
        "tr": "turkish",
        "ru": "russian",
        "zh": "chinese",
        "ja": "japanese",
    }
    
    t = text.lower().strip()
    words = set(re.findall(r'\b[a-zA-Z0-9_\-а-яА-ЯёЁüäößçğışñáéíóúàèìòùâêîôûãõ]+\b', t))

    # 1. Priorité absolue à la langue explicite du sélecteur si fournie
    if explicit_language:
        normalized_explicit = lang_code_map.get(explicit_language.lower(), explicit_language.lower())
        if normalized_explicit == "arabic":
            return "arabic"
        if normalized_explicit in ["darija_ar", "darija"]:
            if re.search(r'[\u0600-\u06FF]', text):
                return "darija_ar"
            return "darija_lat"
        if normalized_explicit == "darija_lat":
            return "darija_lat"
        if normalized_explicit == "english":
            if len(words.intersection(FRENCH_KEYWORDS)) >= 3 and not words.intersection(ENGLISH_KEYWORDS):
                return "french"
            return "english"
        if normalized_explicit == "french":
            if len(words.intersection(ENGLISH_KEYWORDS)) >= 3 and not words.intersection(FRENCH_KEYWORDS):
                return "english"
            return "french"
        if normalized_explicit in LANGUAGE_NAMES:
            return normalized_explicit

    # 2. Détection automatique par script et lexique
    if re.search(r'[\u0600-\u06FF]', text):
        if any(kw in text for kw in DARIJA_ARABIC_KEYWORDS):
            return "darija_ar"
        return "arabic"

    if re.search(r'[a-zA-Z]+[3795]|[3795][a-zA-Z]+', t):
        return "darija_lat"
    
    if words.intersection(DARIJA_LATIN_KEYWORDS):
        return "darija_lat"
    darija_patterns = [
        'salam', 'slm', 'labas', 'bghit', 'kayna', 'chhal', 'chno homa', 'fihom machakil',
        'li fihom', 'chno howa', 'wach kayn', 'ki dayr', 'chhal taman', 'gol lia', 'chnahya', 'chnhya', 'chnou', 'achnahya', 'achnhya', 'achnou', 'm3lomat', 'ma3lomat', 'dyal', 'dial'
    ]
    if any(p in t for p in darija_patterns):
        return "darija_lat"

    if history and (len(words) <= 2 or t in {"diesel", "essence", "oui", "non", "ok", "d'accord"} or re.match(r'^\d+[\s\w]*$', t)):
        for prev in reversed(history):
            if prev.get("role") == "user":
                prev_text = prev.get("content", "")
                prev_lang = detect_language(prev_text, history=None)
                if prev_lang != "french":
                    return prev_lang

    if re.search(r'\b(hello|hi|hey|i want|i need|looking for|what is|which car)\b', t) or len(words.intersection(ENGLISH_KEYWORDS)) >= 2:
        return "english"

    if words.intersection(FRENCH_KEYWORDS) or any(t.startswith(kw) for kw in ['bonjour', 'salut', 'coucou', 'bonsoir', 'je cherche', 'quels sont', 'quel est', 'combien', 'comment', 'pourquoi', 'est-ce']):
        return "french"

    if re.search(r'[\u0400-\u04FF]', text) or words.intersection(RUSSIAN_KEYWORDS):
        return "russian"

    if re.search(r'[\u4e00-\u9fff]', text):
        return "chinese"

    if re.search(r'[\u3040-\u30ff]', text):
        return "japanese"

    if len(words.intersection(SPANISH_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['hola', 'buenos días', 'buenas tardes', 'qué ', 'cómo ', 'cuánto ']):
        return "spanish"

    if len(words.intersection(GERMAN_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['hallo', 'guten tag', 'guten morgen', 'wie ', 'was ']):
        return "german"

    if len(words.intersection(ITALIAN_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['ciao', 'buongiorno', 'buonasera', 'come ', 'cosa ']):
        return "italian"

    if len(words.intersection(PORTUGUESE_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['olá', 'ola', 'bom dia', 'boa tarde', 'como ']):
        return "portuguese"

    if len(words.intersection(TURKISH_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['merhaba', 'selam', 'nasılsınız']):
        return "turkish"

    if history:
        for prev in reversed(history):
            if prev.get("role") == "user":
                prev_text = prev.get("content", "")
                prev_lang = detect_language(prev_text, history=None)
                if prev_lang != "french":
                    return prev_lang

    return "french"

LANGUAGE_NAMES = {
    "darija_lat": "Moroccan Darija (written in Latin script)",
    "darija_ar": "Moroccan Darija (in Arabic script)",
    "arabic": "Modern Standard Arabic (العربية الفصحى)",
    "english": "English",
    "french": "Français",
    "spanish": "Español",
    "german": "Deutsch",
    "italian": "Italiano",
    "portuguese": "Português",
    "turkish": "Türkçe",
    "russian": "Русский",
    "chinese": "Mandarin Chinese (中文)",
    "japanese": "Japanese (日本語)"
}

KNOWN_BRANDS_MODELS = [
    'dacia', 'renault', 'peugeot', 'hyundai', 'volkswagen', 'vw', 'fiat', 'citroen', 'citroën',
    'ford', 'kia', 'toyota', 'audi', 'bmw', 'mercedes', 'mercedes-benz', 'jeep', 'nissan',
    'skoda', 'seat', 'opel', 'honda', 'volvo', 'land rover', 'range rover', 'alfa romeo',
    'porsche', 'suzuki', 'byd', 'mg', 'chery', 'geely', 'changan', 'dongfeng', 'haval',
    'jac', 'mazda', 'mitsubishi', 'mini', 'lexus', 'jaguar', 'maserati', 'cupra', 'ds',
    'omoda', 'jaecoo', 'baic', 'seres', 'dfsk', 'tesla',
    'sandero', 'logan', 'duster', 'jogger', 'spring', 'bigster',
    'clio', 'megane', 'mégane', 'captur', 'kadjar', 'arkana', 'austral', 'scenic', 'twingo',
    '208', '308', '2008', '3008', '5008', 'rifter', 'partner',
    'golf', 'polo', 'tiguan', 't-roc', 'touareg', 'passat', 'caddy', 'taigo', 'arteon',
    'i10', 'i20', 'i30', 'tucson', 'santa fe', 'creta', 'kona', 'elantra', 'accent',
    'picanto', 'rio', 'sportage', 'sorento', 'seltos', 'ceed', 'cerato',
    'yaris', 'corolla', 'rav4', 'c-hr', 'prado', 'land cruiser', 'hilux', 'auris',
    'a1', 'a3', 'a4', 'a5', 'a6', 'q2', 'q3', 'q5', 'q7', 'q8',
    'serie 1', 'serie 2', 'serie 3', 'serie 4', 'serie 5', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6',
    'classe a', 'classe c', 'classe e', 'gla', 'glb', 'glc', 'gle',
    'c3', 'c4', 'c5', 'berlingo', 'c-elysee',
    'fiesta', 'focus', 'kuga', 'puma', 'ranger',
    '500', 'panda', 'tipo', 'punto',
    'ibiza', 'leon', 'arona', 'ateca', 'tarraco',
    'corsa', 'astra', 'mokka', 'grandland', 'crossland',
    'qashqai', 'juke', 'micra', 'x-trail',
    'octavia', 'fabia', 'kodiaq', 'karoq', 'kamiq', 'scala',
    'swift', 'jimny', 'vitara',
    'civic', 'cr-v', 'hr-v'
]

def is_specific_search_request(message: str, max_price: Optional[int], history: List[Dict[str, str]] = None) -> bool:
    msg = message.lower().strip()
    all_user_text = msg
    if history:
        all_user_text = " ".join(m.get("content", "").lower() for m in history if m.get("role") == "user") + " " + msg
    
    # 1. Direct Search with Specific Brand or Model
    has_brand_model = any(b in all_user_text for b in KNOWN_BRANDS_MODELS)
    
    # 2. Key Criteria Extraction across Multi-Turn Conversation
    has_budget = bool(
        max_price is not None
        or re.search(r'\b\d+\s*(?:k|000|mad|dh|dirham|درهم|mlyon|melyon|million|مليون|الف|ألف)\b', all_user_text)
    )
    
    fuel_keywords = [
        'diesel', 'essence', 'hybride', 'hybrid', 'electrique', 'électrique', 'petrol', 'gasoline',
        'مازوط', 'مازوت', 'بنزين', 'هجين', 'ايبريد', 'إيبريد', 'كهربائي', 'كهربائية', 'تريسينتي', 'mazot', 'lisans', 'ليصانص', 'بترول'
    ]
    has_fuel = any(k in all_user_text for k in fuel_keywords)
    
    trans_keywords = [
        'automatique', 'automatic', 'manuelle', 'manual', 'bva', 'bvm',
        'أوتوماتيك', 'اوتوماتيك', 'يدوي', 'مانييل', 'بواط'
    ]
    has_transmission = any(k in all_user_text for k in trans_keywords)
    
    body_keywords = [
        'suv', 'crossover', 'citadine', 'berline', 'sedan', 'hatchback', 'break', 'compacte', '7 places', 'familiale',
        'coupe', 'coupé', 'monospace', 'pick-up', 'pickup',
        'سيتادين', 'سيدان', 'دفع رباعي', 'صغيرة', 'طوموبيل صغيرة', 'مونوسباس', 'كوبيه', 'كوبي', 'بيك اب', 'بيك أب'
    ]
    has_body = any(k in all_user_text for k in body_keywords)
    
    explicit_rec_triggers = [
        'montre-moi', 'recommande', 'propose', 'quelles voitures', 'voici mes critères', 'show me', 'what cars', 'recommend',
        'وريني', 'اقترح', 'شنو كترشح', 'أعطني الترشيحات', 'ما هي السيارات'
    ]
    has_explicit_rec = any(trig in msg for trig in explicit_rec_triggers)

    # Condition A: Specific model searched with any qualifier or budget
    if has_brand_model and (has_budget or has_fuel or has_transmission or has_body or has_explicit_rec):
        return True
        
    # Condition B: Full Consultative Discovery Cycle completed (Budget + Body + Fuel/Transmission)
    if has_budget and has_body and (has_fuel or has_transmission):
        return True

    # Condition C: User explicitly demands final recommendations after providing at least budget or body style
    if has_explicit_rec and (has_budget or has_body or has_fuel):
        return True

    # Condition D: User is answering narrowing question or following up on previous recommendations
    if history:
        for m in history:
            if m.get("role") == "assistant" and ("CAR_RECOMMENDATION" in m.get("content", "") or "sélection" in m.get("content", "").lower() or "recommand" in m.get("content", "").lower()):
                return True
        
    return False

def build_system_prompt(detected_lang: str, context: str, is_car_search: bool = False) -> str:
    target_lang_name = LANGUAGE_NAMES.get(detected_lang, "the exact same language as the user's query")
    
    rec_rule_darija_lat = """4. CATALOGUE VEHICLES & RECOMMANDATION FINALE (2 TAL 3 D LES TOMOBILAT):
- Mnin t-recommender des voitures mn l-CONTEXT, khtar 2 wla 3 d les modeles mnasbin w dir l-bloc JSON pour chaque voiture:
```json
{
  "type": "CAR_RECOMMENDATION",
  "id": "ID",
  "brand": "BRAND",
  "model": "MODEL",
  "year": 2022,
  "price": 140000
}
```
- HBES L-AS2ILA : Mnin t-3tih had 2 wla 3 d les voitures, 3teberhom natija niha2iya (final result) w matb9ach tsewel as2ila d la qualification. Gol lih ychouf les details, y-reserver essai wla y-twasel m3a l-vendeur.
- ILA BGHITI T-HESSER F TOMOBILA WEHDA : Ila banti lik bli b9at ghir nuqta wehda (bhal boite auto/manuelle wla coffre) bach t-khtar tomobila wehda par excellence binathum, teqder tsewel STRICTEMENT soual wahed idafi. Mn be3d mat-hdedha, 3tih l-khtiyar l-nihai w matzid ta soual.""" if is_car_search else "4. CONSULTATIVE DISCOVERY: When the user is exploring buying a car without enough details, do NOT output fake JSON blocks or recommend random cars. First inspect the structured profile and its covered/missing dimensions. Select the single missing dimension by how much they distinguish the remaining vehicles, never by a fixed question order. Ask exactly one concise question per message and never repeat a covered dimension."

    rec_rule_darija_ar = """4. عند التوصية بسيارات من السياق أرفق كود JSON الخاص بكل سيارة (ترشيح 2 إلى 3 سيارات كنتيجة نهائية):
```json
{
  "type": "CAR_RECOMMENDATION",
  "id": "ID",
  "brand": "BRAND",
  "model": "MODEL",
  "year": 2022,
  "price": 140000
}
```
- التوقف عن طرح الأسئلة: عند تقديم هذه السيارات (2 إلى 3)، اعتبرها النتيجة النهائية وتوقف عن طرح أسئلة استكشافية أو أسئلة تأهيل. اختم بدعوة العميل للاطلاع على تفاصيل السيارة، أو حجز موعد لتجربة القيادة، أو التواصل مع البائع.
- حصر الاختيار في سيارة واحدة: إذا رأيت أن هناك معياراً فاصلاً ومحدداً (مثل علبة السرعات أوتوماتيك/يدوي أو سعة الصندوق) يمكن أن يحسم الاختيار نحو سيارة واحدة مثالية بين هذه الخيارات، يمكنك طرح سؤال إضافي واحد فقط لحسم الاختيار، وبعدها تقدم السيارة الفائزة وتتوقف نهائياً عن طرح الأسئلة.""" if is_car_search else "4. الاستشارة والاكتشاف قبل التوصية: لا تصدر كتل JSON أو ترشيحات عشوائية. حلل ملف الاحتياجات والأبعاد المغطاة والناقصة، ثم اختر بُعداً واحداً ناقصاً حسب قدرتهما على التمييز بين السيارات المتبقية، وليس حسب ترتيب ثابت. اطرح سؤالاً واحداً فقط ولا تكرر بُعداً تمت الإجابة عنه."

    rec_rule_ar = """4. عند التوصية بسيارات من السياق أرفق كود JSON الخاص بها (ترشيح 2 إلى 3 سيارات كنتيجة نهائية):
```json
{
  "type": "CAR_RECOMMENDATION",
  "id": "ID",
  "brand": "BRAND",
  "model": "MODEL",
  "year": 2022,
  "price": 140000
}
```
- التوقف عن طرح الأسئلة: بمجرد ترشيح هذه السيارات (2 إلى 3)، اعتبرها النتيجة النهائية ولا تطرح مزيداً من أسئلة الاستكشاف والتأهيل. اختم بدعوة العميل لمعاينة تفاصيل السيارة، أو حجز موعد تجربة القيادة، أو التواصل مع البائع.
- تضييق الاختيار إلى سيارة واحدة: إذا وجدت فارقاً جوهرياً وحاسماً يمكن من خلاله تضييق الاختيار إلى سيارة واحدة نهائية مثالية، يجوز لك طرح سؤال حاسم واحد إضافي فقط لتحديد السيارة الأنسب، وبعد ذلك تعرض النتيجة النهائية دون طرح أي أسئلة أخرى.""" if is_car_search else "4. الاستشارة والتشخيص قبل التوصية: لا تدرج كتل JSON أو اقتراحات عشوائية. حلل الحالة المنظمة، اختر بُعداً أو بُعدين ناقصين الأكثر تمييزاً للسيارات المتبقية، ثم صغ سؤالاً واحداً فقط. لا تكرر بُعداً تمت الإجابة عنه ولا تتبع ترتيباً ثابتاً."

    rec_rule_fr = """4. VÉHICULES DU CATALOGUE & SÉLECTION FINALE (2 À 3 VOITURES) :
- Lorsque tu recommandes des véhicules spécifiques à partir du CONTEXTE, sélectionne les 2 ou 3 véhicules les plus adaptés et insère pour chacun le bloc JSON standard :
```json
{
  "type": "CAR_RECOMMENDATION",
  "id": "VEHICLE_ID",
  "brand": "BRAND",
  "model": "MODEL",
  "year": 2022,
  "price": 140000
}
```
- ARRÊT DES QUESTIONS : Dès que tu présentes ces 2 ou 3 véhicules, considère-les comme ta SÉLECTION FINALE / RÉSULTAT FINAL et arrête de poser des questions de découverte ou de qualification. Invite le client à consulter la fiche détaillée, planifier un essai ou contacter le vendeur.
- EXCEPTION UNIQUE (AFFINAGE À 1 VOITURE) : Si et seulement si tu constates qu'un critère discriminant précis (ex: boîte automatique vs manuelle, volume de coffre en valises, ou budget vs consommation) permet d'isoler UNE SEULE voiture finale idéale parmi ces 2 ou 3 options, tu peux poser STRICTEMENT UNE question supplémentaire décisive pour départager. Une fois cette précision apportée, présente le résultat final et n'ajoute plus aucune question.""" if is_car_search else "4. CONSULTATION ET QUALIFICATION DU PROJET : Lorsqu'un utilisateur souhaite acheter un véhicule sans avoir précisé ses critères complets, N'ÉMETS AUCUN bloc JSON et ne suggère aucun véhicule au hasard. Analyse le profil structuré, sélectionne une seule dimension manquante selon leur pouvoir discriminant dans le stock restant, puis formule exactement une question. Ne répète jamais une dimension déjà couverte et ne suis pas un ordre chronologique fixe."

    rec_rule_en = """4. CATALOGUE VEHICLES & FINAL SELECTION (2 TO 3 CARS):
- When recommending specific vehicles from the CONTEXT, select the 2 or 3 best matching cars and insert the standard JSON block for each:
```json
{
  "type": "CAR_RECOMMENDATION",
  "id": "VEHICLE_ID",
  "brand": "BRAND",
  "model": "MODEL",
  "year": 2022,
  "price": 140000
}
```
- STOP ASKING QUESTIONS: Once you recommend these 2 or 3 cars, consider them as the FINAL RESULT and STOP asking qualification or discovery questions. Conclude by inviting the user to view vehicle details, schedule a test drive, or contact the seller.
- NARROWING DOWN TO 1 CAR (SINGLE QUESTION): IF and only if you see that a specific decisive differentiator (e.g. automatic vs manual transmission, trunk suitcase space, or running cost) can narrow the selection down to ONE single best car, you may ask EXACTLY ONE additional targeted question to decide. Once that preference is clarified, present the final car and stop asking questions.""" if is_car_search else "4. CONSULTATIVE DIAGNOSIS: When a user inquires about buying or finding a car without specific parameters, do NOT output any JSON blocks or random vehicle picks. Inspect the structured profile and its covered/missing dimensions, select one missing dimension by discriminating power in the remaining pool, then ask exactly one concise question. Never repeat a covered dimension and never follow a fixed turn-by-turn order."

    loop_rule_darija_lat = "5. NTIJA NIHA2IYA W HBES L-AS2ILA : Had 2 wla 3 d les tomobilat li 3titih homa l-khtiyar l-nihai. Matb9ach tsewel as2ila khrin d l-qualification. Ila ban lik bli teqder t-hesser f tomobila wehda ghir b soual wahed mouhim, sewel STRICTEMENT soual wahed bach tkhtar tomobila l-ideal. Sinon, matzid ta soual w gol lih ychouf les details wla y-reserver essai." if is_car_search else "5. DISCOVERY LOOP (Analyse → Sélection → Formulation) : Pose STRICTEMENT UNE question ciblée à partir des dimensions manquantes du profil. Ne répète jamais une dimension couverte et ne suis pas un ordre fixe. N'écris JAMAIS de questionnaire."

    loop_rule_darija_ar = "5. النتيجة النهائية والتوقف عن الأسئلة: السيارات (2 إلى 3) المرشحة تمثل النتيجة النهائية للاختيار. توقف تماماً عن طرح أسئلة التأهيل أو الاستكشاف. إذا رأيت إمكانية لحصر الاختيار في سيارة واحدة مثالية عبر معيار حاسم، اطرح سؤالاً إضافياً واحداً فقط، وإلا فلا تطرح أي سؤال وادعُ العميل لمعاينة السيارة أو تجربة القيادة." if is_car_search else "5. حلقة الاكتشاف: حلل الأبعاد المغطاة والناقصة، اختر بُعداً واحداً فقط الأكثر تمييزاً، ثم اطرح سؤالاً واحداً فقط. لا تكرر بُعداً تمت الإجابة عنه ولا تستخدم ترتيباً ثابتاً."

    loop_rule_ar = "5. النتيجة النهائية والتوقف عن الأسئلة: تشكل السيارات الـ 2 إلى 3 المرشحة النتيجة النهائية لعملية الاختيار. توقف عن طرح أسئلة التأهيل والاستكشاف العامة. يجوز لك فقط طرح سؤال حاسم واحد إضافي إذا كان كفيلاً بتضييق الاختيار إلى سيارة واحدة نهائية مثالية، وإلا فاكتفِ بالنتيجة دون طرح أسئلة وادعُ العميل لمعاينة التفاصيل أو حجز موعد للتجربة." if is_car_search else "5. حلقة التشخيص: حلل الأبعاد المغطاة والناقصة، اختر بُعداً واحداً فقط الأكثر تمييزاً، ثم اطرح سؤالاً واحداً فقط. لا تكرر بُعداً تمت الإجابة عنه ولا تستخدم ترتيباً ثابتاً."

    loop_rule_fr = "6. RÉSULTAT FINAL & FIN DES QUESTIONS : Les 2 ou 3 véhicules présentés constituent ta sélection finale. Arrête de poser des questions de découverte ou de qualification. Si et seulement si tu identifies un critère discriminant majeur permettant d'isoler LA seule voiture idéale parmi les 2-3, tu peux poser STRICTEMENT UNE question supplémentaire de départage. Sinon, ne pose aucune question et invite le client à consulter les détails ou planifier un essai." if is_car_search else "6. BOUCLE DE DÉCOUVERTE : Analyse les dimensions couvertes et manquantes, sélectionne une seule dimension selon leur pouvoir discriminant dans le stock restant, puis formule exactement une question. Ne répète aucune dimension couverte et ne suis pas un ordre fixe. Ne présente JAMAIS de questionnaire multiple."

    loop_rule_en = "6. FINAL RESULT & STOP ASKING QUESTIONS: The 2 to 3 recommended vehicles constitute your final result. Stop asking discovery or qualification questions. If and only if you identify a decisive factor that can narrow down from these 2-3 cars to ONE single winning car, you may ask EXACTLY ONE additional targeted question to make that final cut. Otherwise, ask no further questions and invite the user to view details or book a test drive." if is_car_search else "6. DISCOVERY LOOP: Analyze covered and missing dimensions, select one missing dimension by its discriminating power in the remaining pool, and formulate exactly one concise question. Never repeat a covered dimension and never follow a fixed order. Never present a multi-question questionnaire."

    if detected_lang == "darija_lat":
        return f"""You are the expert automotive consultant for the Wakala platform in Morocco.

CRITICAL RULES:
1. LANGUAGE RULE: You MUST answer 100% in natural Moroccan Darija written in Latin script (e.g. 'Kaynin ba3d les modeles w les moteurs li ma3roufin b machakil f l-mghrib...').
   - Speak clearly and naturally like a knowledgeable Moroccan car expert.
   - DO NOT speak French.
   - DO NOT invent bizarre words, repeated tokens, or random numbers.
   - NEVER repeat words or phrases in a loop. Keep sentences crisp and meaningful.
2. ZERO EMOJIS: Never use any emojis or icons.
3. COFFRE ET VALISES : Pour qualifier le besoin du client, demande toujours la capacité en nombre de valises, jamais en litres. Pour une fiche technique, tu peux mentionner les litres uniquement avec leur équivalence en valises (ex: 'Coffre fih 440 L, yhez lik 3 tal 4 d les valises').
4. DOMAIN EXPERTISE: Answer the user's specific automotive question directly with full technical clarity based on the CONTEXT.
{rec_rule_darija_lat}
{loop_rule_darija_lat}
6. CRITICAL OUTPUT CONSTRAINT:
   - Output ONLY the direct final response to the user in Moroccan Darija.
   - NEVER output internal reasoning, thinking tags (<think>...</think>), or chain-of-thought steps.

--- CONTEXT ---
{context}
---------------
"""

    if detected_lang == "darija_ar":
        return f"""أنت الخبير والمستشار الآلي لمنصة وكالة (Wakala) المتخصصة في سوق وصناعة السيارات بالمغرب.

قواعد صارمة:
1. قاعدة اللغة: أجب بنسبة 100% بالدارجة المغربية المكتوبة بالحرف العربي بشكل واضح واحترافي ودقيق.
2. بدون إيموجي: ممنوع استخدام أي رمز تعبيري (Emoji) نهائياً.
3. سعة الصندوق وحقائب السفر: عند تأهيل العميل، اسأل عن مساحة الأمتعة بعدد حقائب السفر وليس باللتر. وفي المواصفات التقنية، لا تذكر اللترات إلا مع المعادل العملي بعدد الحقائب (مثال: 'صندوق بسعة 440 لتر، يهز ليك من 3 حتى 4 ديال الفاليزات').
4. خبرة شاملة: أجب بدقة وعمق عن أي سؤال يخص قطاع السيارات اعتماداً على المعلومات في السياق.
{rec_rule_darija_ar}
{loop_rule_darija_ar}
6. الالتزام بالمخرجات المباشرة:
   - أخرج فقط النص النهائي الموجه للعميل دون أي مسودة تفكير أو وسوم <think>.

--- سياق المعلومات ---
{context}
----------------------
"""

    if detected_lang == "arabic":
        return f"""أنت الخبير والمستشار الهندسي والتقني المعتمد لمنصة وكالة (Wakala) لقطاع وسوق السيارات.

قواعد صارمة:
1. قاعدة اللغة: يجب أن تجيب بنسبة 100% باللغة العربية الفصحى السليمة والواضحة والمهنية.
2. بدون إيموجي: لا تستخدم أي رموز تعبيرية (Emojis) إطلاقاً.
3. سعة الصندوق وحقائب السفر: عند تأهيل العميل، اسأل عن مساحة الأمتعة بعدد حقائب السفر وليس باللتر. وعند الحديث عن المواصفات التقنية، اذكر اللترات فقط مع المعادل العملي بعدد الحقائب (مثال: 'صندوق بسعة 450 لتر، يتسع لحوالي 3 إلى 4 حقائب سفر').
4. موسوعية قطاع السيارات: أجب بمعلومات تقنية واقتصادية دقيقة ومفصلة حول أي موضوع في عالم السيارات بناءً على السياق.
{rec_rule_ar}
{loop_rule_ar}
6. الالتزام بالمخرجات النهائية المباشرة:
   - أخرج فقط النص النهائي الموجه للعميل دون أي مسودة تفكير أو وسوم تفكير.

--- سياق المعلومات ---
{context}
----------------------
"""

    if detected_lang == "french":
        return f"""Tu es l'expert consultant automobile et ingénieur de référence pour la plateforme d'intelligence automobile Wakala au Maroc.

RÈGLES STRICTES ET OBLIGATOIRES :
1. RÈGLE DE LANGUE : Tu DOIS répondre à 100% en français fluide, naturel, technique et professionnel.
   - Ne mélange JAMAIS d'autres langues.
2. ZÉRO ÉMOJI : N'utilise STRICTEMENT AUCUN émoji ni symbole graphique dans tes réponses.
3. COFFRE ET VALISES : Pour qualifier le besoin du client, demande la capacité en nombre de valises, jamais en litres. Dans une fiche technique, indique les litres uniquement avec leur équivalence concrète en valises (ex: 'Coffre de 440 L, soit environ 3 à 4 valises').
4. EXPERTISE AUTOMOBILE DE HAUT NIVEAU :
   - Fournis des réponses techniques, fiables, précises et autoritaires sur l'ensemble du secteur automobile et du marché marocain basées sur le CONTEXTE ci-dessous.
5. STRUCTURE : Rédige des réponses claires, structurées et aérées avec titres en gras et puces si nécessaire.
{rec_rule_fr}
{loop_rule_fr}
7. CONTRAINTE DE SORTIE :
   - Rédige UNIQUEMENT ta réponse finale directement adressée à l'utilisateur.
   - Ne divulgue JAMAIS tes réflexions internes, listes d'analyse ou balises <think>...</think>.
   - Démarre IMMÉDIATEMENT par le texte de réponse.

--- CONTEXTE ---
{context}
----------------
"""

    if detected_lang == "english":
        return f"""You are the world-class automotive consultant and engineering expert for the Wakala automotive intelligence platform.

MANDATORY RULES:
1. LANGUAGE RULE: You MUST respond 100% in English.
   - Maintain total linguistic purity and fluency in English. Do NOT mix other languages.
2. ZERO EMOJIS: Do NOT use any emojis, icons, or graphical symbols under any circumstances.
3. TRUNK CAPACITY & SUITCASES: When qualifying the client's luggage needs, ask for a number of suitcases, never liters. In technical specifications, mention liters only together with the practical suitcase equivalence (e.g. '440 L trunk, fitting approximately 3 to 4 suitcases').
4. AUTOMOTIVE SECTOR AUTHORITY:
   - Provide highly accurate, authoritative, technical, and practical insights on ANY question concerning the automotive sector globally and in Morocco based on the CONTEXT below.
5. STRUCTURE: Use well-formatted bullet points, numbered lists, and bold titles for clarity.
{rec_rule_en}
{loop_rule_en}
7. CRITICAL OUTPUT CONSTRAINT:
   - Output ONLY your direct, final response for the user in English.
   - NEVER output internal thinking, reasoning steps, checklists, chain-of-thought, or <think> tags.
   - Begin your response IMMEDIATELY with the answer text.

--- CONTEXT ---
{context}
---------------
"""

    return f"""You are the world-class automotive consultant and engineering expert for the Wakala automotive intelligence platform.

MANDATORY RULES:
1. LANGUAGE RULE: You MUST respond 100% in {target_lang_name}.
   - Maintain total linguistic purity and fluency in {target_lang_name}. Do NOT mix other languages.
2. ZERO EMOJIS: Do NOT use any emojis, icons, or graphical symbols under any circumstances.
3. COFFRE ET VALISES : Pour qualifier le besoin du client, demande la capacité en nombre de valises, jamais en litres. Dans les spécifications techniques, mentionne les litres uniquement avec leur équivalence concrète en valises.
4. AUTOMOTIVE SECTOR AUTHORITY:
   - Provide highly accurate, authoritative, technical, and practical insights on ANY question concerning the automotive sector globally and in Morocco based on the CONTEXT below.
5. STRUCTURE: Use well-formatted bullet points, numbered lists, and bold titles for clarity.
{rec_rule_en}
{loop_rule_en}
7. CRITICAL OUTPUT CONSTRAINT:
   - Output ONLY your direct, final response for the user in {target_lang_name}.
   - NEVER output internal thinking, reasoning steps, checklists, chain-of-thought, or <think> tags.
   - Begin your response IMMEDIATELY with the answer text.

--- CONTEXT ---
{context}
---------------
"""

def sanitize_input(text: str) -> str:
    text = text[:800]
    return re.sub(r'[\x00-\x1F\x7F]', '', text)

def redact_pii(text: str) -> str:
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_MASKED]', text)
    text = re.sub(r'(?:\+212|0)[ \-]?\d{1}[ \-]?\d{2}[ \-]?\d{2}[ \-]?\d{2}[ \-]?\d{2}', '[PHONE_MASKED]', text)
    return text

def normalize_multilingual_query_terms(query: str) -> str:
    q = query.lower()
    replacements = {
        "tomobilat": "voitures",
        "tomobilate": "voitures",
        "tonobilat": "voitures",
        "tonobilate": "voitures",
        "tomobila": "voiture",
        "tomobil": "voiture",
        "tonobil": "voiture",
        "tonobila": "voiture",
        "mazot": "diesel",
        "mazout": "diesel",
        "lisans": "essence",
        "lissans": "essence",
        "n9iya": "bon état",
        "nqi": "bon état",
        "rkhisa": "pas cher économique",
        "rkhis": "pas cher économique",
        "jdida": "neuve récente",
        "jadida": "neuve récente",
        "chhal taman": "prix",
        "bghit": "cherche",
        "baghi": "cherche",
        "سيارة": "voiture",
        "سيارات": "voiture",
        "طوموبيل": "voiture",
        "طوموبيلا": "voiture",
        "طوموبيلات": "voiture",
        "ديزل": "diesel",
        "مازوط": "diesel",
        "بنزين": "essence",
        "مستعملة": "neuf",
        "مستعمل": "neuf",
        "جديدة": "neuf",
        "جديد": "neuf",
        "رخيصة": "economique",
        "رخيص": "economique",
        "أوتوماتيك": "automatique",
        "اوتوماتيك": "automatique",
        "يدوي": "manuelle",
        "عائلية": "familiale",
        "شراء": "achat",
        "أبحث": "cherche",
        "car": "voiture",
        "cars": "voiture",
        "used car": "neuf",
        "used cars": "neuf",
        "new car": "neuf",
        "new cars": "neuf",
        "cheap": "economique",
        "petrol": "essence",
        "gasoline": "essence",
        "automatic": "automatique",
        "manual": "manuelle",
        "under": "moins de",
        "looking for": "cherche",
        "want to buy": "acheter",
    }
    for term, repl in replacements.items():
        q = re.sub(r'\b' + re.escape(term) + r'\b', repl, q)
    return q

def fast_classify_intent(message: str) -> Optional[Dict[str, Any]]:
    msg = message.lower().strip()
    definition_question_words = [
        'chnahya', 'chnhya', 'chnou hiya', 'chnou howa', 'chnou', 'chniya', 'chnehiya',
        'achnahya', 'achnhya', 'achnou', 'ach hiya', 'ach howa', 'chouhouwa',
        "c'est quoi", "qu'est-ce que", "qu'est ce que", 'what is', "what's",
        'شنو هي', 'شنو هو', 'ما هي', 'ما هو', 'شنو كتعني', 'معنى'
    ]
    if any(q_word in msg for q_word in definition_question_words):
        # Questions asking what a brand, model, or automotive term is (e.g. "chnahya amg", "c'est quoi amg")
        if any(term in msg for term in AUTOMOTIVE_DOMAIN_TERMS) or any(b in msg for b in KNOWN_BRANDS_MODELS) or 'amg' in msg:
            clean_q = normalize_multilingual_query_terms(message)
            return {"intent": "auto_expert", "max_price": None, "search_query": clean_q}


    expert_kw = [
        'problème', 'probleme', 'problèmes', 'problemes', 'panne', 'pannes', 'bruit bizarre',
        'fiabilité', 'fiabilite', 'avis sur', 'défaut', 'defauts', 'casse moteur', 'surconsommation',
        'courroie distribution', 'puretech', 'tce', 'adblue', '1.2 puretech', '1.2 tce', '1.6 thp',
        'rappel constructeur', 'secteur auto', 'industrie automobile', 'marche automobile',
        'machakil', 'mashakil', 'lmachakil', 'moshkil', 'moshkila', 'mouchkil', 'mouchkila',
        'sout ghrib', 'vibration', '3oyob', '3ouyoub', 'katkonsomi zit',
        'katkhser', 'katkhesser', 'doukhan', 'khatar', 'nasiha f moteur',
        'problem', 'problems', 'issue', 'issues', 'defect', 'defects', 'reliability', 'reliable',
        'review of', 'overheating', 'smoke', 'warning light', 'engine failure', 'timing belt issue',
        'automotive industry', 'sector data',
        'warning light', 'check engine', 'dashboard light', 'strange noise', 'weird noise',
        'vibration', 'shaking', 'smoke', 'overheating', 'wont start', "won't start",
        'hard to start', 'brake noise', 'battery dead', 'flat tire', 'leak',
        'problema', 'problemas', 'avería', 'fallo', 'fiabilidad', 'industria automotriz',
        'problem', 'probleme', 'zuverlässigkeit', 'panne',
        'problema', 'problemi', 'guasto', 'affidabilità',
        'مشكل', 'مشاكل', 'مشكلة', 'عيوب', 'عطب', 'اعطال', 'دخان',
        'اعتمادية', 'قطاع السيارات', 'صناعة السيارات'
    ]
    # Technical questions must stay in the automotive expert flow even when
    # they contain a word that is also used during vehicle discovery (for
    # example "automatic" or "diesel").
    automotive_topics = [
        'moteur', 'engine', 'motor', 'turbo', 'hybride', 'hybrid', 'electric motor',
        'batterie', 'battery', 'alternateur', 'starter', 'démarreur', 'demarreur',
        'embrayage', 'clutch', 'boîte de vitesses', 'gearbox', 'transmission',
        'frein', 'brake', 'pneu', 'tire', 'tyre', 'suspension', 'amortisseur',
        'direction', 'airbag', 'abs', 'esp', 'adblue', 'dpf', 'fap', 'egr',
        'injecteur', 'injector', 'courroie', 'timing belt', 'distribution',
        'huile', 'oil', 'refroidissement', 'coolant', 'radiateur', 'overheating',
        'consommation', 'consumption', 'chevaux', 'horsepower', 'torque', 'couple',
        'bva', 'bvm', 'dci', 'tce', 'puretech', 'tsi', 'tdi', 'vin', 'kilométrage',
        'kilometrage', 'mileage', 'carte grise', 'assurance', 'sécurité', 'safety',
        'rappel constructeur', 'recall', 'contrôle technique', 'technical inspection',
        'موتور', 'محرك', 'بطارية', 'فران', 'عجلة', 'زيت', 'كوبلاج', 'بواط', 'أوتوماتيك'
    ]
    question_words = [
        'quoi', 'qu est', "qu'est", 'comment', 'pourquoi', 'signifie', 'définition',
        'what', 'how', 'why', 'meaning', 'explain', 'difference', 'différence',
        'شنو', 'كيفاش', 'علاش', 'معنى'
    ]
    maintenance_tracking_signals = [
        'service book', 'service history', 'track service', 'record service',
        'record my', 'carnet d’entretien', "carnet d'entretien", 'carnet entretien',
        'دفتر الصيانة', 'سجل الصيانة'
    ]
    if any(signal in msg for signal in maintenance_tracking_signals) and (
        any(word in msg for word in question_words) or any(word in msg for word in ['record', 'track', 'log', 'update', 'enregistrer', 'suivre'])
    ):
        return {"intent": "maintenance_check", "max_price": None, "search_query": None}
    if any(topic in msg for topic in automotive_topics) and any(word in msg for word in question_words):
        return {"intent": "auto_expert", "max_price": None, "search_query": None}
    if any(kw in msg for kw in expert_kw):
        return {"intent": "auto_expert", "max_price": None, "search_query": None}

    customs_kw = [
        'douane', 'dédouanement', 'dedouanement', 'diwana', 'dywana',
        'import', 'importation', 'taxe douane', 'frais douane', 'taman diwana',
        'customs', 'customs duty', 'import tax', 'clearance fees',
        'aduanas', 'arancel', 'zoll', 'dogana', 'alfândega', 'gümrük', 'таможня',
        'ديوانة', 'جمارك', 'الجمارك', 'جمرك', 'جمركية', 'الجمركية', 'تعشير', 'التعشير', 'استيراد'
    ]
    if any(kw in msg for kw in customs_kw):
        return {"intent": "customs", "max_price": None, "search_query": None}

    maint_kw = [
        'entretien', 'vidange', 'maintenance', 'révision', 'revision',
        'carnet', 'pneu', 'pneus', 'rappel entretien', 'khassni vidange', 'zite',
        'oil change', 'service book', 'tires', 'inspection', 'car maintenance',
        'mantenimiento', 'cambio de aceite', 'wartung', 'ölwechsel', 'manutenzione',
        'فحص', 'صيانة', 'تغيير الزيت', 'عجلات', 'إطارات'
    ]
    if any(kw in msg for kw in maint_kw):
        return {"intent": "maintenance_check", "max_price": None, "search_query": None}

    # A make/model mentioned in an informational question (for example
    # "what is Dacia?" or "شنو هي داسيا؟") must not be mistaken for a vehicle
    # search merely because the make is present in search_triggers below.
    informative_prefixes = [
        'what is', "what's", 'what does', 'who is', 'tell me about', 'do you know',
        'give me info', 'give me information', 'explain', 'meaning of',
        'how reliable', 'does ', 'compare ', 'difference between', 'why ',
        'how ', 'when ', 'where ', 'how much', "qu'est-ce que", "c'est quoi",
        'qui est', 'parle-moi de', 'parle moi de', 'informations sur', 'infos sur',
        'je veux des informations sur', 'je veux des infos sur',
        'renseigne-moi', 'renseigne moi', 'est-ce que', 'quelle est la différence',
        'pourquoi ', 'comment ', 'quand ', 'où ', 'combien coûte', 'combien coute',
        'ما هي', 'ما هو', 'من هي', 'من هو', 'معلومات عن', 'أخبرني عن', 'هل ',
        'شنو هي', 'شنو هو', 'اش هي', 'اش هو', 'شكون هي', 'شكون هو', 'شنو كتعني',
        'علاش ', 'كيفاش ', 'كيف ', 'الفرق بين', 'قارن ', 'بشحال', 'chno hiya',
        'chno howa', 'gol lia 3la', '3tini ma3lomat', '3tini m3lomat', 'bghit m3lomat', 'bghit ma3lomat', 'chnahya', 'chnhya', 'chnou', 'achnahya', 'achnhya', 'wach ', '3lach ',
        'kifach ', 'chno kay3ni', 'far9 bin', 'qaren '
    ]
    recommendation_markers = [
        'recommend', 'suggest', 'choose', 'find', 'show me',
        'buy', 'best', 'safest', 'help me choose', 'which car', 'recommande',
        'propose', 'choisir', 'cherche', 'acheter', 'meilleur',
        'meilleure', 'aide-moi', 'aide moi', 'quelle voiture',
        'أبحث', 'أفضل', 'أنسب', 'اختيار', 'ساعدني', 'شنو نشري',
        'نشري', 'كنقلب', '3awni'
    ]
    informative_markers = [
        'information about', 'info about', 'info on', 'informations sur',
        'des informations sur', 'help me understand', 'aide-moi à comprendre',
        'price of', 'prix de', ' vs ', ' versus ', ' contre ', 'worth it',
        'available in', 'disponible au', 'reliable', 'fiable', 'معلومات عن',
        'معلومات على', 'معلومة على', 'بغيت معلومات', 'بغيت نعرف', 'ثمن',
        'سعر', 'ma3lomat 3la', 'bghit ma3lomat', 'bghit m3lomat', 'bghit m3lomat 3la', 'm3lomat 3la', 'ma3lomat 3la', 'ma3loumat 3la', 'maloumat 3la', 'bghit n3ref 3la'
    ]
    informative_signal = any(msg.startswith(prefix) for prefix in informative_prefixes) or any(marker in msg for marker in informative_markers)
    if informative_signal and not any(marker in msg for marker in recommendation_markers):
        clean_q = normalize_multilingual_query_terms(message)
        return {"intent": "general_advice", "max_price": None, "search_query": clean_q}

    greetings = [
        'bonjour', 'salut', 'bonsoir', 'hello', 'hi', 'hey', 'good morning', 'good afternoon',
        'salam', 'slm', 'salamo alaykom', 'salamou alaykoum', 'salam alaykom',
        'labas', 'kidayr', 'ki dayr', 'kidayra', 'cv', 'cava', 'ca va', 'ça va',
        'merci', 'thanks', 'thank you', 'shukran', 'chokran', 'barak allaho fik',
        'ok', 'oui', 'non', 'yes', 'no', 'bye', 'goodbye', 'bslama', 'b slama',
        'hola', 'buenos días', 'buenas tardes', 'gracias',
        'hallo', 'guten tag', 'danke',
        'ciao', 'buongiorno', 'grazie',
        'olá', 'ola', 'obrigado',
        'merhaba', 'teşekkürler',
        'здравствуйте', 'привет', 'спасибо',
        'سلام', 'السلام عليكم', 'مرحبا', 'أهلا', 'شكرا', 'صباح الخير', 'مساء الخير'
    ]
    if any(msg == g or msg.startswith(g + ' ') or msg.startswith(g + ',') or msg.startswith(g + '!') or msg.startswith(g + '?') for g in greetings):
        if len(msg) < 35:
            return {"intent": "greeting", "max_price": None, "search_query": None}

    search_triggers = [
        'bghit', 'baghi', 'kanqleb', 'kan9leb', 'kayna chi', 'kayn chi',
        '3ndkom chi', '3andkom', 'cherche', 'recherche', 'trouver',
        'je veux acheter', 'acheter', 'voiture pour', 'budget de', 'mon budget',
        'tomobila', 'sayara', 'neuf', 'dacia', 'renault',
        'peugeot', 'clio', 'golf', 'volkswagen', 'hyundai', 'kia', 'mercedes', 'bmw',
        'looking for', 'search', 'want to buy', 'i want', 'i need', 'find me', 'help me choose',
        'show me', 'cheap car', 'diesel car', 'new car', 'price of', 'my budget',
        'comprar', 'coche', 'auto', 'kaufen', 'comprare',
        'سيارة', 'سيارات', 'شراء', 'أبحث', 'أريد', 'بدي', 'طوموبيل', 'ميزانيتي', 'البودجي',
        # Single-word / preference criteria triggers during discovery
        'diesel', 'essence', 'hybride', 'hybrid', 'electrique', 'petrol', 'gasoline',
        'مازوط', 'بنزين', 'هجين', 'ايبريد', 'كهربائي',
        'automatique', 'automatic', 'manuelle', 'manual', 'أوتوماتيك', 'اوتوماتيك', 'يدوي', 'مانييل',
        'suv', 'crossover', 'citadine', 'berline', 'sedan', 'hatchback', 'سيتادين', 'سيدان',
        'ville', 'city', 'autoroute', 'highway', 'mixte', 'mixed', 'مدينة', 'طريق', 'سفر', 'مخلط'
    ]
    
    max_price = None
    k_match = re.search(r'(?:under|below|moins de|max|budget(?: de)?|أقل من|ميزانية|البودجي)?\s*(\d+[\s,.]?\d*)\s*(?:k|000|mad|dh|dirham|درهم|usd|eur)?', msg)
    if k_match:
        val_str = k_match.group(1).replace(' ', '').replace(',', '').replace('.', '')
        if val_str.isdigit():
            val = int(val_str)
            max_price = val * 1000 if (val < 1000 and 'k' in msg) else val
    
    mlyon_match = re.search(r'(\d+)\s*(?:mlyon|melyon|million|مليون)', msg)
    if mlyon_match:
        val = int(mlyon_match.group(1))
        max_price = val * 10000

    alf_match = re.search(r'(\d+)\s*(?:ألف|الف)', msg)
    if alf_match:
        val = int(alf_match.group(1))
        max_price = val * 1000

    if any(kw in msg for kw in search_triggers) or any(b in msg for b in KNOWN_BRANDS_MODELS):
        clean_search = normalize_multilingual_query_terms(message)
        return {"intent": "car_search", "max_price": max_price, "search_query": clean_search}

    clean_q = normalize_multilingual_query_terms(message)
    return {"intent": "general_advice", "max_price": max_price, "search_query": clean_q}

async def analyze_intent(user_message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    fast_result = fast_classify_intent(user_message)
    if fast_result:
        return fast_result

    clean_q = normalize_multilingual_query_terms(user_message)
    is_car = any(w in user_message.lower() for w in ["voiture", "car", "tomobil", "dacia", "clio", "golf", "prix", "price", "budget", "سيارة"])
    return {
        "intent": "car_search" if is_car else "general_advice",
        "max_price": None,
        "search_query": clean_q
    }


# This guard is deliberately local and cheap. It prevents the chatbot from
# becoming a general-purpose assistant and avoids spending 10–20 seconds on
# an LLM call for a question outside the car domain.
AUTOMOTIVE_DOMAIN_TERMS = (
    'voiture', 'voitures', 'véhicule', 'vehicule', 'auto', 'automobile', 'car', 'cars',
    'vehicle', 'automotive', 'moteur', 'engine', 'motor', 'turbo', 'diesel', 'essence',
    'petrol', 'gasoline', 'hybride', 'hybrid', 'électrique', 'electric', 'batterie',
    'battery', 'huile', 'oil', 'vidange', 'entretien', 'maintenance', 'révision',
    'service', 'frein', 'brake', 'pneu', 'tire', 'tyre', 'embrayage', 'clutch',
    'boîte', 'boite', 'gearbox', 'transmission', 'suspension', 'airbag', 'abs', 'esp',
    'adblue', 'dpf', 'fap', 'egr', 'injecteur', 'injector', 'courroie', 'distribution',
    'consommation', 'consumption', 'kilométrage', 'kilometrage', 'mileage', 'suv',
    'berline', 'citadine', 'break', 'crossover', 'pickup', 'van', '4x4', 'bva', 'bvm',
    'dci', 'tce', 'puretech', 'tsi', 'tdi', 'vin', 'amg', 'mercedes-amg', 'm power', 'audi rs', 'gti', 'dacia', 'panne', 'fiabilité', 'reliability',
    'occasion', 'neuf', 'new car', 'used car', 'achat', 'acheter', 'buy', 'prix', 'price',
    'budget', 'assurance', 'insurance', 'douane', 'dédouanement', 'customs', 'import',
    'sécurité', 'safety', 'carte grise', 'concessionnaire', 'marque', 'modèle',
    'problème', 'probleme', 'problem', 'issue', 'panne', 'warning light', 'check engine',
    'voyant', 'bruit', 'noise', 'vibration', 'fumée', 'smoke', 'surchauffe', 'overheating',
    'ne démarre pas', 'wont start', "won't start", 'fuite', 'leak', 'voyant moteur',
    'طوموبيل', 'سيارة', 'سيارات', 'موتور', 'محرك', 'بطارية', 'زيت', 'فران', 'بواط',
    'عجلة', 'كروسة', 'مازوط', 'بنزين', 'كهربائية', 'صيانة', 'ميكانيك', 'ميكانيكي'
)
AUTOMOTIVE_GREETING_TERMS = (
    'bonjour', 'salut', 'bonsoir', 'hello', 'hi', 'hey', 'salam', 'slm', 'مرحبا', 'سلام',
    'merci', 'thanks', 'thank you', 'شكرا', 'chokran',
    'cava', 'ca va', 'ça va', 'cv', 'labas', 'kidayr', 'ki dayr', 'kidayra'
)


def is_automotive_domain_request(message: str, history: Optional[List[Dict[str, str]]] = None) -> bool:
    """Return True only for car-domain messages or a short conversational turn."""
    normalized = re.sub(r'\s+', ' ', message.lower()).strip()
    if not normalized:
        return True
    if any(term in normalized for term in AUTOMOTIVE_DOMAIN_TERMS):
        return True
    if any(brand_or_model in normalized for brand_or_model in KNOWN_BRANDS_MODELS):
        return True
    if any(normalized == term or normalized.startswith(term + ' ') for term in AUTOMOTIVE_GREETING_TERMS):
        return True
    # Follow-ups such as "and for diesel?" inherit the subject from the chat.
    recent = ' '.join(str(item.get('content', '')).lower() for item in (history or [])[-4:])
    return any(term in recent for term in AUTOMOTIVE_DOMAIN_TERMS)


OUT_OF_DOMAIN_RESPONSES = {
    'french': "Je suis spécialisé uniquement dans l'automobile. Posez-moi une question sur une voiture, un moteur, l'entretien, la sécurité, l'achat ou la comparaison de modèles.",
    'english': "I specialise strictly in cars. Ask me about a vehicle, engine, maintenance, safety, buying, ownership, or comparing car models.",
    'arabic': "أنا متخصص حصراً في السيارات. اطرح سؤالاً عن سيارة أو محرك أو الصيانة أو السلامة أو الشراء أو مقارنة الطرازات.",
    'darija_ar': "أنا متخصص غير فمجال السيارات. سولني على طوموبيل، الموتور، الصيانة، السلامة، الشراء ولا مقارنة الموديلات.",
    'darija_lat': "Ana mkhssas ghir f tomobilat. Sowelni 3la tomobil, moteur, ssiانة, salam, chra wela comparaison dyal les modeles.",
}

async def retrieve_vehicles_from_db(query: str, max_price: Optional[float] = None, top_k: int = 3) -> str:
    """Fallback text search in PostgreSQL when vector search is unavailable."""
    try:
        from app.core.database import async_session_factory
        if not async_session_factory:
            return ""
        from app.models.vehicle import Vehicle
        from sqlalchemy import select, or_

        stop_words = {'les', 'des', 'une', 'qui', 'pour', 'avec', 'dans', 'quel', 'quelle', 'voiture', 'auto', 'cherche', 'veut', 'besoin', 'budget'}
        clean_tokens = [w for w in re.findall(r'\b\w{3,}\b', query.lower()) if w not in stop_words]

        async with async_session_factory() as session:
            stmt = select(Vehicle)
            if max_price is not None:
                stmt = stmt.where(Vehicle.price <= float(max_price))

            if clean_tokens:
                clauses = []
                for token in clean_tokens[:4]:
                    clauses.append(Vehicle.brand.ilike(f"%{token}%"))
                    clauses.append(Vehicle.model.ilike(f"%{token}%"))
                    clauses.append(Vehicle.body_type.ilike(f"%{token}%"))
                stmt = stmt.where(or_(*clauses))

            stmt = stmt.order_by(Vehicle.price.asc()).limit(top_k)
            res = await session.execute(stmt)
            vehicles = res.scalars().all()

            if not vehicles:
                return ""

            context_lines = []
            for v in vehicles:
                specs = [f"Prix: {v.price} MAD", f"Ville: {v.city or 'Maroc'}"]
                if v.fuel_type:
                    specs.append(f"Carburant: {v.fuel_type}")
                if v.transmission:
                    specs.append(f"Boîte: {v.transmission}")
                if v.body_type:
                    specs.append(f"Carrosserie: {v.body_type}")
                specs_str = " | ".join(specs)
                context_lines.append(f"- ID: {v.id} | {v.brand} {v.model} ({v.year}) | {specs_str}")
            return "\n".join(context_lines)
    except Exception as err:
        print(f"[DB Fallback Vehicle Retrieval Warning] {err}")
        return ""


async def retrieve_vehicles(query: str, max_price: Optional[float] = None, top_k: int = 3) -> str:
    qdrant = get_qdrant_client()
    clean_query = normalize_multilingual_query_terms(query)
    search_result = None

    if qdrant:
        try:
            from app.rag.embeddings import embedding_service
            query_vector = embedding_service.embed_text(clean_query)
            filter_conditions = []
            if max_price is not None:
                filter_conditions.append(
                    qmodels.FieldCondition(
                        key="price",
                        range=qmodels.Range(lte=float(max_price))
                    )
                )
            query_filter = qmodels.Filter(must=filter_conditions) if filter_conditions else None
            search_result = await qdrant.search(
                collection_name=settings.QDRANT_COLLECTION,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k * 3
            )
        except Exception as e:
            print(f"[Qdrant Fast Fallback] Vector search unavailable or timed out: {e}")

    context_str = ""
    if search_result:
        seen_signatures = set()
        for hit in search_result:
            payload = hit.payload or {}
            sig = (payload.get('brand'), payload.get('model'), payload.get('year'), payload.get('price'))
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)
            
            brand = payload.get('brand', 'Véhicule')
            model = payload.get('model', '')
            year = payload.get('year', '')
            price = payload.get('price', '')
            city = payload.get('city', 'Maroc')
            fuel = payload.get('fuel_type', '')
            transmission = payload.get('transmission', '')
            body_type = payload.get('body_type', '')
            
            specs = [f"Prix: {price} MAD", f"Ville: {city}"]
            if fuel:
                specs.append(f"Carburant: {fuel}")
            if transmission:
                specs.append(f"Boîte: {transmission}")
            if body_type:
                specs.append(f"Carrosserie: {body_type}")
            
            specs_str = " | ".join(specs)
            context_str += f"- ID: {hit.id} | {brand} {model} ({year}) | {specs_str}\n"
            if len(seen_signatures) >= top_k:
                break

    if not context_str:
        # Fallback to direct PostgreSQL database search
        db_context = await retrieve_vehicles_from_db(clean_query, max_price=max_price, top_k=top_k)
        if db_context:
            return db_context
        return "Catalogue de véhicules neufs disponibles sur la plateforme Wakala."

    return context_str

GREETING_RESPONSES = {
    "darija_lat": "Salam ! Merhba bik f Wakala, l-plateforme l-oula d l-automobile f l-mghrib. Nqder n3awnek tkhtar tomobila jdida li tnasbek, n7esbo rassem diwana, nqarno bin les modeles, wla njawbek 3la ay soual teqni w mécanique. Kifach nqder n3awnek lyoum ?",
    "darija_ar": "السلام عليكم و مرحباً بك في منصة وكالة للسيارات بالمغرب. نقدر نعاونك في اختيار سيارة جديدة مناسبة، حساب مصاريف الديوانة، مقارنة الموديلات، أو الإجابة على أي استفسار تقني أو ميكانيكي. كيفاش نقدر نعاونك اليوم؟",
    "arabic": "أهلاً ومرحباً بك في منصة وكالة الرائدة في استشارات وقطاع السيارات بالمغرب. يمكنني مساعدتك في اختيار السيارة الجديدة الأنسب لك، حساب الرسوم الجمركية، مقارنة المواصفات، أو تقديم استشارات هندسية دقيقة حول المحركات والصيانة. كيف يمكنني مساعدتك اليوم؟",
    "english": "Hello and welcome to Wakala, your intelligent automotive advisory platform in Morocco. I can help you find your ideal new car, calculate customs clearance duties, compare models, or provide expert mechanical advice. How can I best assist you today?",
    "french": "Bonjour et bienvenue sur Wakala ! Je suis votre conseiller automobile intelligent au Maroc. Je peux vous guider dans le choix d'un véhicule neuf, estimer vos droits de douane, comparer des modèles ou vous conseiller sur la fiabilité mécanique. Que recherchez-vous aujourd'hui ?",
    "spanish": "¡Hola y bienvenido a Wakala! Soy tu asesor automotriz inteligente en Marruecos. Puedo ayudarte a elegir un vehículo nuevo, calcular aranceles aduaneros, comparar modelos o asesorarte sobre mecánica. ¿Cómo puedo ayudarte hoy?",
    "german": "Hallo und herzlich willkommen bei Wakala! Ich bin Ihr persönlicher Automobilberater in Marokko. Ich helfe Ihnen bei der Neuwagensuche, Zollkalkulation, Modellvergleichen und technischen Fragen. Wie kann ich Ihnen heute helfen?",
    "italian": "Ciao e benvenuto su Wakala! Sono il tuo consulente automobilistico in Marocco. Posso aiutarti a scegliere un'auto nuova, stimare i dazi doganali, confrontare modelli o darti consigli tecnici. Come posso aiutarti oggi?",
    "portuguese": "Olá e bem-vindo à Wakala! Sou seu consultor automotivo no Marrocos. Posso ajudar você a escolher um carro novo, calcular taxas alfandegárias, comparar modelos ou tirar dúvidas técnicas. Como posso ajudar hoje?",
    "turkish": "Merhaba ve Wakala'ya hoş geldiniz! Fas'taki yapay zeka destekli otomotiv danışmanınızım. Sıfır araç seçimi, gümrük vergisi hesaplama, model karşılaştırması ve teknik danışmanlık konularında yardımcı olabilirim. Bugün size nasıl yardımcı olabilirim?",
    "russian": "Здравствуйте и добро пожаловать в Wakala! Я ваш автомобильный консультант в Марокко. Помогу выбрать новый автомобиль, рассчитать таможенные пошлины, сравнить модели или дать экспертный технический совет. Чем могу помочь вам сегодня?"
}

EXPERT_CONTEXTS = {
    "darija_lat": """Moteurs w machakil mikanikiya ma3roufa f l-mghrib :
1. Moteur 1.2 PureTech (Peugeot, Citroen, Opel, DS) : Mochkil kbir f la courroie de distribution immergee f zit li katfertet w katboucher la crepine d'huile, chi li kaydir casse moteur w surconsommation kbira d zit.
2. Moteur 1.2 TCe (Renault, Dacia, Nissan) : Istihlak kbir bzaf d zit (surconsommation d'huile) w defaut f la segmentation li kaykhlli l-moteur ykhser.
3. Moteur 1.6 THP (Peugeot, Citroen, Mini) : Decalage d la chaine de distribution w perte de puissance.
4. Boites automatiques robotisees : Boite Ford Powershift (double embrayage a sec) w boite DSG 7 DQ200 li fihom machakil d mecatronique.
5. Systeme AdBlue (Diesels recents BlueHDi) : Panne dyal reservoir w pompe AdBlue li katbghi changement complet b taman ghali.""",

    "darija_ar": """أهم مشاكل المحركات والأعطال الشائعة في السوق المغربي:
1. محرك 1.2 PureTech (Peugeot, Citroen, Opel, DS): حزام التوقيت المغمور في الزيت يتفتت ويسد مضخة الزيت، مما يسبب استهلاكاً كبيراً للزيت وتلف المحرك.
2. محرك 1.2 TCe (Renault, Dacia, Nissan): استهلاك مفرط للزيت وعيب في حلقات المكابس (segmentation).
3. محرك 1.6 THP (Peugeot, Citroen, Mini): تمدد سلسلة التوقيت وفقدان العزم.
4. علب السرعة الأوتوماتيكية: Ford Powershift و DSG7 الجافة تعاني من مشاكل في الدبرياج المزدوج والميكاترونيك.
5. نظام AdBlue في محركات الديزل الحديثة: أعطال متكررة في الخزان والمضخة تستدعي الاستبدال بتكلفة باهظة.""",

    "arabic": """أبرز المشاكل الميكانيكية والعيوب المصنعية الشائعة في سوق السيارات:
1. محرك 1.2 PureTech (مجموعة Stellantis): حزام التوقيت المغمور في الزيت (Wet Belt) يتآكل ويسد مصفاة الزيت ومضخة التزييت، مما يؤدي لاستهلاك مفرط للزيت وتلف كامل للمحرك.
2. محرك 1.2 TCe (Renault/Dacia/Nissan): استهلاك غير طبيعي لزيت المحرك وعيوب في شنابر المكابس (Piston rings).
3. محرك 1.6 THP (BMW/PSA): ارتخاء سلسلة التوقيت وتراكم الكربون على صمامات السحب.
4. علب السرعات الأوتوماتيكية: علبة Powershift (Ford) و DSG 7 الجافة (DQ200) بمشاكل القابض المزدوج ووحدة الميكاترونيكس.
5. منظومة AdBlue في محركات الديزل الحديثة: تبلور السائل وتلف مضخة وخزان AdBlue.""",

    "english": """Notable automotive mechanical issues and engine reliability data:
1. 1.2 PureTech engine (Stellantis: Peugeot, Citroen, DS, Opel): Wet timing belt runs in oil, sheds rubber particles, clogs the oil strainer/pickup, leading to oil starvation, heavy oil consumption, and engine failure.
2. 1.2 TCe engine (Renault, Dacia, Nissan): High oil consumption caused by defective piston rings and cylinder wear.
3. 1.6 THP engine (PSA / BMW / Mini): Timing chain elongation and intake valve carbon buildup.
4. Automatic Transmissions: Ford Powershift (dry dual-clutch) and VW DSG7 (DQ200 dry clutch) mechatronic and clutch shudder issues.
5. AdBlue SCR Systems: Urea crystallization leading to failed tanks and injector/pump module replacements in modern diesel engines.""",

    "french": """Principaux défauts mécaniques et moteurs à problèmes connus :
1. Moteur 1.2 PureTech (Peugeot, Citroën, DS, Opel) : Courroie de distribution immergée dans l'huile qui se désagrège, obstrue la crépine de pompe à huile, cause de fortes surconsommations d'huile et casses moteur.
2. Moteur 1.2 TCe (Renault, Dacia, Nissan) : Forte surconsommation d'huile liée à un défaut de segmentation et de pression dans le carter.
3. Moteur 1.6 THP (PSA / BMW / Mini) : Décalage de la chaîne de distribution et encrassement des soupapes.
4. Boîtes robotisées : Ford Powershift et VW DSG7 à sec (DQ200) sujettes aux pannes de mécatronique et d'embrayages.
5. Système AdBlue (Diesels récents BlueHDi) : Cristallisation de l'urée et défaillance de la pompe/réservoir indissociable."""
}

MAINTENANCE_CONTEXTS = {
    "darija_lat": "Suivi d l'entretien automobile. Nesh l-utilisateur ytebba3 l-vidange dyalo f le module 'Carnet d'Entretien' f le Dashboard Wakala.",
    "darija_ar": "تتبع صيانة السيارات وتغيير الزيت. ذكر المستخدم بإمكانية تسجيل صياناته في 'دفتر الصيانة' داخل منصة وكالة.",
    "arabic": "إدارة صيانة السيارات والفحص الدوري. ذكّر المستخدم بإمكانية تتبع مواعيد تغيير الزيت والصيانة عبر وحدة 'دفتر الصيانة' في منصة وكالة.",
    "english": "Vehicle maintenance and service tracking. Remind the user they can track oil changes and service history using the 'Service Book' in their Wakala Dashboard.",
    "french": "Gestion de l'entretien automobile. Rappelle que l'utilisateur peut suivre ses vidanges et révisions dans le module 'Carnet d'Entretien' de son Dashboard Wakala."
}

CUSTOMS_CONTEXTS = {
    "darija_lat": "Diwana w dedouanement dyal les voitures f l-Maroc. Chre7 tariqa dyal l-hisab w gol lih ysta3mel le simulateur d dedouanement f Wakala.",
    "darija_ar": "جمارك واستيراد السيارات في المغرب. اشرح طريقة الحساب بشكل واضح ووجه المستخدم إلى حاسبة الجمارك في منصة وكالة.",
    "arabic": "حساب الرسوم الجمركية لاستيراد السيارات في المغرب. اشرح الرسوم ووجّه المستخدم لاستخدام حاسبة الجمارك التفاعلية على منصة وكالة.",
    "english": "Automotive customs clearance and duties in Morocco. Explain the calculation criteria and direct the user to the Wakala Customs Simulator.",
    "french": "Dedouanement automobile au Maroc. Explique le calcul des droits de douane et oriente vers le simulateur de dedouanement Wakala."
}

CONSULTATIVE_DISCOVERY_CONTEXTS = {
    "darija_lat": """L-client baghi ychri tomobila walakin mazal ma7eddech koulchi.
Nta l-moustachar l-automobile d Wakala f l-mghrib.
L-qualification mbnia b charama 3la l-ab3ad t-tmanya (8 Dimensions) d Wakala (Prix d'acces/Budget, Praticite f l-mdina, Espace coffre/valisat, Cout reel/masarif, Ecologie/moteur propre, Securite NCAP, Performance, Motricite 4x4).
Silsilat d l-as2ila sSarima (8D) soual b soual :
1. Etape 1 (Prix d'acces / Budget) : Ila mazal ma3tach l-budget, sewlo b d-derhem (MAD / DH).
2. Etape 2 (Praticite f l-mdina) : Ila 3tana l-budget, sewlo wach kayfdel tomobila sghira sahla f l-parking f l-mdina wla format kber.
3. Etape 3 (Espace & Coffre) : Sewlo ch7al kaye7taj f l-coffre b l-valisat wla wach kaye7taj 7 d les places.
4. Etape 4 (Ecologie & Masarif d l-isti3mal) : Sewlo wach l-moteur l-hybride/electrique awla l-conso l-qlila hiya l-awlawiya.
5. Etape 5 (Securite NCAP, Motricite 4x4 wla Performance) : Sewlo 3la la securite certifiee (5 etoiles NCAP), 4x4 awla l-puissance.
6. Etape 6 (Recommandations finales 8D) : Mnin ykounou l-ma3loumat d les 8D kamlin, 3tih 2 tal 3 d les modeles mn l-catalogue k natija nihaiya m3a l-evaluation 8D, l-coffre b l-valisat w l-bloc JSON. Hbes l-as2ila d l-qualification.

Qawa3id sSarima :
- Sewel STRICTEMENT soual wahed f kol risala.
- Kol soual khesso ykoun b charama tied l wahed mn les 8 Dimensions d Wakala (mamnou3 as2ila kharja 3la les 8D).
- Matktech 3lih b les listes d les questions.
- Hder 100% b Darija b l-hrof l-latiniya w bla aucun emoji.""",

    "darija_ar": """الزبون مهتم بالبحث عن سيارة أو استشارة حول الشراء لكنه لم يحدد كل تفاصيله بعد.
أنت المستشار الأول وخبير السيارات في منصة وكالة (Wakala).
التأهيل كيعتمد 100% وبصرامة على الأبعاد الثمانية لوكالة (سعر الشراء/الميزانية، القيادة فالمدينة، اتساع الكوفير، مصاريف الاستعمال، المحرك النظيف، السلامة المعتمدة، قوة الموتور، الدفع الرباعي).
تسلسل مراحل الاستشارة الصارم على الأبعاد الثمانية (8D):
1. المرحلة 1 (سعر الشراء / الميزانية): إذا كانت الميزانية غير محددة، اسأل فقط عن الميزانية القصوى بالدرهم.
2. المرحلة 2 (العملية الحضرية وسهولة الركن): اسأل واش كيفضل طوموبيل صغيرة وساهلة فالباركينغ فالمدينة ولا طوموبيل كبر منها وأوسع.
3. المرحلة 3 (الكوفير والوسع): اسأل عن حجم الصندوق شحال كيحتاج (بعدد الفاليزات) ولا كيحتاج 7 د البلايص.
4. المرحلة 4 (الموتور النظيف ومصاريف ليسانس): اسأل واش الموتور الهجين (إيبريد) أو الكهربائي أولوية، ولا كيفضل مازوط/ليصانص باستهلاك ومصاريف قليلة.
5. المرحلة 5 (السلامة أو 4x4 أو قوة الموتور): اسأل عن السلامة المعتمدة (5 نجوم Euro NCAP)، الدفع الرباعي 4x4 ولا قوة الموتور والريبريز.
6. المرحلة 6 (التوصية والنتيجة النهائية 8D): بعد اكتمال الأبعاد الثمانية، رشح أفضل 2 إلى 3 سيارات مناسبة من الكتالوج كنتيجة نهائية مع تقييم الأبعاد الثمانية، ذكر سعة الصندوق بالفاليزات وإدراج كود JSON. توقف عن طرح أسئلة التأهيل.

شروط صارمة:
- اطرح سؤالاً واحداً فقط في كل رسالة بالدارجة المغربية.
- كل سؤال خاصو يركز حصرياً وبصرامة على واحد من الأبعاد الثمانية المعتمدة (8D).
- ممنوع طرح قائمة أسئلة متعددة دفعة واحدة.
- التزم 100% بالدارجة المغربية المكتوبة بالعربية وبدون أي إيموجي نهائياً.""",

    "arabic": """العميل يرغب في استشارة حول شراء سيارة في السوق المغربي ولكن لم يحدد بعد كل معاييره وتفضيلاته.
أنت كبير المستشارين والخبراء التقنيين لمنصة وكالة (Wakala).
يعتمد التأهيل حصرياً وبشكل صارم على الأبعاد الثمانية لمنصة وكالة (سعر الشراء/الميزانية، العملية الحضرية، سعة الأمتعة، كلفة الاستخدام، البيئة، السلامة المعتمدة، الأداء، الدفع والجر).
التسلسل التشخيصي الصارم للأبعاد الثمانية (8D) خطوة بخطوة:
1. الخطوة 1 (سعر الشراء / الميزانية): إذا لم تُحدد الميزانية، اسأل فقط عن الميزانية القصوى بالدرهم المغربي.
2. الخطوة 2 (العملية الحضرية): إذا عُرفت الميزانية، اسأل فقط عن الحاجة لسيارة مدمجة سهلة الركن في المدينة أم حجماً أكثر اتساعاً.
3. الخطوة 3 (المساحة وصندوق الأمتعة): اسأل فقط عن سعة صندوق الأمتعة المطلوبة (بعدد حقائب السفر) أو الحاجة إلى 7 مقاعد.
4. الخطوة 4 (البيئة وكلفة الاستخدام): اسأل عما إذا كان المحرك الهجين/الكهربائي النظيف أو التوفير الأقصى في الوقود وتكاليف التشغيل يمثل أولوية.
5. الخطوة 5 (السلامة المعتمدة، الأداء أو الدفع الرباعي): اسأل عن متطلبات السلامة المعتمدة Euro NCAP (5 نجوم)، قوة المحرك أو الدفع الرباعي 4x4.
6. الخطوة 6 (الترشيحات النهائية 8D): عند اكتمال الأبعاد الثمانية، قدم أفضل 2 إلى 3 سيارات من الكتالوج كنتيجة نهائية مع تقييم الأبعاد الثمانية، التعليل التقني، حجم الصندوق بعدد الحقائب وإدراج كتل JSON. توقف عن طرح أسئلة التأهيل.

قواعد قطعية:
- اطرح دائماً سؤالاً واحداً فقط في كل رسالة باللغة العربية الفصحى.
- يجب أن يرتبط كل سؤال بشكل صارم وحصري بأحد الأبعاد الثمانية المعتمدة (8D).
- تجنب تماماً طرح قوائم أسئلة متعددة.
- التزم 100% باللغة العربية الفصحى السليمة وبدون أي رموز تعبيرية (Emojis).""",

    "french": """Le client souhaite trouver ou acheter un véhicule au Maroc mais n'a pas encore défini l'ensemble de ses critères.
Tu es l'expert conseiller automobile d'élite de la plateforme Wakala.
La qualification s'appuie STRICTEMENT sur les 8 Dimensions Wakala : Prix d'accès, Praticité urbaine, Espace coffre, Coût réel d'usage, Écologie, Sécurité certifiée, Performance, Motricité.
SÉQUENCE STRICTE DE QUALIFICATION TOUR PAR TOUR (8D) :
1. Étape 1 (Prix d'accès) : Si le budget n'est pas encore précisé, demande UNIQUEMENT son budget maximum en Dirhams (MAD / DH).
2. Étape 2 (Praticité urbaine) : Si le budget est connu mais pas l'usage urbain, demande UNIQUEMENT s'il recherche un format compact facile à garer en ville ou un gabarit plus grand et spacieux.
3. Étape 3 (Espace & Habitabilité) : Si l'usage est connu, demande UNIQUEMENT son besoin en volume de coffre (en nombre de valises) ou s'il a besoin de 7 places.
4. Étape 4 (Écologie & Coût réel) : Demande si la motorisation propre (Hybride ou Électrique) ou l'économie de carburant et coûts réduits est une priorité.
5. Étape 5 (Sécurité certifiée, Performance ou Motricité 4x4) : Selon les priorités, demande son exigence sur la sécurité Euro NCAP (5★), la puissance moteur/reprises ou la transmission 4x4 tout-terrain.
6. Étape 6 (Recommandations finales 8D) : Une fois les critères 8D réunis, présente les 2 à 3 véhicules les plus pertinents du catalogue comme résultat final avec leurs scores 8D, arguments techniques, équivalence coffre en valises et blocs JSON de recommandation. Arrête de poser des questions de qualification.

RÈGLES IMPÉRATIVES :
- Pose STRICTEMENT UNE SEULE question par message en français.
- Chaque question doit impérativement et strictement qualifier l'une des 8 Dimensions Wakala (jamais de questions hors 8D comme la boîte de vitesses isolée).
- Ne fais JAMAIS de liste de questions ni de questionnaire.
- Reste 100% en français avec zéro émoji.""",

    "english": """The user is exploring buying a car in Morocco but has not yet specified all required preferences.
You are the elite automotive consultant for the Wakala platform.
Qualification strictly follows Wakala's 8 Core Dimensions: Access Price, Urban Practicality, Space & Luggage, Real Running Cost, Ecology, Certified Safety, Performance, Drivetrain/Motricity.
STRICT TURN-BY-TURN 8D DISCOVERY SEQUENCE:
1. Turn 1 (Access Price): If target budget is missing, ask ONLY for their maximum target budget in MAD.
2. Turn 2 (Urban Practicality): If budget is known, ask ONLY about their need for a compact city-friendly car easy to park vs a larger spacious vehicle.
3. Turn 3 (Space & Luggage): Ask ONLY for their luggage capacity requirement (in number of suitcases) or if they need 7 seats.
4. Turn 4 (Ecology & Running Cost): Ask if clean hybrid/electric propulsion or low fuel consumption and minimal running costs is a priority.
5. Turn 5 (Certified Safety, Performance or 4x4 Motricity): Ask about their requirement for top Euro NCAP safety (5★), engine power/responsiveness, or all-wheel drive 4x4 capability.
6. Turn 6 (Final 8D Recommendations): Once 8D criteria are gathered, present 2 to 3 tailored vehicle options from the catalogue with their 8D score evaluation, technical reasons, suitcase trunk capacity, and JSON recommendation blocks. Stop asking qualification questions.

STRICT CONSTRAINTS:
- Ask STRICTLY ONE question per response in English.
- Every question must strictly qualify one of Wakala's 8 Dimensions.
- Do NOT generate bulleted question lists or multiple questions.
- Answer 100% in English with zero emojis."""
}


def get_fallback_discovery_question(
    detected_lang: str,
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    max_price: Optional[int] = None,
) -> str:
    all_user_text = message.lower()
    if history:
        all_user_text = " ".join(m.get("content", "").lower() for m in history if m.get("role") == "user") + " " + all_user_text

    # 1. Dimension 1: Prix d'accès (Budget)
    extracted_price = max_price
    if extracted_price is None:
        budget_match = re.search(r'(\d+[\s,.]?\d*)\s*(?:k|000|mad|dhs?|dirhams?|درهم|دراهم|mlyon|melyon|million|مليون|الف|ألف)\b', all_user_text)
        if budget_match:
            val_str = budget_match.group(1).replace(' ', '').replace(',', '').replace('.', '')
            if val_str.isdigit():
                val = int(val_str)
                extracted_price = val * 1000 if (val < 1000 and 'k' in all_user_text) else val
        else:
            raw_num_match = re.search(r'\b([4-9]\d{4}|[1-9]\d{5,7})\b', all_user_text)
            if raw_num_match:
                extracted_price = int(raw_num_match.group(1))

    has_budget = extracted_price is not None

    # 2. Dimension 2: Praticité urbaine (City / Compact / Easy parking vs spacious)
    praticite_keywords = [
        'ville', 'city', 'urbain', 'urbaine', 'compact', 'compacte', 'parking', 'garer',
        'autoroute', 'highway', 'mixte', 'both', 'citadine', 'hatchback',
        'مدينة', 'المدينة', 'حضرية', 'مدمجة', 'ركن', 'الركنة', 'باركينغ', 'سيتادين',
        'فالمدينة', 'طريق سيار', 'بجوج'
    ]
    has_praticite = any(k in all_user_text for k in praticite_keywords)

    # 3. Dimension 3: Espace (Trunk volume, suitcases, 5 vs 7 seats)
    space_keywords = [
        'coffre', 'valise', 'valises', 'bagage', 'bagages', 'trunk', 'suitcase', 'suitcases',
        'luggage', 'boot', '7 places', '7 seats', '7 مقاعد', '7 بلايص', 'places', 'seats',
        'famille', 'family', 'enfants', 'poussette', 'أمتعة', 'حقائب', 'صندوق', 'كوفير', 'عائلة'
    ]
    has_space = any(k in all_user_text for k in space_keywords)

    # 4. Dimension 4 & 5: Coût réel & Écologie (TCO, fuel economy, hybrid/electric)
    eco_cost_keywords = [
        'hybride', 'hybrid', 'electrique', 'électrique', 'electric', 'ev', 'phev', 'diesel', 'essence', 'petrol',
        'consommation', 'conso', 'économie', 'economie', 'running cost', 'running costs', 'low fuel',
        'coût', 'coûts', 'frais', 'vignette',
        'مازوط', 'مازوت', 'بنزين', 'ليصانص', 'هجين', 'ايبريد', 'إيبريد', 'كهربائي',
        'استهلاك', 'توفير', 'تكاليف', 'مصاريف', 'صرف', 'اقتصاد'
    ]
    has_eco_cost = any(k in all_user_text for k in eco_cost_keywords)

    # 5. Dimension 6: Sécurité (Euro NCAP, active safety, ADAS)
    safety_keywords = [
        'securite', 'sécurité', 'security', 'safety', 'ncap', 'crash', 'crash-test', 'adas', 'isofix',
        'étoiles', 'etoiles', 'stars', '5★', '4★',
        'سلامة', 'أمان', 'حماية'
    ]
    has_safety = any(k in all_user_text for k in safety_keywords)

    # 6. Dimension 7: Motricité (4x4 / AWD vs 2WD)
    motricite_keywords = [
        '4x4', '4wd', 'awd', 'integrale', 'intégrale', 'tout-terrain', 'tout terrain', 'offroad', 'off-road',
        'piste', 'montagne', 'motricité', 'motricite', 'garde au sol', '2wd', '2 roues', 'deux roues',
        'دفع رباعي', 'دفع ثنائي', 'رباعي', 'ثنائي'
    ]
    has_motricite = any(k in all_user_text for k in motricite_keywords)

    # 7. Dimension 8: Performance (Power, acceleration, dynamics)
    performance_keywords = [
        'performance', 'puissance', 'power', 'reprises', 'dynamique', 'sport', 'sportif', 'ch', 'hp', 'vitesse',
        'قوة', 'تسارع', 'أداء', 'رياضي'
    ]
    has_performance = any(k in all_user_text for k in performance_keywords)

    formatted_price = f"{extracted_price:,}".replace(",", " ") if extracted_price else ""

    # Strict 8 Dimensions Progression
    if not has_budget:
        return {
            "french": "Quel est votre budget maximum en MAD pour cette voiture ?",
            "english": "What is your maximum target budget in MAD for this car?",
            "arabic": "ما هي ميزانيتك القصوى بالدرهم لشراء هذه السيارة؟",
            "darija_ar": "شحال هي الميزانية القصوى ديالك بالدرهم لهاد الطوموبيل؟",
            "darija_lat": "Ch7al hiya l-budget maximum dyalek b d-derhem l had tomobil?",
        }.get(detected_lang, "What is your maximum target budget in MAD for this car?")

    if not has_praticite:
        price_prefix = f"Avec un budget de {formatted_price} DH, " if formatted_price else ""
        price_prefix_en = f"With a budget of {formatted_price} DH, " if formatted_price else ""
        price_prefix_ar = f"مع ميزانية {formatted_price} درهم، " if formatted_price else ""
        price_prefix_darija = f"مع ميزانية {formatted_price} درهم، " if formatted_price else ""
        return {
            "french": f"{price_prefix}pour vos trajets quotidiens, préférez-vous un format compact facile à garer en ville ou un gabarit plus spacieux ?",
            "english": f"{price_prefix_en}for daily driving, do you prefer a compact car easy to park in the city or a more spacious vehicle?",
            "arabic": f"{price_prefix_ar}لتنقلاتك اليومية، هل تفضل سيارة مدمجة وسهلة الركن في المدينة أم حجماً أكثر اتساعاً؟",
            "darija_ar": f"{price_prefix_darija}فالتحركات اليومية، واش كتفضل طوموبيل صغيرة وساهلة فالركنة فالمدينة ولا طوموبيل واسعة وكبيرة؟",
            "darija_lat": f"{price_prefix}f l-isti3mal l-yawmi, wach katfeddel tomobil sghira sahla f l-parking wla tomobil was3a w kbira?",
        }.get(detected_lang, f"{price_prefix_en}for daily driving, do you prefer a compact car easy to park in the city or a more spacious vehicle?")

    if not has_space:
        return {
            "french": "De combien de place pour les bagages avez-vous besoin (en nombre de valises) ou cherchez-vous 7 places ?",
            "english": "How much luggage space do you need (in suitcases), or are you looking for 7 seats?",
            "arabic": "كم من مساحة الأمتعة تحتاج (بعدد الحقائب)، أم تبحث عن 7 مقاعد؟",
            "darija_ar": "شحال كتحتاج ديال المساحة للباݣاج (بعدد الفاليزات)، ولا كتقلب على 7 د البلايص؟",
            "darija_lat": "Ch7al kaye7taj l-coffre dyalek b l-valisat, wla katqelleb 3la 7 d les places?",
        }.get(detected_lang, "How much luggage space do you need (in suitcases), or are you looking for 7 seats?")

    if not has_eco_cost:
        return {
            "french": "La motorisation hybride ou électrique propre est-elle une priorité, ou préférez-vous une motorisation thermique à faible consommation ?",
            "english": "Is clean hybrid or electric power a priority for you, or do you prefer a fuel-efficient combustion engine?",
            "arabic": "هل المحرك الهجين أو الكهربائي النظيف أولوية بالنسبة لك، أم تفضل محركاً عادياً باستهلاك اقتصادي؟",
            "darija_ar": "واش الموتور الهجين (إيبريد) ولا الكهربائي أولوية عندك، ولا كتفضل موتور عادي واقتصادي فالمصاريف؟",
            "darija_lat": "Wach l-moteur hybride wla electrique awlawiya, wla katfeddel moteur classique b conso qlila?",
        }.get(detected_lang, "Is clean hybrid or electric power a priority for you, or do you prefer a fuel-efficient combustion engine?")

    if not has_safety:
        return {
            "french": "Quelle importance accordez-vous à la sécurité certifiée et à une note maximale Euro NCAP (5★) ?",
            "english": "How important is certified safety and a top Euro NCAP rating (5★) to you?",
            "arabic": "ما مدى أهمية السلامة المعتمدة والتقييم الأقصى Euro NCAP (5 نجوم) بالنسبة لك؟",
            "darija_ar": "شحال مهمة عندك السلامة المعتمدة وأعلى نقطة فالأمان (5 نجوم Euro NCAP)؟",
            "darija_lat": "Ch7al mohima 3ndek la securite certifiee w a3la noqta (5 etoiles Euro NCAP)?",
        }.get(detected_lang, "How important is certified safety and a top Euro NCAP rating (5★) to you?")

    if not has_motricite:
        return {
            "french": "Avez-vous besoin d'une motricité 4x4 / transmission intégrale (AWD) pour les pistes, ou d'une 2 roues motrices standard ?",
            "english": "Do you need 4x4 / all-wheel drive (AWD) for rough terrain, or standard 2WD?",
            "arabic": "هل تحتاج إلى دفع رباعي (4x4 / AWD) للطرق الوعرة، أم دفع ثنائي عادي (2WD)؟",
            "darija_ar": "واش كتحتاج الدفع الرباعي (4x4) للبستات والعقابي، ولا دفع عادي (2WD)؟",
            "darija_lat": "Wach kaye7taj 4x4 awla transmission integrale AWD l l-piste, wla 2 roues motrices standard?",
        }.get(detected_lang, "Do you need 4x4 / all-wheel drive (AWD) for rough terrain, or standard 2WD?")

    if not has_performance:
        return {
            "french": "Privilégiez-vous la puissance moteur et les reprises dynamiques sur autoroute ?",
            "english": "Do you prioritize engine power and highway acceleration responsiveness?",
            "arabic": "هل تفضل قوة المحرك والتسارع القوي على الطرق السريعة؟",
            "darija_ar": "واش كتفضل الموتور القوي والتسارع والريبريز فالطريق الكبيرة؟",
            "darija_lat": "Wach katfeddel l-moteur l-qwi w les reprises f l-autoroute?",
        }.get(detected_lang, "Do you prioritize engine power and highway acceleration responsiveness?")

    return {
        "french": "Parfait ! Voici les modèles du catalogue qui répondent le mieux à vos exigences sur l'ensemble des 8 dimensions.",
        "english": "Great! Here are the catalogue models that best match your preferences across all 8 dimensions.",
        "arabic": "ممتاز! إليك السيارات الأنسب لمعاييرك وتفضيلاتك وفق تقييم الأبعاد الثمانية.",
        "darija_ar": "مزيان بزاف! ها هما الطوموبيلات اللي كيطابقو المعايير ديالك على حساب الأبعاد الثمانية كاملين.",
        "darija_lat": "Mezyan bzaf! Hahoma les modeles li kaynasbou l-ma3ayir dyalek 3la 7sab les 8 dimensions.",
    }.get(detected_lang, "Great! Here are the catalogue models that best match your preferences across all 8 dimensions.")


async def chat_stream(message: str, history: List[Dict[str, str]], language: Optional[str] = None) -> AsyncIterable[str]:
    """Gère la logique complète du chat et génère la réponse 100% dans la langue du client sur tout le secteur automobile, garantie sans emojis ni fuite de réflexion."""
    clean_message = redact_pii(sanitize_input(message))
    
    # 1. Détection universelle de la langue avec mémoire de contexte et respect de la langue explicite
    detected_lang = detect_language(clean_message, history=history, explicit_language=language)

    # Keep the assistant useful and safe: it is an automotive expert, not a
    # general-purpose chatbot. This response is intentionally immediate.
    if not is_automotive_domain_request(clean_message, history):
        response = OUT_OF_DOMAIN_RESPONSES.get(detected_lang, OUT_OF_DOMAIN_RESPONSES['french'])
        yield response
        return
    
    # 2. Analyse d'intention ultra-rapide
    intent_data = await analyze_intent(clean_message, history)
    intent = intent_data.get("intent", "general_advice")
    max_price = intent_data.get("max_price")
    search_query = intent_data.get("search_query") or clean_message
    
    # 3. Gestion instantanée des salutations simples (0 latence, 100% langue cible, 0 emoji)
    if intent == "greeting":
        greeting_text = GREETING_RESPONSES.get(detected_lang, GREETING_RESPONSES.get("french", "Bonjour !"))
        words = greeting_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.02)
        return

    # 4. Contexte adapté à la langue et à l'intention
    is_car_search_active = False
    if intent == "car_search":
        is_specific = is_specific_search_request(clean_message, max_price, history)
        if is_specific:
            is_car_search_active = True
            context = await retrieve_vehicles(search_query, max_price=max_price)
        else:
            context = CONSULTATIVE_DISCOVERY_CONTEXTS.get(detected_lang, CONSULTATIVE_DISCOVERY_CONTEXTS.get("french", ""))
    elif intent == "auto_expert":
        context = EXPERT_CONTEXTS.get(detected_lang, EXPERT_CONTEXTS.get("french", ""))
    elif intent == "maintenance_check":
        context = MAINTENANCE_CONTEXTS.get(detected_lang, MAINTENANCE_CONTEXTS.get("french", ""))
    elif intent == "customs":
        context = CUSTOMS_CONTEXTS.get(detected_lang, CUSTOMS_CONTEXTS.get("french", ""))
    else:
        context = "Automotive sector domain question. Answer thoroughly, accurately, and professionally as a leading automotive industry authority."
    
    # 5. Construction dynamique du System Prompt 100% dans la langue cible
    system_prompt = build_system_prompt(detected_lang, context, is_car_search=is_car_search_active)
    
    raw_messages = [{"role": "system", "content": system_prompt}]
    
    recent_history = history[-6:] if len(history) > 6 else history
    for msg in recent_history:
        clean_content = redact_pii(sanitize_input(msg.get("content", "")))
        clean_content = remove_emojis(clean_content)
        role = "user" if msg.get("role") == "user" else "assistant"
        if role == "assistant" and len(clean_content) > 400:
            clean_content = clean_content[:400] + "..."
        raw_messages.append({"role": role, "content": clean_content})
            
    raw_messages.append({"role": "user", "content": remove_emojis(clean_message)})
    
    # Discovery questions apply ONLY to car_search intent (when user actually wants to purchase/find cars)
    is_discovery_request = (intent == "car_search")

    # 6. Stream de génération avec filtrage systématique d'emojis et des balises de réflexion (<think>)
    if is_discovery_request:
        fallback_text = get_fallback_discovery_question(detected_lang, clean_message, history, max_price)
    else:
        fallback_text = {
            "french": "Je peux vous aider avec votre question automobile. Pouvez-vous préciser votre besoin ?",
            "english": "I can help with your automotive question. Could you clarify what you need?",
            "arabic": "يمكنني مساعدتك في سؤالك عن السيارات. هل يمكنك توضيح حاجتك؟",
            "darija_ar": "نقدر نعاونك فالسؤال ديالك على السيارات. واش تقدر توضح ليا الحاجة ديالك؟",
            "darija_lat": "N9der n3awnek f sou2al dyalek 3la tomobilat. Wach t9der twadda7 l7aja dyalek?",
        }.get(detected_lang, "I can help with your automotive question. Could you clarify what you need?")

    stream_source = _stream_openrouter_direct(raw_messages, fallback_text, detected_lang=detected_lang, query_text=clean_message)

    thinking_buffer = ""
    is_filtering_thinking = False
    started_yielding = False

    THINKING_MARKERS = (
        "<think>",
        "Here's a thinking process:",
        "Here is a thinking process:",
        "Thinking Process:",
        "Thinking process:",
        "Thought process:",
        "Thought:",
        "Reasoning Process:",
        "1. **Analyze",
        "1. Analyze",
    )

    async for content in stream_source:
        if not content:
            continue
        
        if not started_yielding:
            thinking_buffer += content
            
            if any(m in thinking_buffer for m in THINKING_MARKERS):
                is_filtering_thinking = True
                
            if is_filtering_thinking:
                if "</think>" in thinking_buffer:
                    after_think = thinking_buffer.split("</think>", 1)[1]
                    clean = remove_emojis(after_think)
                    if clean.strip():
                        started_yielding = True
                        yield clean.lstrip()
                    thinking_buffer = ""
                    is_filtering_thinking = False
                elif re.search(r'\n\n(?=[A-Z\*\#\-\u0600-\u06FF])', thinking_buffer):
                    scrubbed = scrub_thinking(thinking_buffer)
                    if scrubbed:
                        started_yielding = True
                        yield remove_emojis(scrubbed)
                        thinking_buffer = ""
                        is_filtering_thinking = False
                continue
            else:
                if len(thinking_buffer) > 25 or "\n" in thinking_buffer:
                    started_yielding = True
                    yield remove_emojis(thinking_buffer)
                    thinking_buffer = ""
                    continue
        else:
            clean_chunk = remove_emojis(content)
            if clean_chunk:
                yield clean_chunk

    if thinking_buffer:
        final_clean = scrub_thinking(thinking_buffer) if is_filtering_thinking else thinking_buffer
        final_clean = remove_emojis(final_clean)
        if final_clean.strip():
            started_yielding = True
            yield final_clean

    # Some free providers spend the entire budget on hidden reasoning even
    # when reasoning exclusion is requested. Never leave the UI empty in that
    # case: return one localized, useful next step.
    if not started_yielding and is_discovery_request:
        yield get_fallback_discovery_question(detected_lang, clean_message, history, max_price)


def get_automotive_knowledge_fallback(detected_lang: str, query: str) -> Optional[str]:
    """Provide accurate automotive knowledge fallback when cloud LLMs are unreachable."""
    q = (query or "").lower().strip()
    if "amg" in q:
        return {
            "darija_ar": "AMG هو الفرع الرياضي وعالي الأداء ديال مرسيدس-بنز (Mercedes-Benz). كيتخصص فمحركات قوية معدلة يدوياً ('رجل واحد، محرك واحد')، شاسيه رياضي وتصميم هجومي (بحال A45 AMG، C63 AMG، G63). واش باغي معلومات على شي موديل محدد؟",
            "darija_lat": "AMG houwa l-far3 r-riyadi dyal l-performance l-3alya 3nd Mercedes-Benz. M3roufin b les moteurs 9wiyin m9adin b l-yed ('one man, one engine'), chassis sport w design hjoumi (bhal A45, C63, G63 AMG). Wach bghiti t3ref 3la chi modele precis?",
            "french": "AMG (Aufrecht, Melcher et Großaspach) est la division sportive et haute performance de Mercedes-Benz. Elle est réputée pour ses moteurs puissants assemblés à la main ('un homme, un moteur'), ses châssis affûtés et son design agressif (ex. A45, C63, G63 AMG). Souhaitez-vous des détails sur un modèle en particulier ?",
            "arabic": "AMG هو قسم الأداء العالي والرياضي التابع لشركة مرسيدس-بنز (Mercedes-Benz). يشتهر بمحركاته القوية المجمعة يدوياً وأنظمة التعليق الرياضية والتصاميم الحصرية (مثل A45 وC63 وG63 AMG). هل تود معرفة تفاصيل حول طراز معين؟",
            "english": "AMG is the high-performance division of Mercedes-Benz, famous for hand-built high-output engines ('one man, one engine'), tuned chassis, and aggressive styling (such as A45, C63, G63 AMG). Would you like details on a specific model?",
        }.get(detected_lang, "AMG is the high-performance division of Mercedes-Benz, famous for hand-built engines and sports performance.")

    if "dacia" in q:
        return {
            "darija_ar": "داسيا (Dacia) علامة تابعة لمجموعة رونو ومصنعة محلياً فالمغرب (طنجة والدار البيضاء). معروفة بالموثوقية، واقتصادية فالاستهلاك وقطع الغيار متوفرة ورخيصة. الموديلات الأكثر شعبية فالمغرب هي سانديرو (Sandero)، وداستر (Duster SUV)، ولوغان (Logan)، وجوغر (Jogger). واش باغي تعرف تفاصيل على شي موديل بالخصوص؟",
            "darija_lat": "Dacia marque tab3a l Renault w katssna3 f l-Meghrib (Tanger w Casablanca). M3roufa b l-fiabilite, l-iqtissad f l-mazot w l-pièces mojoudin w rkhas. Les modeles li kaynin: Sandero, Duster, Logan, w Jogger. Wach bghiti m3lomat 3la chi modele precis?",
            "french": "Dacia est une marque du groupe Renault produite au Maroc (usines de Tanger et Casablanca). Elle est reconnue pour sa robustesse, sa grande fiabilité et ses coûts d'usage très économiques. Les modèles les plus vendus au Maroc sont la Sandero, le Duster, la Logan et le Jogger. Souhaitez-vous des informations détaillées sur l'un de ces modèles ?",
            "arabic": "داسيا هي علامة تجارية تابعة لمجموعة رينو وتُصنع محلياً في المغرب (مصانع طنجة والدار البيضاء). تشتهر بالموثوقية العالية والاقتصاد الكبير في استهلاك الوقود وانخفاض تكلفة قطع الغيار والصيانة. أبرز موديلاتها: سانديرو، داستر، لوغان، وجوغر. هل تود معرفة معلومات عن طراز محدد؟",
            "english": "Dacia is a brand under the Renault Group manufactured locally in Morocco (Tangier and Casablanca). It is celebrated for durability, low maintenance costs, and exceptional fuel efficiency. Popular models in Morocco include the Sandero, Duster, Logan, and Jogger. Would you like details on a specific model?",
        }.get(detected_lang, "Dacia is a Renault Group brand produced in Morocco, known for reliability and affordable maintenance.")

    return None
