import React, { useState, useEffect } from 'react';
import './VisitChecklist.css';

interface ChecklistResponse {
  vehicle_id: string;
  trust_score: number;
  confidence: string;
  checklist: string[];
}

export interface VisitChecklistProps {
  vehicleId: string;
}

export default function VisitChecklist({ vehicleId }: VisitChecklistProps) {
  const [data, setData] = useState<ChecklistResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  useEffect(() => {
    // In a real app, this would use a service or fetch directly
    fetch(`http://localhost:8000/api/guided-journey/checklist/${vehicleId}`)
      .then(res => res.json())
      .then(resData => {
        setData(resData);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching checklist:", err);
        setLoading(false);
      });
  }, [vehicleId]);

  const toggleCheck = (index: number) => {
    setCheckedItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (loading) return <div className="visit-checklist-loading">Génération de la checklist intelligente...</div>;
  if (!data) return null;

  return (
    <div className="visit-checklist-container">
      <h3 className="visit-checklist-title">Checklist de Visite IA</h3>
      <p className="visit-checklist-subtitle">
        Générée sur mesure d'après l'analyse de cette annonce (Score: {data.trust_score}%)
      </p>
      <ul className="visit-checklist-list">
        {data.checklist.map((item, index) => (
          <li 
            key={index} 
            className={`visit-checklist-item ${checkedItems[index] ? 'checked' : ''} ${item.startsWith('⚠️') ? 'warning-item' : ''}`}
            onClick={() => toggleCheck(index)}
          >
            <div className="checkbox">
              {checkedItems[index] && <span>✓</span>}
            </div>
            <span className="item-text">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
