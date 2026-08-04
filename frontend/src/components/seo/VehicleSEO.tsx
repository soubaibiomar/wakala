import React from 'react';
import { Helmet } from 'react-helmet-async';
import type { Vehicle } from '../../types/vehicle';

interface VehicleSEOProps {
  vehicle: Vehicle;
  currency?: string;
  image?: string;
}

export default function VehicleSEO({ vehicle, currency = "MAD", image }: VehicleSEOProps) {
  // Construire l'objet JSON-LD Schema.org
  const schemaData = {
    "@context": "https://schema.org",
    "@type": ["Vehicle", "Product"], // Product permet d'utiliser 'offers' proprement
    "name": `${vehicle.brand} ${vehicle.model} - ${vehicle.year}`,
    "brand": {
      "@type": "Brand",
      "name": vehicle.brand
    },
    "model": vehicle.model,
    "vehicleModelDate": vehicle.year.toString(),
    "mileageFromOdometer": {
      "@type": "QuantitativeValue",
      "value": vehicle.mileage,
      "unitCode": "KMT" // Kilometers
    },
    "fuelType": vehicle.fuel_type,
    "vehicleTransmission": vehicle.transmission,
    "bodyType": vehicle.body_type,
    "description": vehicle.description || `Achetez ce véhicule d'occasion ${vehicle.brand} ${vehicle.model} de l'année ${vehicle.year} au prix de ${vehicle.price} ${currency}.`,
    "image": image || `https://via.placeholder.com/800x600?text=${vehicle.brand}+${vehicle.model}`,
    "offers": {
      "@type": "Offer",
      "priceCurrency": currency,
      "price": vehicle.price,
      "itemCondition": "https://schema.org/UsedCondition",
      "availability": "https://schema.org/InStock",
      "seller": {
        "@type": vehicle.seller?.role === 'seller' ? "Organization" : "Person",
        "name": vehicle.seller?.name || "Vendeur Wakala"
      }
    }
  };

  const pageTitle = `${vehicle.brand} ${vehicle.model} ${vehicle.year} - ${vehicle.price.toLocaleString('fr-FR')} ${currency} | Wakala`;
  const pageDescription = `Achetez ce véhicule d'occasion ${vehicle.brand} ${vehicle.model} de l'année ${vehicle.year} au prix de ${vehicle.price} ${currency}. ${vehicle.city ? 'À ' + vehicle.city + '.' : ''}`;

  const citySlug = (vehicle.city || "maroc").toLowerCase().replace(/ /g, "-");
  const brandSlug = (vehicle.brand || "marque").toLowerCase().replace(/ /g, "-");
  const modelSlug = (vehicle.model || "modele").toLowerCase().replace(/ /g, "-");
  const slug = `${brandSlug}-${modelSlug}-${vehicle.year}-${vehicle.price}dh`;
  const canonicalUrl = `https://wakala.ma/voitures-occasion/${citySlug}/${slug}`;

  return (
    <Helmet>
      <title>{pageTitle}</title>
      <meta name="description" content={pageDescription} />
      <link rel="canonical" href={canonicalUrl} />
      <script type="application/ld+json">
        {JSON.stringify(schemaData).replace(/</g, '\\u003c')}
      </script>
    </Helmet>
  );
}
