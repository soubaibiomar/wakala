import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { Vehicle } from '../types/vehicle';

interface CompareContextType {
  compareList: Vehicle[];
  addVehicle: (vehicle: Vehicle) => void;
  removeVehicle: (id: string) => void;
  clearCompare: () => void;
  isDrawerOpen: boolean;
  setDrawerOpen: (isOpen: boolean) => void;
}

const CompareContext = createContext<CompareContextType | undefined>(undefined);

export const CompareProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [compareList, setCompareList] = useState<Vehicle[]>(() => {
    const saved = localStorage.getItem('wakala_compare_list');
    return saved ? JSON.parse(saved) : [];
  });
  const [isDrawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem('wakala_compare_list', JSON.stringify(compareList));
  }, [compareList]);

  const addVehicle = (vehicle: Vehicle) => {
    if (compareList.length < 4 && !compareList.find((v) => v.id === vehicle.id)) {
      setCompareList([...compareList, vehicle]);
      setDrawerOpen(true);
    }
  };

  const removeVehicle = (id: string) => {
    setCompareList(compareList.filter((v) => v.id !== id));
    if (compareList.length <= 1) {
      setDrawerOpen(false);
    }
  };

  const clearCompare = () => {
    setCompareList([]);
    setDrawerOpen(false);
  };

  return (
    <CompareContext.Provider
      value={{
        compareList,
        addVehicle,
        removeVehicle,
        clearCompare,
        isDrawerOpen,
        setDrawerOpen,
      }}
    >
      {children}
    </CompareContext.Provider>
  );
};

export const useCompare = () => {
  const context = useContext(CompareContext);
  if (context === undefined) {
    throw new Error('useCompare must be used within a CompareProvider');
  }
  return context;
};
