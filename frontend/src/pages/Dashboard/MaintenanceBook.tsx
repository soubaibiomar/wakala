import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Plus, Car } from 'lucide-react';
import api from '../../services/api';
import { AddServiceForm } from '../../components/maintenance/AddServiceForm';
import { MaintenanceTimeline } from '../../components/maintenance/MaintenanceTimeline';

interface VehicleOption {
  id: string;
  brand: string;
  model: string;
}

export default function MaintenanceBook() {
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedCarId, setSelectedCarId] = useState<string>('');

  const { data: myCars, isLoading } = useQuery<VehicleOption[]>({
    queryKey: ['my_vehicles'],
    queryFn: async () => {
      const res = await api.get('/vehicles/me');
      return res.data;
    }
  });

  // Default to first car if available
  if (myCars && myCars.length > 0 && !selectedCarId) {
    setSelectedCarId(myCars[0].id);
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <BookOpen className="text-accent h-8 w-8" />
            Carnet d'Entretien
          </h1>
          <p className="text-gray-400 mt-2">
            Gérez l'historique de maintenance de vos véhicules pour maximiser leur valeur.
          </p>
        </div>
        {selectedCarId && !showAddForm && (
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-accent hover:bg-accent/90 text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-colors"
          >
            <Plus className="h-5 w-5" />
            Ajouter un entretien
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="text-center text-gray-400">Chargement de vos véhicules...</div>
      ) : !myCars || myCars.length === 0 ? (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center">
          <Car className="h-12 w-12 text-slate-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Aucun véhicule</h3>
          <p className="text-gray-400">Vous devez ajouter un véhicule avant de pouvoir utiliser le carnet d'entretien.</p>
        </div>
      ) : (
        <>
          {/* Sélecteur de véhicule */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center gap-4">
            <label className="text-gray-300 font-medium shrink-0">Sélectionner un véhicule :</label>
            <select
              value={selectedCarId}
              onChange={(e) => setSelectedCarId(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white outline-none focus:border-accent w-full md:w-auto"
            >
              {myCars.map(car => (
                <option key={car.id} value={car.id}>{car.brand} {car.model}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Timeline */}
            <div className={`lg:col-span-7 ${showAddForm ? 'hidden lg:block' : ''}`}>
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-6">Historique complet</h2>
                <MaintenanceTimeline carId={selectedCarId} />
              </div>
            </div>

            {/* Form or Next Reminder Widget */}
            <div className={`lg:col-span-5 ${!showAddForm ? 'hidden lg:block' : ''}`}>
              {showAddForm ? (
                <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-xl sticky top-6">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-white">Nouvelle Facture</h2>
                    <button 
                      onClick={() => setShowAddForm(false)}
                      className="text-gray-400 hover:text-white text-sm font-medium"
                    >
                      Annuler
                    </button>
                  </div>
                  <AddServiceForm 
                    carId={selectedCarId} 
                    onSuccess={() => setShowAddForm(false)} 
                  />
                </div>
              ) : (
                <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 sticky top-6">
                  <div className="text-center py-12">
                    <BookOpen className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                    <p className="text-gray-400">
                      Cliquez sur "Ajouter un entretien" pour importer une facture.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
