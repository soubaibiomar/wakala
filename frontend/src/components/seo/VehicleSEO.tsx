import React from 'react';
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

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData).replace(/</g, '\\u003c') }}
    />
  );
}
