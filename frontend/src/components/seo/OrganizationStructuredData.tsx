import React from 'react';

export const OrganizationStructuredData: React.FC = () => {
  const schemaData = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Wakala Maroc',
    alternateName: 'Wakala',
    url: 'https://wakala.ma',
    logo: 'https://wakala.ma/logos/wakala.png',
    description: "Le tiers de confiance automobile au Maroc. Catalogue officiel certifié 100% véhicules neufs, simulateur de dédouanement (Diwana), Scoring Déterministe 8D et Conseiller IA.",
    areaServed: {
      '@type': 'Country',
      name: 'Maroc',
    },
    address: {
      '@type': 'PostalAddress',
      addressCountry: 'MA',
      addressLocality: 'Casablanca',
    },
    sameAs: [
      'https://www.linkedin.com/company/wakala-maroc',
      'https://twitter.com/wakala_ma',
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'customer service',
      availableLanguage: ['French', 'Arabic'],
      areaServed: 'MA',
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData).replace(/</g, '\\u003c') }}
    />
  );
};

export default OrganizationStructuredData;
