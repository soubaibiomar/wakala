import re
import json
import asyncio
import httpx
from typing import AsyncIterable, List, Dict, Any, Optional
try:
    from langchain_openai import ChatOpenAI
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    class ChatOpenAI:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def bind(self, *args: Any, **kwargs: Any) -> Any: return self
    class OllamaEmbeddings:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        async def aembed_query(self, text: str) -> list[float]: return []
        def embed_query(self, text: str) -> list[float]: return []
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

async def _stream_ollama_direct(messages_payload: list[dict]) -> AsyncIterable[str]:
    """Stream des tokens en direct depuis Ollama local via API native avec haute résilience."""
    ollama_base = (settings.OLLAMA_BASE_URL or "http://localhost:11434").replace("/v1", "").rstrip("/")
    url = f"{ollama_base}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL_TEXT or "qwen3:8b",
        "messages": messages_payload,
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_predict": 450,
        }
    }
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                delta = data.get("message", {}).get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                pass
                else:
                    # Fallback OpenAI-compatible endpoint on Ollama
                    openai_url = f"{ollama_base}/v1/chat/completions"
                    openai_payload = {
                        "model": settings.OLLAMA_MODEL_TEXT or "llama3.2:1b",
                        "messages": messages_payload,
                        "stream": True,
                        "temperature": 0.2,
                        "max_tokens": 450,
                    }
                    async with client.stream("POST", openai_url, json=openai_payload) as resp2:
                        async for line2 in resp2.aiter_lines():
                            if line2.startswith("data: "):
                                data_str2 = line2[6:].strip()
                                if data_str2 == "[DONE]":
                                    break
                                try:
                                    d2 = json.loads(data_str2)
                                    delta2 = d2["choices"][0].get("delta", {}).get("content", "")
                                    if delta2:
                                        yield delta2
                                except Exception:
                                    pass
    except Exception as e:
        print(f"[Ollama Direct Stream Fallback Error] {e}")


async def _stream_openrouter_direct(messages_payload: list[dict]) -> AsyncIterable[str]:
    """Stream des tokens depuis OpenRouter avec basculement automatique et transparent sur Ollama en cas de quota épuisé (429/402), erreur réseau ou timeout."""
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://wakala.ma",
        "X-Title": "Wakala Platform",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages_payload,
        "stream": True,
        "temperature": 0.2,
        "max_tokens": 650,
    }
    url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
    
    yielded_any = False
    should_fallback = False
    
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                # Si quota épuisé (402, 429), erreur serveur (5xx) ou auth (401)
                if response.status_code != 200:
                    print(f"[OpenRouter Status {response.status_code}] Basculement automatique transparent vers Ollama local...")
                    should_fallback = True
                else:
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
    except Exception as e:
        print(f"[OpenRouter Stream Exception: {e}] Basculement automatique transparent vers Ollama local...")
        should_fallback = True

    # Si OpenRouter a échoué ou n'a renvoyé aucun token, on relaie immédiatement vers Ollama
    if should_fallback or not yielded_any:
        async for chunk in _stream_ollama_direct(messages_payload):
            yield chunk


# Define the models
def get_llm():
    if settings.OPENROUTER_API_KEY:
        return ChatOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            model=settings.OPENROUTER_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            temperature=0.2,
            max_tokens=450,
            request_timeout=30.0,
            timeout=30.0,
            default_headers={
                "HTTP-Referer": "https://wakala.ma",
                "X-Title": "Wakala Platform",
            }
        )
    api_key = settings.OPENAI_API_KEY or "ollama"
    return ChatOpenAI(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL_TEXT,
        api_key=api_key,
        temperature=0.2,
        max_tokens=380,
        request_timeout=25.0,
        timeout=25.0,
        extra_body={
            "options": {
                "num_ctx": 4096,
                "num_predict": 380,
                "repeat_penalty": 1.15,
            }
        }
    )

_ollama_base = settings.OLLAMA_BASE_URL.replace("/v1", "") if settings.OLLAMA_BASE_URL else "http://localhost:11434"
embeddings_model = OllamaEmbeddings(base_url=_ollama_base, model="bge-m3")

# ─── Filtre strict d'emojis ──────────────────────────────────
EMOJI_PATTERN = re.compile(
    r'[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\uD83C-\uDBFF\uDC00-\uDFFF]|[\u2300-\u23FF]|[\u2B50\u2B55\u2934\u2935\u25AA\u25AB\u25FE\u25FD\u25FB\u25FC\u25B6\u25C0\u3030\u303D\u3297\u3299\uFE0F]'
)


def remove_emojis(text: str) -> str:
    """Supprime impérativement tous les emojis du texte."""
    if not text:
        return ""
    cleaned = EMOJI_PATTERN.sub('', text)
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    return cleaned


# ─── Dictionnaires de détection de langue ─────────────────────
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
    'طوموبيل', 'طوموبيلا', 'طوموبيلات', 'سيارات', 'شحال', 'بشحال', 'مزيان', 'مزيانة',
    'لاباس', 'كي داير', 'خويا', 'أشمن', 'فين', 'بلاصة', 'فلوس', 'مليون', 'سنتيم',
    'ديك', 'هاد', 'هادو', 'عفاك', 'شكرا', 'زوينة', 'زوين', 'شنو', 'هما', 'فيهم', 'مشاكل', 'مشكل'
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
    'looking for', 'want to buy', 'i want', 'i need', 'please'
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


def detect_language(text: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """Détecte avec précision la langue de la requête utilisateur avec mémoire de contexte."""
    t = text.lower().strip()
    
    # 1. Caractères arabes
    if re.search(r'[\u0600-\u06FF]', text):
        if any(kw in text for kw in DARIJA_ARABIC_KEYWORDS):
            return "darija_ar"
        return "arabic"

    # 2. Chiffres Arabizi ou Darija Latin
    if re.search(r'[a-zA-Z]+[3795]|[3795][a-zA-Z]+', t):
        return "darija_lat"

    words = set(re.findall(r'\b[a-zA-Z0-9_\-а-яА-ЯёЁüäößçğışñáéíóúàèìòùâêîôûãõ]+\b', t))
    
    # Darija Latin
    if words.intersection(DARIJA_LATIN_KEYWORDS):
        return "darija_lat"
    darija_patterns = [
        'salam', 'slm', 'labas', 'bghit', 'kayna', 'chhal', 'chno homa', 'fihom machakil',
        'li fihom', 'chno howa', 'wach kayn', 'ki dayr', 'chhal taman', 'gol lia'
    ]
    if any(p in t for p in darija_patterns):
        return "darija_lat"

    # Français (prioritaire dans l'écosystème marocain)
    if words.intersection(FRENCH_KEYWORDS) or any(t.startswith(kw) for kw in ['bonjour', 'salut', 'coucou', 'bonsoir', 'je cherche', 'quels sont', 'quel est', 'combien', 'comment', 'pourquoi', 'est-ce']):
        return "french"

    # Anglais
    if len(words.intersection(ENGLISH_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['hello', 'hi ', 'hey ', 'how ', 'what ', 'where ', 'which ', 'i want', 'i need', 'looking for', 'tell me']):
        return "english"

    # Russe
    if re.search(r'[\u0400-\u04FF]', text) or words.intersection(RUSSIAN_KEYWORDS):
        return "russian"

    # Chinois
    if re.search(r'[\u4e00-\u9fff]', text):
        return "chinese"

    # Japonais
    if re.search(r'[\u3040-\u30ff]', text):
        return "japanese"

    # Espagnol (exige 2 mots distincts ou salutation explicite)
    if len(words.intersection(SPANISH_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['hola', 'buenos días', 'buenas tardes', 'qué ', 'cómo ', 'cuánto ']):
        return "spanish"

    # Allemand
    if len(words.intersection(GERMAN_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['hallo', 'guten tag', 'guten morgen', 'wie ', 'was ']):
        return "german"

    # Italien
    if len(words.intersection(ITALIAN_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['ciao', 'buongiorno', 'buonasera', 'come ', 'cosa ']):
        return "italian"

    # Portugais
    if len(words.intersection(PORTUGUESE_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['olá', 'ola', 'bom dia', 'boa tarde', 'como ']):
        return "portuguese"

    # Turc
    if len(words.intersection(TURKISH_KEYWORDS)) >= 2 or any(t.startswith(kw) for kw in ['merhaba', 'selam', 'nasılsınız']):
        return "turkish"

    # 3. Mémoire de contexte sur les réponses courtes (chiffres, noms de modèles, oui/non)
    if history:
        for prev in reversed(history):
            if prev.get("role") == "user":
                prev_text = prev.get("content", "")
                prev_lang = detect_language(prev_text, history=None)
                if prev_lang != "french":
                    return prev_lang

    # Français par défaut
    return "french"


# ─── Générateur de System Prompt ─────────────────────────────
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


# ─── Marques et modèles connus pour détection de précision ───
KNOWN_BRANDS_MODELS = [
    # Marques
    'dacia', 'renault', 'peugeot', 'hyundai', 'volkswagen', 'vw', 'fiat', 'citroen', 'citroën',
    'ford', 'kia', 'toyota', 'audi', 'bmw', 'mercedes', 'mercedes-benz', 'jeep', 'nissan',
    'skoda', 'seat', 'opel', 'honda', 'volvo', 'land rover', 'range rover', 'alfa romeo',
    'porsche', 'suzuki', 'byd', 'mg', 'chery', 'geely', 'changan', 'dongfeng', 'haval',
    'jac', 'mazda', 'mitsubishi', 'mini', 'lexus', 'jaguar', 'maserati', 'cupra', 'ds',
    'omoda', 'jaecoo', 'baic', 'seres', 'dfsk', 'tesla',
    # Modèles populaires
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
    """Détermine si la demande de véhicule est suffisamment qualifiée pour recommander des modèles précis.
    
    Requires at least 3 qualifying signals (budget + 2 descriptors, or brand/model + budget, etc.)
    to avoid premature vehicle search during consultative discovery.
    """
    msg = message.lower()
    score = 0
    
    # Combine current message with history for context
    all_user_text = msg
    if history:
        all_user_text = " ".join(m.get("content", "").lower() for m in history if m.get("role") == "user") + " " + msg
    
    # 1. Budget spécifié (current message or history)
    if max_price is not None:
        score += 1
    elif re.search(r'\b\d+\s*(?:k|000|mad|dh|dirham|درهم|mlyon|melyon|million|مليون|الف|ألف)\b', all_user_text):
        score += 1

    # 2. Marque ou modèle précis → counts as 2 (strong qualifier)
    if any(b in all_user_text for b in KNOWN_BRANDS_MODELS):
        score += 2
        
    # 3. Descripteurs clés (fuel, transmission, body style, etc.)
    descriptors = ['diesel', 'essence', 'hybride', 'hybrid', 'electrique', 'électrique', 'automatique', 'manuelle', 'suv', 'citadine', 'berline', '7 places', 'familiale', 'break', 'pick-up', 'pickup', 'urbain', 'ville', 'autoroute', 'route', 'mixte']
    score += sum(1 for d in descriptors if d in all_user_text)

    # Need at least 3 qualifying signals to trigger vehicle search
    return score >= 3


def build_system_prompt(detected_lang: str, context: str, is_car_search: bool = False) -> str:
    """Construit un prompt système d'expert automobile mondial adapté à la langue demandée."""
    target_lang_name = LANGUAGE_NAMES.get(detected_lang, "the exact same language as the user's query")
    
    rec_rule_darija_lat = """4. CATALOGUE VEHICLES: When recommending specific cars from the CONTEXT, include the JSON block:
```json
{
  "type": "CAR_RECOMMENDATION",
  "id": "ID",
  "brand": "BRAND",
  "model": "MODEL",
  "year": 2022,
  "price": 140000
}
```""" if is_car_search else "4. CONSULTATIVE DISCOVERY: When the user is exploring buying a car without enough details, do NOT output fake JSON blocks or recommend random cars. Ask ONLY ONE question per message. Follow this order across multiple turns: 1st turn → Budget, 2nd turn → Usage (city/highway), 3rd turn → Fuel type, 4th turn → Transmission, 5th turn → Body style. Wait for the client's answer before asking the next question."

    rec_rule_darija_ar = "4. عند التوصية بسيارات من السياق أرفق كود JSON الخاص بكل سيارة." if is_car_search else "4. الاستشارة والاكتشاف قبل التوصية: عندما يرغب المستخدم في شراء سيارة دون تحديد معاييره، لا تصدر أي كتل JSON أو ترشيحات عشوائية. اطرح سؤالاً واحداً فقط في كل رسالة. الترتيب: الرسالة الأولى ← الميزانية، الثانية ← نوع الاستعمال، الثالثة ← الوقود، الرابعة ← ناقل الحركة، الخامسة ← نوع الهيكل. انتظر جواب العميل قبل طرح السؤال التالي."

    rec_rule_ar = "4. عند التوصية بسيارات من السياق أرفق كود JSON الخاص بها." if is_car_search else "4. الاستشارة والتشخيص قبل التوصية: عند رغبة العميل في شراء سيارة دون معايير واضحة، لا تدرج أي كتل JSON أو اقتراحات عشوائية. اطرح سؤالاً تشخيصياً واحداً فقط في كل رسالة. الترتيب عبر الرسائل: 1← الميزانية، 2← طبيعة القيادة، 3← نوع الوقود، 4← ناقل الحركة، 5← فئة السيارة. انتظر رد العميل قبل الانتقال للسؤال الموالي."

    rec_rule_gen = """5. CATALOGUE VEHICLES: When recommending specific vehicles from the CONTEXT, insert the standard JSON block:
```json
{
  "type": "CAR_RECOMMENDATION",
  "id": "VEHICLE_ID",
  "brand": "BRAND",
  "model": "MODEL",
  "year": 2022,
  "price": 140000
}
```""" if is_car_search else f"5. CONSULTATIVE DIAGNOSIS: When a user inquires about buying or finding a car without specific parameters, do NOT output any JSON blocks or random vehicle picks. Ask ONLY ONE qualifying question per message in {target_lang_name}. Follow this strict turn-by-turn order: 1st message → Budget in MAD, 2nd → Daily usage (city/highway), 3rd → Fuel type (Diesel/Petrol/Hybrid), 4th → Transmission (Manual/Automatic), 5th → Body style. Always wait for the client's answer before moving to the next question."

    if detected_lang == "darija_lat":
        return f"""You are the expert automotive consultant for the Wakala platform in Morocco.

CRITICAL RULES:
1. LANGUAGE RULE: You MUST answer 100% in natural Moroccan Darija written in Latin script (e.g. 'Kaynin ba3d les modeles w les moteurs li ma3roufin b machakil f l-mghrib...').
   - Speak clearly and naturally like a knowledgeable Moroccan car expert.
   - DO NOT speak French.
   - DO NOT invent bizarre words, repeated tokens, or random numbers.
   - NEVER repeat words or phrases in a loop. Keep sentences crisp and meaningful.
2. ZERO EMOJIS: Never use any emojis or icons.
3. COFFRE ET VALISES : Dès que tu parles de la taille du coffre d'un véhicule (en Litres), donne TOUJOURS son équivalence en nombre de valises (ex: 'Coffre fih 440 L, yhez lik 3 tal 4 d les valises').
4. DOMAIN EXPERTISE: Answer the user's specific automotive question directly with full technical clarity based on the CONTEXT.
{rec_rule_darija_lat}
5. STRICT ONE QUESTION AT A TIME (Soul wahed b rasso) : Pose STRICTEMENT UNE SEULE QUESTION À LA FOIS pour découvrir les besoins du client (d'abord le budget, puis l'usage, etc.). N'écris JAMAIS de liste de questions ni de questionnaire.

--- CONTEXT ---
{context}
---------------
"""

    if detected_lang == "darija_ar":
        return f"""أنت الخبير والمستشار الآلي لمنصة وكالة (Wakala) المتخصصة في سوق وصناعة السيارات بالمغرب.

قواعد صارمة:
1. قاعدة اللغة: أجب بنسبة 100% بالدارجة المغربية المكتوبة بالحرف العربي بشكل واضح واحترافي ودقيق.
2. بدون إيموجي: ممنوع استخدام أي رمز تعبيري (Emoji) نهائياً.
3. سعة الصندوق وحقائب السفر: كلما ذكرت سعة أو حجم صندوق السيارة (باللتر)، اذكر دائماً المعادل العملي بعدد حقائب السفر (مثال: 'صندوق بسعة 440 لتر، يهز ليك من 3 حتى 4 ديال الفاليزات').
4. خبرة شاملة: أجب بدقة وعمق عن أي سؤال يخص قطاع السيارات اعتماداً على المعلومات في السياق.
{rec_rule_darija_ar}
5. سؤال واحد فقط في كل مرة: اطرح دائماً سؤالاً واحداً فقط محدداً وبسيطاً (الميزانية أولاً، ثم طبيعة الاستعمال، ثم الوقود). ممنوع طرح قائمة أسئلة متعددة في نفس الرسالة.

--- سياق المعلومات ---
{context}
----------------------
"""

    if detected_lang == "arabic":
        return f"""أنت الخبير والمستشار الهندسي والتقني المعتمد لمنصة وكالة (Wakala) لقطاع وسوق السيارات.

قواعد صارمة:
1. قاعدة اللغة: يجب أن تجيب بنسبة 100% باللغة العربية الفصحى السليمة والواضحة والمهنية.
2. بدون إيموجي: لا تستخدم أي رموز تعبيرية (Emojis) إطلاقاً.
3. سعة الصندوق وحقائب السفر: عند الحديث عن حجم أو سعة الصندوق (باللتر)، اذكر دائماً المعادل العملي بعدد حقائب السفر (مثال: 'صندوق بسعة 450 لتر، يتسع لحوالي 3 إلى 4 حقائب سفر').
4. موسوعية قطاع السيارات: أجب بمعلومات تقنية واقتصادية دقيقة ومفصلة حول أي موضوع في عالم السيارات بناءً على السياق.
{rec_rule_ar}
5. سؤال تشخيصي واحد فقط: اطرح دائماً سؤالاً واحداً فقط في كل رسالة (الميزانية أولاً، ثم طبيعة التنقل، ثم نوع الوقود). تجنب تماماً طرح قوائم أسئلة متعددة دفعة واحدة.

--- سياق المعلومات ---
{context}
----------------------
"""

    return f"""You are the world-class automotive consultant and engineering expert for the Wakala automotive intelligence platform.

MANDATORY RULES:
1. LANGUAGE RULE: You MUST respond 100% in {target_lang_name}.
   - Maintain total linguistic purity and fluency in {target_lang_name}. Do NOT mix other languages.
2. ZERO EMOJIS: Do NOT use any emojis, icons, or graphical symbols under any circumstances.
3. COFFRE ET VALISES : Dès que tu mentionnes la taille ou le volume du coffre d'un véhicule (en Litres), indique TOUJOURS AUSSI son équivalence concrète en nombre de valises (ex: 'Coffre de 440 L, soit environ 3 à 4 valises' ou 'Grand coffre de 560 L pouvant accueillir 4 à 5 grandes valises de voyage').
4. AUTOMOTIVE SECTOR AUTHORITY:
   - Provide highly accurate, authoritative, technical, and practical insights on ANY question concerning the automotive sector globally and in Morocco based on the CONTEXT below.
5. STRUCTURE: Use well-formatted bullet points, numbered lists, and bold titles for clarity.
{rec_rule_gen}
6. STRICT ONE QUESTION AT A TIME: Always ask STRICTLY ONE diagnostic question at a time to discover the client's preferences (e.g. start with target budget in MAD, then usage, then fuel/transmission). Never present bulleted multi-question lists.

--- CONTEXT ---
{context}
---------------
"""


def sanitize_input(text: str) -> str:
    """Nettoie le texte utilisateur pour éviter les injections basiques."""
    text = text[:800]
    return re.sub(r'[\x00-\x1F\x7F]', '', text)


def redact_pii(text: str) -> str:
    """Masque les emails et les numéros de téléphone."""
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_MASKED]', text)
    text = re.sub(r'(?:\+212|0)[ \-]?\d{1}[ \-]?\d{2}[ \-]?\d{2}[ \-]?\d{2}[ \-]?\d{2}', '[PHONE_MASKED]', text)
    return text


def normalize_multilingual_query_terms(query: str) -> str:
    """Traduit et normalise les termes Darija, Arabe et Anglais vers les termes standards du catalogue."""
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
        "مستعملة": "neuf",  # PIVOT: redirected from occasion → neuf
        "مستعمل": "neuf",  # PIVOT: redirected from occasion → neuf
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
        "used car": "neuf",   # PIVOT: redirected from occasion → neuf
        "used cars": "neuf",  # PIVOT: redirected from occasion → neuf
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


# ═══════════════════════════════════════════════════════════════
# CLASSIFICATEUR D'INTENTION RAPIDE MULTILINGUE
# ═══════════════════════════════════════════════════════════════

def fast_classify_intent(message: str) -> Optional[Dict[str, Any]]:
    """Classifie instantanément l'intention avec priorité rigoureuse."""
    msg = message.lower().strip()

    # 1. Questions d'Expert / Fiabilité / Pannes / Moteurs (Priorité ABSOLUE pour pannes/défauts)
    expert_kw = [
        # Français (uniquement termes de problèmes, pannes, fiabilité mécanique)
        'problème', 'probleme', 'problèmes', 'problemes', 'panne', 'pannes', 'bruit bizarre',
        'fiabilité', 'fiabilite', 'avis sur', 'défaut', 'defauts', 'casse moteur', 'surconsommation',
        'courroie distribution', 'puretech', 'tce', 'adblue', '1.2 puretech', '1.2 tce', '1.6 thp',
        'rappel constructeur', 'secteur auto', 'industrie automobile', 'marche automobile',
        # Darija
        'machakil', 'mashakil', 'lmachakil', 'moshkil', 'moshkila', 'mouchkil', 'mouchkila',
        'sout ghrib', 'vibration', '3oyob', '3ouyoub', 'katkonsomi zit',
        'katkhser', 'katkhesser', 'doukhan', 'khatar', 'nasiha f moteur',
        # Anglais
        'problem', 'problems', 'issue', 'issues', 'defect', 'defects', 'reliability', 'reliable',
        'review of', 'overheating', 'smoke', 'warning light', 'engine failure', 'timing belt issue',
        'automotive industry', 'sector data',
        # Espagnol
        'problema', 'problemas', 'avería', 'fallo', 'fiabilidad', 'industria automotriz',
        # Allemand
        'problem', 'probleme', 'zuverlässigkeit', 'panne',
        # Italien
        'problema', 'problemi', 'guasto', 'affidabilità',
        # Arabe
        'مشكل', 'مشاكل', 'مشكلة', 'عيوب', 'عطب', 'اعطال', 'دخان',
        'اعتمادية', 'قطاع السيارات', 'صناعة السيارات'
    ]
    if any(kw in msg for kw in expert_kw):
        return {"intent": "auto_expert", "max_price": None, "search_query": None}

    # 2. Dédouanement / Douane / Customs
    customs_kw = [
        'douane', 'dédouanement', 'dedouanement', 'diwana', 'dywana',
        'import', 'importation', 'taxe douane', 'frais douane', 'taman diwana',
        'customs', 'customs duty', 'import tax', 'clearance fees',
        'aduanas', 'arancel', 'zoll', 'dogana', 'alfândega', 'gümrük', 'таможня',
        'ديوانة', 'جمارك', 'الجمارك', 'تعشير', 'استيراد'
    ]
    if any(kw in msg for kw in customs_kw):
        return {"intent": "customs", "max_price": None, "search_query": None}

    # 3. Entretien / Vidange / Carnet / Maintenance
    maint_kw = [
        'entretien', 'vidange', 'maintenance', 'révision', 'revision',
        'carnet', 'pneu', 'pneus', 'rappel entretien', 'khassni vidange', 'zite',
        'oil change', 'service book', 'tires', 'inspection', 'car maintenance',
        'mantenimiento', 'cambio de aceite', 'wartung', 'ölwechsel', 'manutenzione',
        'فحص', 'صيانة', 'تغيير الزيت', 'عجلات', 'إطارات'
    ]
    if any(kw in msg for kw in maint_kw):
        return {"intent": "maintenance_check", "max_price": None, "search_query": None}

    # 4. Salutations courtes EXCLUSIVES (exact match ou début de salutation sans question technique)
    greetings = [
        'bonjour', 'salut', 'bonsoir', 'hello', 'hi', 'hey', 'good morning', 'good afternoon',
        'salam', 'slm', 'salamo alaykom', 'salamou alaykoum', 'salam alaykom',
        'labas', 'kidayr', 'ki dayr', 'kidayra', 'cv', 'ca va', 'ça va',
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
        # Si c'est une salutation courte (< 30 caractères sans autre question)
        if len(msg) < 35:
            return {"intent": "greeting", "max_price": None, "search_query": None}

    # 5. Recherche explicite de voiture (Multilingue)
    search_triggers = [
        'bghit', 'baghi', 'kanqleb', 'kan9leb', 'kayna chi', 'kayn chi',
        '3ndkom chi', '3andkom', 'cherche', 'recherche', 'trouver',
        'je veux acheter', 'acheter', 'voiture pour', 'budget de',
        'tomobila', 'sayara', 'neuf', 'dacia', 'renault',  # PIVOT: removed 'occasion'
        'peugeot', 'clio', 'golf', 'volkswagen', 'hyundai', 'kia', 'mercedes', 'bmw',
        'looking for', 'search', 'want to buy', 'i want', 'i need', 'find me',
        'show me', 'cheap car', 'diesel car', 'new car', 'price of',  # PIVOT: removed 'used car'
        'comprar', 'coche', 'auto', 'kaufen', 'comprare',
        'سيارة', 'سيارات', 'شراء', 'أبحث', 'أريد', 'بدي', 'طوموبيل'
    ]
    
    max_price = None
    k_match = re.search(r'(?:under|below|moins de|max|budget(?: de)?|أقل من|ميزانية)?\s*(\d+)\s*(?:k|000)\s*(?:mad|dh|dirham|درهم|usd|eur)?', msg)
    if k_match:
        val = int(k_match.group(1))
        max_price = val * 1000 if val < 1000 else val
    
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

    # 6. Conseil automobile général par défaut (instantané sans appel LLM intermédiaire)
    clean_q = normalize_multilingual_query_terms(message)
    return {"intent": "general_advice", "max_price": max_price, "search_query": clean_q}


async def analyze_intent(user_message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """Analyse instantanément l'intention de l'utilisateur (100% Python déterministe < 0.1ms)."""
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


async def retrieve_vehicles(query: str, max_price: Optional[float] = None, top_k: int = 6) -> str:
    """Interroge Qdrant pour récupérer les véhicules réels du catalogue sans duplication (avec timeout 2.5s)."""
    qdrant = get_qdrant_client()
    clean_query = normalize_multilingual_query_terms(query)
    
    try:
        query_vector = await asyncio.wait_for(embeddings_model.aembed_query(clean_query), timeout=2.5)
    except Exception as e:
        print(f"[Qdrant Embed Fast Fallback] {e}")
        return "Catalogue de véhicules neufs disponibles sur la plateforme Wakala."
    
    filter_conditions = []
    if max_price is not None:
        filter_conditions.append(
            qmodels.FieldCondition(
                key="price",
                range=qmodels.Range(lte=float(max_price))
            )
        )
    
    query_filter = qmodels.Filter(must=filter_conditions) if filter_conditions else None
    
    try:
        search_result = await qdrant.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
    except Exception:
        return "Aucun véhicule correspondant dans la base de données actuelle."

    if not search_result:
        return "Aucun véhicule correspondant dans la base de données actuelle."

    seen_signatures = set()
    context_str = ""
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
        
        context_str += f"- ID: {hit.id} | {brand} {model} ({year}) | Prix: {price} MAD | Ville: {city} | Carburant: {fuel}\n"
    
    return context_str if context_str else "Aucun véhicule correspondant dans la base de données actuelle."


# ─── Salutations immédiates multilingues ───────────────────────
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


# ─── Connaissances riches sectorielles d'expertise automobile ──
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
Koun moustachar teqni kbir d Wakala : hder m3ah b tariqa tabi3iya, zwiyna w mfhoma.
Matkounch robot w matktech 3lih b les questions mserfin.
Ila mazal ma3tach l-ma3loumat, sewlo soual wahed bohdo f kol risala (chmen naw3 d l-tomobila baghi, wla chhal l-budget li f balo, wla l-isti3mal dyalo).
Mat3tich liste d les questions w mat3tich des modeles 3chwa2iyen qbel matfhem l-ihtiyaj dyalo.""",

    "darija_ar": """الزبون مهتم بالبحث عن سيارة أو استشارة حول الشراء لكنه لم يحدد كل تفاصيله بعد.
تحدث معه بأسلوب استشاري ذكي وعفوي كخبير سيارات محترف.
تجنب الأسلوب الآلي أو طرح استمارة أسئلة جافة دفعة واحدة.
اطرح سؤالاً واحداً فقط بلباقة لمساعدته على توضيح رغبته (مثلاً: نوع السيارة المفضل لديه، أو الميزانية التقريبية، أو طبيعة تنقله اليومي).
لا ترشح سيارات عشوائية قبل فهم احتياجه بدقة.""",

    "arabic": """العميل يرغب في استشارة حول شراء سيارة ولكن لم يحدد بعد كل معاييره.
تحدث بأسلوب استشاري مهني ومرن، كخبير سيارات متخصص.
تجنب تماماً طرح استمارات أو قوائم أسئلة ميكانيكية متتالية.
اطرح سؤالاً واحداً فقط في كل رسالة لمساعدته بلباقة (مثل فئة السيارة التي يفضلها، أو ميزانيته المستهدفة، أو طبيعة تنقلاته اليومية).
لا تقدم ترشيحات عشوائية قبل وضوح المعايير.""",

    "french": """Le client souhaite trouver un véhicule mais n'a pas encore défini l'ensemble de ses critères.
Adopte une posture d'expert consultant automobile, chaleureuse et naturelle.
Ne sois pas rigide et ne pose aucun questionnaire à puces.
Pose UNE SEULE question simple et ouverte à la fois pour comprendre son projet (par exemple le style de véhicule souhaité, son usage principal ou son budget approximatif).
Ne propose aucun véhicule au hasard avant d'avoir cerné ses attentes.""",

    "english": """The user is exploring buying a car but has not yet specified all their preferences.
Act as an empathetic and highly knowledgeable automotive consultant.
Do not act like a rigid bot or generate bulleted questionnaires.
Ask strictly ONE open and friendly question at a time to understand their needs (e.g. preferred vehicle style, daily driving habits, or target budget).
Do not output random vehicle recommendations before understanding their requirements."""
}


async def chat_stream(message: str, history: List[Dict[str, str]]) -> AsyncIterable[str]:
    """Gère la logique complète du chat et génère la réponse 100% dans la langue du client sur tout le secteur automobile, garantie sans emojis."""
    clean_message = redact_pii(sanitize_input(message))
    
    # 1. Détection universelle de la langue avec mémoire de contexte
    detected_lang = detect_language(clean_message, history=history)
    
    # 2. Analyse d'intention ultra-rapide
    intent_data = await analyze_intent(clean_message, history)
    intent = intent_data.get("intent", "general_advice")
    max_price = intent_data.get("max_price")
    search_query = intent_data.get("search_query") or clean_message
    
    # 3. Gestion instantanée des salutations simples (0 latence, 100% langue cible, 0 emoji)
    if intent == "greeting":
        greeting_text = GREETING_RESPONSES.get(detected_lang, GREETING_RESPONSES["french"])
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
    
    # 6. Stream de génération avec filtrage systématique d'emojis et des balises de réflexion (<think>)
    in_think_block = False
    
    if settings.OPENROUTER_API_KEY:
        stream_source = _stream_openrouter_direct(raw_messages)
    else:
        # Fallback local Ollama
        messages = [
            SystemMessage(content=m["content"]) if m["role"] == "system"
            else HumanMessage(content=m["content"]) if m["role"] == "user"
            else AIMessage(content=m["content"])
            for m in raw_messages
        ]
        active_llm = get_llm()
        async def _adapt_langchain():
            async for chunk in active_llm.astream(messages):
                yield getattr(chunk, "content", "")
        stream_source = _adapt_langchain()

    thinking_buffer = ""
    
    async for content in stream_source:
        if not content:
            continue
        
        if "<think>" in content or "Here's a thinking process:" in content:
            in_think_block = True
            
        if in_think_block:
            thinking_buffer += content
            if "</think>" in thinking_buffer:
                in_think_block = False
                content = thinking_buffer.split("</think>", 1)[1]
                thinking_buffer = ""
            elif "\n\n**" in thinking_buffer or "\n\n###" in thinking_buffer or "\n\n- " in thinking_buffer:
                in_think_block = False
                parts = re.split(r'\n\n(?=[\*\#\-])', thinking_buffer)
                content = "\n\n" + "\n\n".join(parts[1:])
                thinking_buffer = ""
            else:
                continue
                
        if content:
            clean_chunk = remove_emojis(content)
            if clean_chunk:
                yield clean_chunk

    if thinking_buffer:
        clean_rem = remove_emojis(thinking_buffer)
        if clean_rem:
            yield clean_rem

