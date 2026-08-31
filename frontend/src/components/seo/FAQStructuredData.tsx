import React from 'react';

export interface FAQItem {
  question: string;
  answer: string;
}

export interface FAQStructuredDataProps {
  faqs: FAQItem[];
}

export const FAQStructuredData: React.FC<FAQStructuredDataProps> = ({ faqs }) => {
  if (!faqs || faqs.length === 0) return null;

  const schemaData = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData).replace(/</g, '\\u003c') }}
    />
  );
};

export default FAQStructuredData;
