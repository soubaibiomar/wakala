import React from 'react';
import type { Vehicle } from '../../types/vehicle';
import type { ModelDetail, TrimDetail } from '../../services/newCatalogService';

export interface VehicleStructuredDataProps {
  vehicle?: Vehicle;
  model?: ModelDetail;
  trim?: TrimDetail;
  currency?: string;
  url?: string;
  image?: string;
}

export const VehicleStructuredData: React.FC<VehicleStructuredDataProps> = ({
  vehicle,
  model,
  trim,
  currency = 'MAD',
  url,
  image,
}) => {
  // Construire un schéma JSON-LD propre et conforme sans champs factices
  let schemaData: Record<string, any> | null = null;

  if (model) {
    const activeTrim = trim || model.trims?.[0];
    const price = activeTrim?.promo_price_mad || activeTrim?.price_new_mad || model.starting_price_mad || 0;
    const brandName = model.brand?.name || 'Constructeur';
    const vehicleName = `${brandName} ${model.name}${activeTrim?.name ? ' ' + activeTrim.name : ''}`.trim();
    const resolvedImage = image || activeTrim?.image_url || model.hero_image_url || 'https://wakala.ma/og-image.jpg';
    const resolvedUrl = url || `https://wakala.ma/neuf/${model.slug}`;

    const pt = activeTrim?.powertrain;

    schemaData = {
      '@context': 'https://schema.org',
      '@type': ['Car', 'Product'],
      name: vehicleName,
      image: resolvedImage,
      description: `Découvrez la nouvelle ${brandName} ${model.name} au Maroc. Fiche technique officielle, motorisation, prix clé en main en MAD et réservation d'essai.`,
      brand: {
        '@type': 'Brand',
        name: brandName,
        logo: model.brand?.logo_url || undefined,
      },
      model: model.name,
      vehicleConfiguration: activeTrim?.name || undefined,
      bodyType: model.body_type || undefined,
      fuelType: pt?.fuel_type || undefined,
      vehicleTransmission: pt?.transmission || undefined,
      vehicleEngine: pt?.name ? {
        '@type': 'EngineSpecification',
        name: pt.name,
        enginePower: pt.engine_power_hp ? {
          '@type': 'QuantitativeValue',
          value: pt.engine_power_hp,
          unitText: 'HP',
        } : undefined,
      } : undefined,
      offers: {
        '@type': 'Offer',
        priceCurrency: currency,
        price: price,
        itemCondition: 'https://schema.org/NewCondition',
        availability: 'https://schema.org/InStock',
        url: resolvedUrl,
        seller: {
          '@type': 'AutoDealer',
          name: 'Wakala Maroc — Réseau Concessionnaires Agréés',
          areaServed: 'Maroc',
        },
      },
    };
  } else if (vehicle) {
    const brandName = vehicle.brand || 'Constructeur';
    const vehicleName = `${brandName} ${vehicle.model} (${vehicle.year})`;
    const resolvedImage = image || vehicle.images?.[0] || 'https://wakala.ma/og-image.jpg';
    const resolvedUrl = url || `https://wakala.ma/vehicule/${vehicle.id}`;

    schemaData = {
      '@context': 'https://schema.org',
      '@type': ['Car', 'Product'],
      name: vehicleName,
      image: resolvedImage,
      description: vehicle.description || `Véhicule neuf ${brandName} ${vehicle.model} au Maroc. Prix clé en main : ${vehicle.price} MAD.`,
      brand: {
        '@type': 'Brand',
        name: brandName,
      },
      model: vehicle.model,
      vehicleModelDate: vehicle.year ? String(vehicle.year) : undefined,
      bodyType: vehicle.body_type || undefined,
      fuelType: vehicle.fuel_type || undefined,
      vehicleTransmission: vehicle.transmission || undefined,
      color: vehicle.color || undefined,
      offers: {
        '@type': 'Offer',
        priceCurrency: currency,
        price: vehicle.price,
        itemCondition: 'https://schema.org/NewCondition',
        availability: 'https://schema.org/InStock',
        url: resolvedUrl,
        seller: {
          '@type': 'AutoDealer',
          name: vehicle.seller?.name || 'Concessionnaire Partenaire Wakala',
          areaServed: vehicle.city || 'Maroc',
        },
      },
    };
  }

  if (!schemaData) return null;

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData).replace(/</g, '\\u003c') }}
    />
  );
};

export default VehicleStructuredData;
