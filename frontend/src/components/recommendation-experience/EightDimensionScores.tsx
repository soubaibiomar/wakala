import type { EightDimensionScores as ScoreMap } from '../../services/recommendationService';
import './eight-dimension-scores.css';

const DIMENSION_KEYS = ['espace', 'securite', 'cout_reel', 'prix_acces', 'praticite_urbaine', 'performance', 'ecologie', 'motricite'] as const;
const DIMENSIONS: Record<'fr' | 'darija' | 'ar' | 'en', string[]> = {
  fr: ['Espace', 'Sécurité', 'Coût réel', "Prix d'accès", 'Praticité urbaine', 'Performance', 'Écologie', 'Motricité'],
  darija: ['البلاصة', 'السلامة', 'المصاريف الحقيقية', 'ثمن الدخول', 'العملية فالمدينة', 'الأداء', 'البيئة', 'الجر'],
  ar: ['المساحة', 'السلامة', 'التكلفة الحقيقية', 'سعر الشراء', 'العملية داخل المدينة', 'الأداء', 'البيئة', 'الدفع'],
  en: ['Space', 'Safety', 'Running cost', 'Entry price', 'City practicality', 'Performance', 'Eco', 'Traction'],
};

interface EightDimensionScoresProps {
  scores?: ScoreMap;
  total?: number;
  language?: 'fr' | 'darija' | 'ar' | 'en' | null;
}

export function EightDimensionScores({ scores, total, language = 'fr' }: EightDimensionScoresProps) {
  if (!scores || typeof total !== 'number') return null;
  const activeLanguage = language || 'fr';
  const labels = DIMENSIONS[activeLanguage];
  const aria = { fr: 'Scores Wakala des 8 dimensions', darija: 'نقط وكالة فـ 8 ديال المعايير', ar: 'درجات وكالة للأبعاد الثمانية', en: 'Wakala scores across 8 dimensions' }[activeLanguage];
  const title = { fr: 'Scores 8D', darija: 'نقط 8D', ar: 'درجات 8D', en: '8D scores' }[activeLanguage];
  
  return (
    <div className="eight-dimension-scores" aria-label={aria} dir={activeLanguage === 'ar' || activeLanguage === 'darija' ? 'rtl' : 'ltr'}>
      <div className="eight-dimension-scores__header">
        <span>{title}</span>
        <strong>{total.toFixed(1)} / 5</strong>
      </div>
      <div className="eight-dimension-scores__grid">
        {DIMENSION_KEYS.map((key, index) => (
          <div className="eight-dimension-scores__item" key={key}>
            <span>{labels[index]}</span>
            <strong>{Number(scores[key] ?? 0).toFixed(1)} / 5</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
