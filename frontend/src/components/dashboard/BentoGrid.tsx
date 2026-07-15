import React from 'react';
import styles from './BentoGrid.module.css';

interface BentoGridProps {
  children: React.ReactNode;
}

export function BentoGrid({ children }: BentoGridProps) {
  return (
    <div className={styles.bentoGrid}>
      {children}
    </div>
  );
}

interface BentoWidgetProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
  colSpan?: 1 | 2 | 3;
  rowSpan?: 1 | 2;
  isLoading?: boolean;
}

export function BentoWidget({ 
  children, 
  title, 
  className = '',
  colSpan = 1,
  rowSpan = 1,
  isLoading = false
}: BentoWidgetProps) {
  const spanClass = `${styles[`colSpan${colSpan}`]} ${styles[`rowSpan${rowSpan}`]}`;

  return (
    <div className={`${styles.widget} ${spanClass} ${className}`}>
      {title && <h3 className={styles.widgetTitle}>{title}</h3>}
      
      <div className={styles.widgetContent}>
        {isLoading ? (
          <div className={styles.skeleton}>
            <div className={styles.skeletonLine} style={{ width: '70%' }}></div>
            <div className={styles.skeletonLine} style={{ width: '100%' }}></div>
            <div className={styles.skeletonLine} style={{ width: '40%' }}></div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
