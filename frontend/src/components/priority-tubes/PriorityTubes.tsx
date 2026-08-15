import React from 'react';
import './PriorityTubes.css';

interface CriteriaItem {
  id: string;
  label: string;
  colorClass: string;
  value: number;
}

interface PriorityTubesProps {
  criteria: CriteriaItem[];
  budget: number | null;
  onCriteriaChange: (index: number, newValue: number) => void;
  onBudgetChange: (newValue: number) => void;
  hideBudget?: boolean;
}

export default function PriorityTubes({ 
  criteria, 
  budget, 
  onCriteriaChange, 
  onBudgetChange, 
  hideBudget = false 
}: PriorityTubesProps) {

  const formatBudget = (value: number) => {
    return new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD', maximumFractionDigits: 0 }).format(value);
  };

  return (
    <>
      <div className="tubes-container">
        {criteria.map((c, index) => (
          <div className="tube-wrapper" key={c.id}>
            <div className="tube-outer">
              <div 
                className={`tube-inner ${c.colorClass}`} 
                style={{ height: `${c.value}%` }}
              ></div>
            </div>
            <div className="tube-label">{c.label}</div>
            <div className="tube-value">{c.value}%</div>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={c.value} 
              onChange={(e) => onCriteriaChange(index, Number(e.target.value))}
              className="tube-slider"
            />
          </div>
        ))}
      </div>

      {!hideBudget && budget !== null && (
        <div className="budget-container">
          <div className="budget-label">Budget Maximum Estimé</div>
          <div className="budget-value">{formatBudget(budget)}</div>
          <input 
            type="range" 
            min="30000" 
            max="1500000" 
            step="10000"
            value={budget} 
            onChange={(e) => onBudgetChange(Number(e.target.value))}
            className="budget-slider"
          />
        </div>
      )}
    </>
  );
}
