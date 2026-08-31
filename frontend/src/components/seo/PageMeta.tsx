import React from 'react';
import { Helmet } from 'react-helmet-async';

export interface PageMetaProps {
  title: string;
  description: string;
  canonicalUrl?: string;
  ogType?: 'website' | 'article' | 'product';
  ogImage?: string;
  noindex?: boolean;
  schema?: Record<string, any> | Array<Record<string, any>>;
}

export const PageMeta: React.FC<PageMetaProps> = ({
  title,
  description,
  canonicalUrl,
  ogType = 'website',
  ogImage = 'https://wakala.ma/og-image.jpg',
  noindex = false,
  schema,
}) => {
  const formattedTitle = title.includes('Wakala') ? title : `${title} | Wakala Maroc`;
  const canonical = canonicalUrl || (typeof window !== 'undefined' ? window.location.href : 'https://wakala.ma');

  return (
    <Helmet>
      {/* Balises HTML standard */}
      <title>{formattedTitle}</title>
      <meta name="description" content={description} />
      {canonical && <link rel="canonical" href={canonical} />}
      <meta name="robots" content={noindex ? 'noindex, nofollow' : 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1'} />

      {/* Open Graph (Facebook, WhatsApp, LinkedIn, IA crawlers) */}
      <meta property="og:site_name" content="Wakala Maroc" />
      <meta property="og:locale" content="fr_MA" />
      <meta property="og:type" content={ogType} />
      <meta property="og:title" content={formattedTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={canonical} />
      {ogImage && <meta property="og:image" content={ogImage} />}

      {/* Twitter Cards */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={formattedTitle} />
      <meta name="twitter:description" content={description} />
      {ogImage && <meta name="twitter:image" content={ogImage} />}

      {/* Structured Data Schema.org */}
      {schema && (
        <script type="application/ld+json">
          {JSON.stringify(schema).replace(/</g, '\\u003c')}
        </script>
      )}
    </Helmet>
  );
};

export default PageMeta;
