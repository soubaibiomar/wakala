import React, { useState, useEffect } from 'react';
import { ArrowRight, Bot, X } from 'lucide-react';
import './PriorityModal.css';
import PriorityTubes from '../../components/priority-tubes/PriorityTubes';
import type { NlpExtractionResult } from '../../services/searchParseService';
import { getIntelligentCriteria } from '../../utils/priorityUtils';

interface PriorityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitPriorities: (priorities: {name: string, value: number}[], budget: number | null) => void;
  nlpResult?: NlpExtractionResult | null;
}





export default function PriorityModal({ isOpen, onClose, onSubmitPriorities, nlpResult }: PriorityModalProps) {
  const [budget, setBudget] = useState<number>(250000);
  const [activeCriteria, setActiveCriteria] = useState<{id: string, label: string, colorClass: string, value: number}[]>([]);

  useEffect(() => {
    if (isOpen) {
      // Set budget if not provided by NLP
      if (nlpResult && nlpResult.budget) {
        setBudget(nlpResult.budget);
      } else {
        setBudget(250000);
      }

      // Determine intelligent criteria to show based on context
      const selected = getIntelligentCriteria(nlpResult);
      setActiveCriteria(selected);
    }
  }, [isOpen, nlpResult]);

  if (!isOpen) return null;

  const handleContinue = () => {
    // Only send budget if the user hasn't already provided it (or send the NLP one too)
    // Actually, sending the budget is fine in either case, but let's just pass what we have.
    const budgetToSend = (nlpResult && nlpResult.budget) ? nlpResult.budget : budget;
    const prios = activeCriteria.map(c => ({ name: c.id, value: c.value }));
    onSubmitPriorities(prios, budgetToSend);
  };

  const updateCriteriaValue = (index: number, newValue: number) => {
    const updated = [...activeCriteria];
    updated[index].value = newValue;
    setActiveCriteria(updated);
  };

  const formatBudget = (value: number) => {
    return new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD', maximumFractionDigits: 0 }).format(value);
  };

  const hideBudgetSlider = Boolean(nlpResult && nlpResult.budget !== null && nlpResult.budget !== undefined);

  return (
    <div className="priority-modal-overlay" onClick={onClose}>
      <div className="priority-modal-container" onClick={e => e.stopPropagation()}>
        <button className="priority-modal-close" onClick={onClose} aria-label="Fermer">
          <X size={24} />
        </button>
        
        <div className="priority-header">
          <Bot size={40} className="priority-icon" />
          <h1>Ajustez vos préférences</h1>
          <p>
            {nlpResult?.priorites?.length 
              ? `Nous avons bien noté vos critères (${nlpResult.priorites.join(', ')}). Ajustez ces autres points pour affiner notre recherche !`
              : 'Personnalisez vos priorités pour que notre IA puisse vous proposer les meilleures recommandations.'
            }
          </p>
        </div>

        <PriorityTubes 
          criteria={activeCriteria}
          budget={budget}
          onCriteriaChange={updateCriteriaValue}
          onBudgetChange={setBudget}
          hideBudget={hideBudgetSlider}
        />

        <button className="continue-btn" onClick={handleContinue}>
          Lancer la recherche IA
          <ArrowRight size={20} />
        </button>

      </div>
    </div>
  );
}
