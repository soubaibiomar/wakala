import React from 'react';
import { ModelDetail, TrimDetail } from '../../services/newCatalogService';

interface VehicleJsonLdProps {
  model: ModelDetail;
  selectedTrim?: TrimDetail;
}

export const VehicleJsonLd: React.FC<VehicleJsonLdProps> = ({ model, selectedTrim }) => {
  const activeTrim = selectedTrim || model.trims?.[0];
  const price = activeTrim?.promo_price_mad || activeTrim?.price_new_mad || model.starting_price_mad || 0;
  const brandName = model.brand?.name || 'Wakala';

  const schemaData = {
    '@context': 'https://schema.org',
    '@type': 'Car',
    name: `${brandName} ${model.name} ${activeTrim?.name || ''}`.trim(),
    image: activeTrim?.image_url || model.hero_image_url || 'https://wakala.ma/og-image.jpg',
    description: `Découvrez la nouvelle ${brandName} ${model.name} au Maroc. Fiche technique, prix clé en main, vignette DGI et réservation d'essai immédiate.`,
    brand: {
      '@type': 'Brand',
      name: brandName,
      logo: model.brand?.logo_url || undefined,
    },
    model: model.name,
    vehicleConfiguration: activeTrim?.name,
    bodyType: model.body_type,
    fuelType: (activeTrim && 'powertrain' in activeTrim && activeTrim.powertrain?.fuel_type) || 'ESSENCE',
    vehicleTransmission: (activeTrim && 'powertrain' in activeTrim && activeTrim.powertrain?.transmission) || 'MANUELLE',
    vehicleEngine: {
      '@type': 'EngineSpecification',
      name: (activeTrim && 'powertrain' in activeTrim && activeTrim.powertrain?.name) || 'Moteur Standard',
      enginePower: {
        '@type': 'QuantitativeValue',
        value: (activeTrim && 'powertrain' in activeTrim && activeTrim.powertrain?.engine_power_hp) || undefined,
        unitText: 'HP',
      },
    },
    offers: {
      '@type': 'Offer',
      priceCurrency: 'MAD',
      price: price,
      itemCondition: 'https://schema.org/NewCondition',
      availability: 'https://schema.org/InStock',
      url: `https://wakala.ma/neuf/${model.slug}`,
      priceValidUntil: '2026-12-31',
      seller: {
        '@type': 'AutoDealer',
        name: 'Wakala Maroc — Réseau Concessionnaires Officiels',
        areaServed: 'Maroc',
      },
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData).replace(/</g, '\\u003c') }}
    />
  );
};
