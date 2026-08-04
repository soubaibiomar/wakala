import { useEffect } from 'react';

interface SEOProps {
  title: string;
  description: string;
  canonical?: string;
  schema?: Record<string, any>;
}

export default function SEO({ title, description, canonical, schema }: SEOProps) {
  useEffect(() => {
    // 1. Update Title
    document.title = title;

    // 2. Update Meta Description
    let metaDescription = document.querySelector('meta[name="description"]');
    if (!metaDescription) {
      metaDescription = document.createElement('meta');
      metaDescription.setAttribute('name', 'description');
      document.head.appendChild(metaDescription);
    }
    metaDescription.setAttribute('content', description);

    // 3. Update Canonical Link
    if (canonical) {
      let linkCanonical = document.querySelector('link[rel="canonical"]');
      if (!linkCanonical) {
        linkCanonical = document.createElement('link');
        linkCanonical.setAttribute('rel', 'canonical');
        document.head.appendChild(linkCanonical);
      }
      linkCanonical.setAttribute('href', canonical);
    }

    // 4. Update Schema.org JSON-LD
    if (schema) {
      let scriptSchema = document.querySelector('#seo-schema');
      if (!scriptSchema) {
        scriptSchema = document.createElement('script');
        scriptSchema.setAttribute('id', 'seo-schema');
        scriptSchema.setAttribute('type', 'application/ld+json');
        document.head.appendChild(scriptSchema);
      }
      scriptSchema.textContent = JSON.stringify(schema);
    }

    return () => {
      // Cleanup schema on unmount to avoid duplicates across route changes
      const scriptSchema = document.querySelector('#seo-schema');
      if (scriptSchema) {
        scriptSchema.remove();
      }
    };
  }, [title, description, canonical, schema]);

  return null;
}
