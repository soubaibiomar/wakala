import type { Car } from './recommendationClient';
import { resolveVehicleImage } from '../../utils/vehicleImageResolver';
import { EightDimensionScores } from './EightDimensionScores';

interface CarResultsPanelProps { cars: Car[]; immersive?: boolean; language?: 'fr' | 'darija' | 'ar' | 'en' | null; }

export function CarResultsPanel({ cars, immersive = false, language = 'fr' }: CarResultsPanelProps) {
  const labels = {
    fr: { aria: 'Véhicules recommandés', eyebrow: 'SÉLECTION WAKALA', title: 'Des voitures qui vous ressemblent', match: 'match', matches: 'matchs', version: 'Version officielle', empty: 'Aucun véhicule ne correspond encore. Essayons un autre critère.' },
    darija: { aria: 'الطوموبيلات المقترحة', eyebrow: 'اختيار وكالة', title: 'طوموبيلات اللي كيناسبوك', match: 'اختيار', matches: 'اختيارات', version: 'النسخة الرسمية', empty: 'مازال ما لقات حتى طوموبيل مناسبة. جرب معيار آخر.' },
    ar: { aria: 'السيارات المقترحة', eyebrow: 'اختيار وكالة', title: 'سيارات تناسب احتياجاتك', match: 'مطابقة', matches: 'مطابقات', version: 'النسخة الرسمية', empty: 'لم نجد سيارة مناسبة بعد. جرّب معياراً آخر.' },
    en: { aria: 'Recommended vehicles', eyebrow: 'WAKALA SELECTION', title: 'Cars that suit you', match: 'match', matches: 'matches', version: 'Official version', empty: 'No suitable vehicle yet. Let’s try another criterion.' },
  }[language || 'fr'];
  return (
    <section className={`recommendation-experience__results ${immersive ? 'recommendation-experience__results--immersive' : ''}`} aria-label={labels.aria} dir={language === 'ar' || language === 'darija' ? 'rtl' : 'ltr'}>
      <div className="recommendation-experience__results-heading">
        <div><span className="recommendation-experience__eyebrow">{labels.eyebrow}</span><h2>{labels.title}</h2></div>
        <strong className="recommendation-experience__counter">{cars.length} <span>{cars.length > 1 ? labels.matches : labels.match}</span></strong>
      </div>
      <div className="recommendation-experience__grid">
        {cars.map((car) => (
          <article className="recommendation-experience__car" key={car.id}>
            <div className="recommendation-experience__car-image">
              <img
                src={resolveVehicleImage(car.brand, car.model, car.images)}
                alt={`${car.brand} ${car.model}`}
                onError={(event) => {
                  event.currentTarget.onerror = null;
                  event.currentTarget.src = '/assets/car-side-fallback.svg';
                }}
              />
              {car.match_score !== undefined && <span>{Math.round(car.match_score)}% match</span>}
            </div>
            <div className="recommendation-experience__car-body"><span>{car.brand}</span><h3>{car.model}</h3><p>{car.version || labels.version} · {car.city}</p><strong>{car.price.toLocaleString(language === 'en' ? 'en-US' : 'fr-FR')} MAD</strong><EightDimensionScores scores={car.eight_dimension_scores} total={car.total_8d_score} language={language} /></div>
          </article>
        ))}
      </div>
      {cars.length === 0 && <p className="recommendation-experience__empty">{labels.empty}</p>}
    </section>
  );
}
