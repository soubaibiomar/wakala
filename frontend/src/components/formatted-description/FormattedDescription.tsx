import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ShieldCheck, Snowflake, Star, Zap, Info, CheckCircle2 } from 'lucide-react';
import './FormattedDescription.css';

interface FormattedDescriptionProps {
  text?: string;
}

const getCategoryIcon = (categoryName: string) => {
  const lower = categoryName.toLowerCase();
  if (lower.includes('sécurité') || lower.includes('securite')) return <ShieldCheck className="category-icon" />;
  if (lower.includes('confort')) return <Snowflake className="category-icon" />;
  if (lower.includes('esthétique') || lower.includes('esthetique') || lower.includes('design')) return <Star className="category-icon" />;
  if (lower.includes('multimédia') || lower.includes('multimedia') || lower.includes('connectivité')) return <Zap className="category-icon" />;
  return <Info className="category-icon" />;
};

function parseBulletedDescription(text: string) {
  // Regex to find known categories before a bullet
  const categoryRegex = /(Sécurité|Confort|Esthétique|Connectivité & Multimédia|Multimédia|Infodivertissement|Design|Extérieur|Intérieur|Technique|Suppléments et options)\s*•/gi;
  
  const sections: { heading: string, items: string[] }[] = [];
  
  let match;
  const matches = [];
  // Need to reset lastIndex since it's a global regex
  categoryRegex.lastIndex = 0;
  while ((match = categoryRegex.exec(text)) !== null) {
    matches.push({
      category: match[1],
      index: match.index,
      length: match[0].length
    });
  }
  
  if (matches.length === 0) return null;
  
  const firstMatchIndex = matches[0].index;
  const introText = text.substring(0, firstMatchIndex).trim();
  
  for (let i = 0; i < matches.length; i++) {
    const start = matches[i].index + matches[i].length;
    const end = i < matches.length - 1 ? matches[i + 1].index : text.length;
    const content = text.substring(start, end).trim();
    
    // Split by bullet point
    const items = content.split('•').map(s => s.trim()).filter(s => s);
    
    sections.push({
      heading: matches[i].category.trim(),
      items
    });
  }
  
  return { introText, sections };
}

export default function FormattedDescription({ text }: FormattedDescriptionProps) {
  if (!text) return null;

  // 1. If text comes from Wandaloo (Véhicule Neuf) with Markdown ###
  if (text.includes('###')) {
    const parts = text.split(/(?=### )/g);
    
    return (
      <div className="formatted-description">
        {parts.map((part, index) => {
          if (!part.trim()) return null;
          
          const isHeading = part.trim().startsWith('###');
          let content = part;
          let heading = '';
          
          if (isHeading) {
            const firstLineEnd = part.indexOf('\n');
            if (firstLineEnd !== -1) {
              heading = part.substring(3, firstLineEnd).trim();
              content = part.substring(firstLineEnd + 1);
            } else {
              heading = part.substring(3).trim();
              content = '';
            }
          }
          
          if (!isHeading && content.includes('•')) {
            const bulletedData = parseBulletedDescription(content);
            if (bulletedData) {
              return (
                <div key={index}>
                  {bulletedData.introText && (
                    <div className="desc-markdown-content" style={{ marginBottom: '24px' }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{bulletedData.introText}</ReactMarkdown>
                    </div>
                  )}
                  
                  {bulletedData.sections.map((section, sIdx) => (
                    <div key={`sec-${sIdx}`} className="desc-section has-heading">
                      <div className="desc-category-header">
                        {getCategoryIcon(section.heading)}
                        <h4 className="desc-category-title">{section.heading}</h4>
                      </div>
                      <ul className="desc-list">
                        {section.items.map((item, idx) => (
                          <li key={idx} className="desc-list-item">
                            <CheckCircle2 size={14} className="list-bullet" /> <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              );
            }
          }

          return (
            <div key={index} className={`desc-section ${isHeading ? 'has-heading' : ''}`}>
              {isHeading && (
                <div className="desc-category-header">
                  {getCategoryIcon(heading)}
                  <h4 className="desc-category-title">{heading}</h4>
                </div>
              )}
              <div className="desc-markdown-content">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table: ({node, ...props}) => (
                      <div className="desc-table-wrapper" style={{ overflowX: 'auto', width: '100%' }}>
                        <table className="desc-table" {...props} />
                      </div>
                    ),
                    th: ({node, ...props}) => <th className="desc-th" {...props} />,
                    td: ({node, ...props}) => {
                      const val = props.children?.toString() || '';
                      if (val === 'Oui') {
                        return <td className="desc-td desc-td-yes"><CheckCircle2 size={16} /> Oui</td>;
                      }
                      if (val === 'Non') {
                        return <td className="desc-td desc-td-no">-</td>;
                      }
                      return <td className="desc-td" {...props} />;
                    },
                    ul: ({node, ...props}) => <ul className="desc-list" {...props} />,
                    li: ({node, ...props}) => <li className="desc-list-item"><CheckCircle2 size={14} className="list-bullet" /> <span>{props.children}</span></li>
                  }}
                >
                  {content}
                </ReactMarkdown>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  // 2. Try to parse bulleted lists format (e.g., from Avito / Moteur)
  const bulletedData = text.includes('•') ? parseBulletedDescription(text) : null;
  
  if (bulletedData) {
    return (
      <div className="formatted-description">
        {bulletedData.introText && (
          <div className="desc-markdown-content" style={{ marginBottom: '24px' }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{bulletedData.introText}</ReactMarkdown>
          </div>
        )}
        
        {bulletedData.sections.map((section, index) => (
          <div key={index} className="desc-section has-heading">
            <div className="desc-category-header">
              {getCategoryIcon(section.heading)}
              <h4 className="desc-category-title">{section.heading}</h4>
            </div>
            <ul className="desc-list">
              {section.items.map((item, idx) => (
                <li key={idx} className="desc-list-item">
                  <CheckCircle2 size={14} className="list-bullet" /> <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    );
  }

  // 3. Fallback for raw text
  return (
    <div className="formatted-description">
      <div className="desc-markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {text}
        </ReactMarkdown>
      </div>
    </div>
  );
}
