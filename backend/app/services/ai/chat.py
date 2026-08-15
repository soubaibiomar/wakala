import re
import json
import asyncio
from typing import AsyncIterable, List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import models as qmodels

from app.core.config import settings
from app.services.ai.qdrant import get_qdrant_client

# Define the models
api_key = settings.OPENAI_API_KEY or "ollama"
llm = ChatOpenAI(
    base_url=settings.OLLAMA_BASE_URL,
    model=settings.OLLAMA_MODEL_TEXT,
    api_key=api_key,
    temperature=0.2,
    max_tokens=2500,
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

ENGLISH_KEYWORDS = {
    'the', 'is', 'are', 'was', 'were', 'have', 'has', 'what', 'which', 'where', 'when',
    'who', 'why', 'how', 'can', 'could', 'should', 'would', 'car', 'cars', 'vehicle',
    'automotive', 'engine', 'transmission', 'gearbox', 'fuel', 'diesel', 'petrol', 'gasoline',
    'electric', 'hybrid', 'battery', 'price', 'cost', 'buy', 'used', 'new', 'mileage',
    'reliable', 'reliability', 'problem', 'problems', 'issue', 'issues', 'maintenance',
    'oil', 'change', 'service', 'brake', 'brakes', 'customs', 'duty', 'import', 'tax',
    'hello', 'hi', 'hey', 'good', 'morning', 'afternoon', 'evening', 'thank', 'thanks'
}

SPANISH_KEYWORDS = {
    'el', 'la', 'los', 'las', 'un', 'una', 'es', 'son', 'que', 'qué', 'como', 'cómo',
    'donde', 'dónde', 'cuando', 'cuándo', 'por', 'para', 'coche', 'coches', 'auto',
    'automóvil', 'vehículo', 'motor', 'gasolina', 'diésel', 'híbrido', 'eléctrico',
    'precio', 'comprar', 'usado', 'segunda', 'mano', 'nuevo', 'kilometraje', 'fiabilidad',
    'problema', 'problemas', 'mantenimiento', 'aceite', 'aduanas', 'arancel', 'hola', 'gracias'
}

GERMAN_KEYWORDS = {
    'der', 'die', 'das', 'und', 'ist', 'sind', 'wie', 'was', 'wo', 'warum', 'wann',
    'ein', 'eine', 'auto', 'autos', 'wagen', 'fahrzeug', 'motor', 'benzin', 'diesel',
    'hybrid', 'elektro', 'batterie', 'preis', 'kaufen', 'gebraucht', 'neu', 'kilometerstand',
    'zuverlässigkeit', 'problem', 'probleme', 'wartung', 'ölwechsel', 'zoll', 'hallo', 'danke'
}

ITALIAN_KEYWORDS = {
    'il', 'la', 'lo', 'i', 'gli', 'le', 'un', 'una', 'è', 'sono', 'che', 'cosa', 'come',
    'dove', 'quando', 'perché', 'auto', 'automobile', 'macchina', 'veicolo', 'motore',
    'benzina', 'diesel', 'ibrido', 'elettrico', 'prezzo', 'comprare', 'usata', 'usato',
    'nuovo', 'chilometraggio', 'affidabilità', 'problema', 'problemi', 'manutenzione',
    'olio', 'dogana', 'ciao', 'grazie'
}

PORTUGUESE_KEYWORDS = {
    'o', 'a', 'os', 'as', 'um', 'uma', 'é', 'são', 'que', 'qual', 'como', 'onde',
    'quando', 'por', 'carro', 'carros', 'veículo', 'automóvel', 'motor', 'gasolina',
    'diesel', 'híbrido', 'elétrico', 'preço', 'comprar', 'usado', 'novo', 'quilometragem',
    'confiabilidade', 'problema', 'problemas', 'manutenção', 'óleo', 'alfândega', 'olá', 'obrigado'
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


def detect_language(text: str) -> str:
    """Détecte avec précision la langue de la requête utilisateur."""
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

    # Russe
    if re.search(r'[\u0400-\u04FF]', text) or words.intersection(RUSSIAN_KEYWORDS):
        return "russian"

    # Chinois
    if re.search(r'[\u4e00-\u9fff]', text):
        return "chinese"

    # Japonais
    if re.search(r'[\u3040-\u30ff]', text):
        return "japanese"

    # Espagnol
    if len(words.intersection(SPANISH_KEYWORDS)) >= 2 or (len(words) <= 5 and len(words.intersection(SPANISH_KEYWORDS)) >= 1) or any(t.startswith(kw) for kw in ['hola', 'buenos días', 'buenas tardes', 'qué ', 'cómo ', 'cuánto ']):
        return "spanish"

    # Allemand
    if len(words.intersection(GERMAN_KEYWORDS)) >= 2 or (len(words) <= 5 and len(words.intersection(GERMAN_KEYWORDS)) >= 1) or any(t.startswith(kw) for kw in ['hallo', 'guten tag', 'guten morgen', 'wie ', 'was ']):
        return "german"

    # Italien
    if len(words.intersection(ITALIAN_KEYWORDS)) >= 2 or (len(words) <= 5 and len(words.intersection(ITALIAN_KEYWORDS)) >= 1) or any(t.startswith(kw) for kw in ['ciao', 'buongiorno', 'buonasera', 'come ', 'cosa ']):
        return "italian"

    # Portugais
    if len(words.intersection(PORTUGUESE_KEYWORDS)) >= 2 or (len(words) <= 5 and len(words.intersection(PORTUGUESE_KEYWORDS)) >= 1) or any(t.startswith(kw) for kw in ['olá', 'ola', 'bom dia', 'boa tarde', 'como ']):
        return "portuguese"

    # Turc
    if len(words.intersection(TURKISH_KEYWORDS)) >= 2 or (len(words) <= 5 and len(words.intersection(TURKISH_KEYWORDS)) >= 1) or any(t.startswith(kw) for kw in ['merhaba', 'selam', 'nasılsınız']):
        return "turkish"

    # Anglais
    if len(words.intersection(ENGLISH_KEYWORDS)) >= 2 or (len(words) <= 5 and len(words.intersection(ENGLISH_KEYWORDS)) >= 1) or any(t.startswith(kw) for kw in ['hello', 'hi ', 'hey ', 'how ', 'what ', 'where ', 'which ', 'i want', 'i need', 'looking for', 'tell me']):
        return "english"

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
    """Détermine si la demande de véhicule est suffisamment qualifiée pour recommander des modèles précis."""
    msg = message.lower()
    
    # 1. Budget spécifié
    if max_price is not None:
        return True
    if re.search(r'\b\d+\s*(?:k|000|mad|dh|dirham|درهم|mlyon|melyon|million|مليون|الف|ألف)\b', msg):
        return True

    # 2. Marque ou modèle précis
    if any(b in msg for b in KNOWN_BRANDS_MODELS):
        return True
        
    # 3. Combinaison de descripteurs clés (ex: suv diesel, citadine automatique, 7 places)
    descriptors = ['diesel', 'essence', 'hybride', 'hybrid', 'electrique', 'électrique', 'automatique', 'manuelle', 'suv', 'citadine', 'berline', '7 places', 'familiale', 'break', 'pick-up', 'pickup']
    matches = sum(1 for d in descriptors if d in msg)
    if matches >= 2:
        return True

    # 4. Réponses précédentes dans l'historique ayant qualifié la recherche
    if history and len(history) >= 2:
        prev_user_msgs = " ".join(m.get("content", "").lower() for m in history if m.get("role") == "user")
        if any(b in prev_user_msgs for b in KNOWN_BRANDS_MODELS) or re.search(r'\b\d+\s*(?:k|000|mad|dh|dirham|درهم|mlyon|million)\b', prev_user_msgs):
            return True

    return False


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
```""" if is_car_search else "4. CONSULTATIVE DISCOVERY: When the user is exploring buying a car without enough details, do NOT output fake JSON blocks or recommend random cars. Welcome them and ask the crucial qualification questions (Budget, City vs Highway usage, Fuel type Diesel/Essence/Hybrid, Manual vs Automatic transmission, Body style) to understand their exact preferences before recommending."

    rec_rule_darija_ar = "4. عند التوصية بسيارات من السياق أرفق كود JSON الخاص بكل سيارة." if is_car_search else "4. الاستشارة والاكتشاف قبل التوصية: عندما يرغب المستخدم في شراء سيارة دون تحديد معاييره، لا تصدر أي كتل JSON أو ترشيحات عشوائية. رحب به واطرح عليه الأسئلة التشخيصية اللازمة (الميزانية، نوع الاستعمال داخل المدينة أو السفر، الوقود ديزل/بنزين/هايبرد، أوتوماتيك/عادي) لفهم احتياجاته بدقة."

    rec_rule_ar = "4. عند التوصية بسيارات من السياق أرفق كود JSON الخاص بها." if is_car_search else "4. الاستشارة والتشخيص قبل التوصية: عند رغبة العميل في شراء سيارة دون معايير واضحة، لا تدرج أي كتل JSON أو اقتراحات عشوائية. رحب بمشروعه واطرح الأسئلة الاستشارية (الميزانية، طبيعة القيادة اليومية، نوع الوقود وناقل الحركة، فئة السيارة) لفهم متطلباته وتوجيهه لأفضل الخيارات."

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
```""" if is_car_search else f"5. CONSULTATIVE DIAGNOSIS: When a user inquires about buying or finding a car without specific parameters, do NOT output any JSON blocks or random vehicle picks. Warmly welcome their purchase project and ask the essential qualifying questions in {target_lang_name} (Budget in MAD, daily commute & city vs highway usage, fuel Diesel/Petrol/Hybrid & transmission Manual vs Automatic, and body style) to understand their exact needs before recommending."

    if detected_lang == "darija_lat":
        return f"""You are the expert automotive consultant for the Wakala platform in Morocco.

CRITICAL RULES:
1. LANGUAGE RULE: You MUST answer 100% in natural Moroccan Darija written in Latin script (e.g. 'Kaynin ba3d les modeles w les moteurs li ma3roufin b machakil f l-mghrib...').
   - Speak clearly and naturally like a knowledgeable Moroccan car expert.
   - DO NOT speak French.
   - DO NOT invent bizarre words, repeated tokens, or random numbers.
   - NEVER repeat words or phrases in a loop. Keep sentences crisp and meaningful.
2. ZERO EMOJIS: Never use any emojis or icons.
3. DOMAIN EXPERTISE: Answer the user's specific automotive question directly with full technical clarity based on the CONTEXT.
{rec_rule_darija_lat}
5. PROACTIVE ENGAGEMENT & CLEVER QUESTIONS: Conclude your answer by asking 1 or 2 concise, intelligent questions in natural Darija (e.g., 'Chhal l-budget li 3ndek ?' or 'Wach baghiha l-mdina wla triq twila ?') to discover the user's preferences and help guide them on Wakala.

--- CONTEXT ---
{context}
---------------
"""

    if detected_lang == "darija_ar":
        return f"""أنت الخبير والمستشار الآلي لمنصة وكالة (Wakala) المتخصصة في سوق وصناعة السيارات بالمغرب.

قواعد صارمة:
1. قاعدة اللغة: أجب بنسبة 100% بالدارجة المغربية المكتوبة بالحرف العربي بشكل واضح واحترافي ودقيق.
2. بدون إيموجي: ممنوع استخدام أي رمز تعبيري (Emoji) نهائياً.
3. خبرة شاملة: أجب بدقة وعمق عن أي سؤال يخص قطاع السيارات اعتماداً على المعلومات في السياق.
{rec_rule_darija_ar}
5. تفاعل ذكي واستبقاء المستخدم: اختم دائماً بسؤال أو سؤالين استشاريين أذكياء لاكتشاف تفضيلات واحتياجات العميل بدقة (مثل الميزانية، طبيعة التنقل اليومي، تفضيل أوتوماتيك أو عادي، أو المقارنة بين موديلات) لمساعدته في المنصة وإبقائه مهتماً.

--- سياق المعلومات ---
{context}
----------------------
"""

    if detected_lang == "arabic":
        return f"""أنت الخبير والمستشار الهندسي والتقني المعتمد لمنصة وكالة (Wakala) لقطاع وسوق السيارات.

قواعد صارمة:
1. قاعدة اللغة: يجب أن تجيب بنسبة 100% باللغة العربية الفصحى السليمة والواضحة والمهنية.
2. بدون إيموجي: لا تستخدم أي رموز تعبيرية (Emojis) إطلاقاً.
3. موسوعية قطاع السيارات: أجب بمعلومات تقنية واقتصادية دقيقة ومفصلة حول أي موضوع في عالم السيارات بناءً على السياق.
{rec_rule_ar}
5. التفاعل الاستشاري الذكي: اختم دائماً بطرح سؤال أو سؤالين تشخيصيين أذكياء ومحفزين حول تفضيلات العميل (مثل الميزانية المرصودة، طبيعة القيادة اليومية، المسافات المقطوعة، تفضيل ناقل الحركة أوتوماتيك أو يدوي، أو المقارنة بين سيارات معينة) لمساعدته في استكشاف أفضل الخيارات على منصة وكالة.

--- سياق المعلومات ---
{context}
----------------------
"""

    return f"""You are the world-class automotive consultant and engineering expert for the Wakala automotive intelligence platform.

MANDATORY RULES:
1. LANGUAGE RULE: You MUST respond 100% in {target_lang_name}.
   - Maintain total linguistic purity and fluency in {target_lang_name}. Do NOT mix other languages.
2. ZERO EMOJIS: Do NOT use any emojis, icons, or graphical symbols under any circumstances.
3. AUTOMOTIVE SECTOR AUTHORITY:
   - Provide highly accurate, authoritative, technical, and practical insights on ANY question concerning the automotive sector globally and in Morocco based on the CONTEXT below.
4. STRUCTURE: Use well-formatted bullet points, numbered lists, and bold titles for clarity.
{rec_rule_gen}
6. PROACTIVE CONSULTATIVE ENGAGEMENT: Always conclude your response with 1-2 clever, insightful, and diagnostic follow-up questions in {target_lang_name} to discover the client's specific preferences (e.g., precise budget, daily commute distance, city vs highway driving, preferred transmission or fuel efficiency, or models being compared) to keep them actively engaged on the Wakala platform.

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

    # 1. Questions d'Expert / Fiabilité / Pannes / Moteurs (Priorité ABSOLUE avant salutations et recherche)
    expert_kw = [
        # Français
        'problème', 'probleme', 'problèmes', 'problemes', 'panne', 'pannes', 'bruit',
        'fiabilité', 'fiabilite', 'avis sur', 'défaut', 'defauts', 'consommation',
        'moteur', 'courroie', 'embrayage', 'turbo', 'boite', 'clim', 'batterie', 'hybride',
        'electrique', 'électrique', 'puretech', 'tce', 'adblue', 'autonomie', 'secteur auto',
        'industrie automobile', 'usine', 'marche automobile',
        # Darija
        'machakil', 'mashakil', 'lmachakil', 'moshkil', 'moshkila', 'mouchkil', 'mouchkila',
        'sout', 'vibration', 'sah', 's7i7', 's7i7a', '3oyob', '3ouyoub', 'katkonsomi',
        'katkhser', 'katkhesser', 'doukhan', 'fren', 'khatar', 'nasiha',
        # Anglais
        'problem', 'problems', 'issue', 'issues', 'defect', 'defects', 'reliability', 'reliable',
        'review of', 'overheating', 'smoke', 'warning light', 'engine', 'gearbox', 'transmission',
        'electric vehicle', 'ev', 'battery', 'hybrid', 'range', 'automotive industry', 'sector',
        # Espagnol
        'problema', 'problemas', 'avería', 'fallo', 'fiabilidad', 'motor', 'batería',
        'consumo', 'coche eléctrico', 'industria automotriz',
        # Allemand
        'problem', 'probleme', 'zuverlässigkeit', 'motor', 'panne', 'batterie', 'verbrauch',
        # Italien
        'problema', 'problemi', 'guasto', 'affidabilità', 'motore', 'batteria', 'consumo',
        # Arabe
        'مشكل', 'مشاكل', 'مشكلة', 'عيوب', 'عطب', 'اعطال', 'صوت', 'اهتزاز', 'محرك', 'دخان',
        'اعتمادية', 'سيارات كهربائية', 'بطارية', 'قطاع السيارات', 'صناعة السيارات'
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

    if any(kw in msg for kw in search_triggers):
        clean_search = normalize_multilingual_query_terms(message)
        return {"intent": "car_search", "max_price": max_price, "search_query": clean_search}

    return None


async def analyze_intent(user_message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """Analyse l'intention de l'utilisateur avec classifieur rapide puis fallback LLM."""
    fast_result = fast_classify_intent(user_message)
    if fast_result:
        return fast_result

    system_prompt = """Tu es un analyseur d'intention automobile. Retourne UNIQUEMENT un JSON valide :
{
  "intent": "car_search" | "auto_expert" | "maintenance_check" | "general_advice" | "customs",
  "max_price": number | null,
  "search_query": string | null
}"""
    
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{message}")
    ])
    
    analyzer_llm = ChatOpenAI(
        base_url=settings.OLLAMA_BASE_URL,
        model="llama3.2:1b",
        api_key=api_key,
        temperature=0,
        max_tokens=120,
    ).bind(response_format={"type": "json_object"})
    
    try:
        chain = analysis_prompt | analyzer_llm
        response = await chain.ainvoke({"message": user_message})
        content = response.content.strip()
        
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1).strip()
            
        if '{' in content and '}' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            content = content[start:end]
            
        parsed = json.loads(content)
        if parsed.get("search_query"):
            parsed["search_query"] = normalize_multilingual_query_terms(parsed["search_query"])
        return parsed
    except Exception:
        clean_q = normalize_multilingual_query_terms(user_message)
        return {"intent": "car_search" if any(w in user_message.lower() for w in ["voiture", "car", "tomobil", "dacia", "clio", "golf", "prix", "price", "budget", "سيارة"]) else "general_advice", "max_price": None, "search_query": clean_q}


async def retrieve_vehicles(query: str, max_price: Optional[float] = None, top_k: int = 6) -> str:
    """Interroge Qdrant pour récupérer les véhicules réels du catalogue sans duplication."""
    qdrant = get_qdrant_client()
    clean_query = normalize_multilingual_query_terms(query)
    
    try:
        query_vector = await embeddings_model.aembed_query(clean_query)
    except Exception as e:
        print(f"[Qdrant Embed Error] {e}")
        return "Aucun véhicule trouvé (Service d'embeddings indisponible)."
    
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
        # PIVOT: mileage removed (new vehicles only)
        
        context_str += f"- ID: {hit.id} | {brand} {model} ({year}) | Prix: {price} MAD | Ville: {city} | Carburant: {fuel}\n"
    
    return context_str if context_str else "Aucun véhicule correspondant dans la base de données actuelle."


# ─── Salutations immédiates multilingues ───────────────────────
GREETING_RESPONSES = {
    "darija_lat": "Salam ! Merhba bik f Wakala, l-plateforme l-oula d l-automobile f l-mghrib. Kifach nqder n3awnek lyoum ? Wach 3ndek chi budget m7ded w baghi nqtarho 3lik ahsan l-ikhtiyarat, wla 3ndek soual teqni 3la chi modele ?",
    "darija_ar": "وعليكم السلام و مرحباً بك في منصة وكالة للسيارات بالمغرب. كيفاش نقدر نعاونك اليوم؟ واش عندك ميزانية محددة باغي نقترحو عليك أحسن الخيارات، ولا عندك استفسار تقني على شي موديل أو محرك؟",
    "arabic": "أهلاً ومرحباً بك في منصة وكالة الرائدة في قطاع واستشارات السيارات. كيف يمكنني مساعدتك اليوم؟ هل لديك ميزانية أو متطلبات محددة لنقترح عليك أفضل الخيارات، أم ترغب في استشارة فنية أو مقارنة بين موديلات معينة؟",
    "english": "Hello and welcome to Wakala, your premier automotive advisory platform. How can I best assist you today? Do you have a specific budget or driving profile so I can recommend the top matching vehicles, or do you need expert technical advice on specific models?",
    "french": "Bonjour et bienvenue sur Wakala, votre plateforme conseil automobile de référence. Comment puis-je vous guider aujourd'hui ? Avez-vous un budget ou un usage précis pour que je vous oriente vers les meilleures options, ou souhaitez-vous un conseil d'expert sur un modèle en particulier ?",
    "spanish": "¡Hola y bienvenido a Wakala! ¿Cómo puedo asesorarte hoy? ¿Tienes un presupuesto o perfil de uso definido para recomendarte las mejores opciones, o necesitas una consulta técnica sobre algún modelo?",
    "german": "Hallo und herzlich willkommen bei Wakala! Wie kann ich Sie heute bestmöglich beraten? Haben Sie ein bestimmtes Budget oder ein bevorzugtes Modell, oder benötigen Sie technische Kaufberatung?",
    "italian": "Ciao e benvenuto su Wakala! Come posso aiutarti oggi? Hai un budget o criteri specifici per trovare l'auto ideale, oppure desideri una consulenza tecnica su un modello?",
    "portuguese": "Olá e bem-vindo à Wakala! Como posso ajudar você hoje? Você tem um orçamento ou perfil de uso definido para encontrarmos as melhores opções, ou precisa de consultoria técnica?",
    "turkish": "Merhaba ve Wakala'ya hoş geldiniz! Size bugün nasıl yardımcı olabilirim? En uygun araçları önerebilmemiz için belirli bir bütçeniz veya kriterleriniz var mı, yoksa teknik bir danışmanlık mı istersiniz?",
    "russian": "Здравствуйте и добро пожаловать в Wakala! Чем я могу помочь вам сегодня? У вас есть определенный бюджет или критерии для подбора идеального авто, или вас интересует техническая консультация?"
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
    "darija_lat": """L-utilisateur baghi ychri tomobila walakin ma3tanach l-kriteriat dyalo (budget, type d'usage, carburant, boite).
Koun mustachar kbir d Wakala : r7eb bih f l-machrou3 dyalo d chira2, w sewlo as2ila wadiha w dkiya bach tefhem chno baghi bedebt :
1. Chhal l-budget max dyalo b dirham ?
2. Wach l-khedma w l-isti3mal f l-mdina wla triq twila w safar ?
3. Wach kayfeddel Diesel, Essence wla Hybride, w boite manuelle wla automatique ?
4. Wach baghi citadine sghira, berline, wla SUV familial ?
Mat3tich des modeles wla cartes JSON daba hta yjawbek 3la had l-as2ila bach n3tiwh ahsan ikhtiyar mnasb lih.""",

    "darija_ar": """المستخدم يرغب في شراء سيارة لكنه لم يحدد المعايير الأساسية (الميزانية، نوع الاستعمال، المحرك، ناقل الحركة).
تصرف كمستشار سيارات محترف لمنصة وكالة: رحب به في مشروعه واطرح عليه أسئلة تشخيصية ذكية وواضحة لفهم احتياجاته بدقة:
1. شحال الميزانية المحددة بالدرهم؟
2. واش الاستعمال اليومي غيكون داخل المدينة ولا في الطريق الطويلة والسفر؟
3. واش كيفضل ديزل، بنزين، أو هايبرد، وعلبة السرعة أوتوماتيك ولا عادية؟
4. فئة السيارة المناسبة: سيارة مدمجة للمدينة (citadine)، سيدان، أو SUV عائلية؟
لا تقدم بطاقات سيارات أو كتل JSON الآن حتى يجيب على هذه المعايير.""",

    "arabic": """العميل يرغب في شراء أو البحث عن سيارة ولكن لم يحدد بعد معاييره وميزانيته بدقة.
تصرف كمستشار مبيعات وخبير هندسي لمنصة وكالة: رحب بمشروع الشراء واطرح عليه الأسئلة التشخيصية الاستشارية الضرورية قبل تقديم التوصيات:
1. ما هي الميزانية التقريبية أو الحد الأقصى المرصود للشراء بالدرهم المغربي؟
2. ما هي طبيعة القيادة والاستخدام الأساسي (تنقلات يومية داخل المدينة، سفر ومسافات طويلة، أم سيارة عائلية)؟
3. ما هو نوع المحرك المفضل (ديزل، بنزين، هجين Hybrid، أم كهربائي) وتفضيل ناقل الحركة (يدوي أم أوتوماتيكي)؟
4. ما هي الفئة المفضلة للسيارة (سيارة مدمجة صغيرة، سيدان، أم كروس أوفر/SUV)؟
لا تقم بإدراج أي كتل JSON أو ترشيحات عشوائية حتى تتضح هذه المعايير لمساعدته في أفضل الخيارات.""",

    "french": """Le client souhaite acheter un véhicule mais n'a pas encore précisé ses critères clés (budget, usage, motorisation, boîte, silhouette).
Agis en expert conseil automobile de référence pour Wakala : accueille son projet avec professionnalisme et pose-lui les questions de cadrage indispensables avant toute recommandation :
1. Quel est votre budget maximal envisagé (en MAD / Dirhams) ?
2. Quel sera l'usage principal du véhicule (trajets urbains quotidiens, autoroute / longues distances, usage familial) ?
3. Avez-vous une préférence de motorisation (Diesel, Essence, Hybride, Électrique) et de boîte de vitesses (Manuelle ou Automatique) ?
4. Quel type de carrosserie correspond le mieux à vos besoins (Citadine compacte, Berline, SUV / Crossover) ?
Ne génère aucun bloc de recommandation JSON tant que ces préférences ne sont pas recueillies afin de lui garantir un conseil sur mesure.""",

    "english": """The user is interested in buying a car but has not yet defined their core search criteria (budget, usage profile, fuel type, transmission, vehicle type).
Act as a premier automotive advisor for Wakala: warmly welcome their purchase journey and ask the essential qualifying diagnostic questions before making specific vehicle recommendations:
1. What is your maximum target budget in MAD (Moroccan Dirhams)?
2. What will be your primary usage (daily city commuting, long highway drives, family trips)?
3. Do you have a preferred powertrain (Diesel, Petrol, Hybrid, Electric) and transmission (Manual vs Automatic)?
4. What vehicle body style do you prefer (Compact hatchback, Sedan, or SUV/Crossover)?
Do not output any JSON recommendation blocks until the user specifies their preferences so we can provide perfectly tailored matches."""
}


async def chat_stream(message: str, history: List[Dict[str, str]]) -> AsyncIterable[str]:
    """Gère la logique complète du chat et génère la réponse 100% dans la langue du client sur tout le secteur automobile, garantie sans emojis."""
    clean_message = redact_pii(sanitize_input(message))
    
    # 1. Détection universelle de la langue
    detected_lang = detect_language(clean_message)
    
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
    
    messages = [SystemMessage(content=system_prompt)]
    
    recent_history = history[-6:] if len(history) > 6 else history
    for msg in recent_history:
        clean_content = redact_pii(sanitize_input(msg.get("content", "")))
        clean_content = remove_emojis(clean_content)
        if msg.get("role") == "user":
            messages.append(HumanMessage(content=clean_content))
        elif msg.get("role") == "assistant":
            if len(clean_content) > 400:
                clean_content = clean_content[:400] + "..."
            messages.append(AIMessage(content=clean_content))
            
    messages.append(HumanMessage(content=remove_emojis(clean_message)))
    
    # 6. Stream de génération avec filtrage systématique d'emojis et des balises de réflexion (<think>)
    in_think_block = False
    async for chunk in llm.astream(messages):
        content = chunk.content
        if not content:
            continue
        
        if "<think>" in content:
            in_think_block = True
            parts = content.split("<think>", 1)
            before = parts[0]
            after = parts[1]
            if before:
                clean = remove_emojis(before)
                if clean:
                    yield clean
            content = after
            
        if in_think_block:
            if "</think>" in content:
                in_think_block = False
                parts = content.split("</think>", 1)
                content = parts[1]
            else:
                continue
                
        if content:
            clean_chunk = remove_emojis(content)
            if clean_chunk:
                yield clean_chunk
