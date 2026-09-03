import type { Car } from './recommendationClient';
import { resolveVehicleImage } from '../../utils/vehicleImageResolver';
import { EightDimensionScores } from './EightDimensionScores';

interface CarResultsPanelProps { cars: Car[]; immersive?: boolean; }

export function CarResultsPanel({ cars, immersive = false }: CarResultsPanelProps) {
  return (
    <section className={`recommendation-experience__results ${immersive ? 'recommendation-experience__results--immersive' : ''}`} aria-label="Véhicules recommandés">
      <div className="recommendation-experience__results-heading">
        <div><span className="recommendation-experience__eyebrow">SÉLECTION WAKALA</span><h2>Des voitures qui vous ressemblent</h2></div>
        <strong className="recommendation-experience__counter">{cars.length} <span>match{cars.length > 1 ? 's' : ''}</span></strong>
      </div>
      <div className="recommendation-experience__grid">
        {cars.map((car) => (
          <article className="recommendation-experience__car" key={car.id}>
            <div className="recommendation-experience__car-image">
              <img
                src={resolveVehicleImage(car.brand, car.model)}
                alt={`${car.brand} ${car.model}`}
                onError={(event) => {
                  event.currentTarget.onerror = null;
                  event.currentTarget.src = '/assets/car-side-fallback.svg';
                }}
              />
              {car.match_score !== undefined && <span>{Math.round(car.match_score)}% match</span>}
            </div>
            <div className="recommendation-experience__car-body"><span>{car.brand}</span><h3>{car.model}</h3><p>{car.version || 'Version officielle'} · {car.city}</p><strong>{car.price.toLocaleString('fr-FR')} MAD</strong><EightDimensionScores scores={car.eight_dimension_scores} total={car.total_8d_score} /></div>
          </article>
        ))}
      </div>
      {cars.length === 0 && <p className="recommendation-experience__empty">Aucun véhicule ne correspond encore. Essayons un autre critère.</p>}
    </section>
  );
}
