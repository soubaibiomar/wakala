import { useQuery } from '@tanstack/react-query';
import { Calendar, Wrench, Settings, AlertTriangle, FileText } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface VehicleService {
  id: string;
  service_type: string;
  mileage: number;
  date: string;
  cost?: number;
  notes?: string;
  receipt_url?: string;
}

const getServiceIcon = (type: string) => {
  const t = type.toLowerCase();
  if (t.includes('vidange') || t.includes('oil')) return <Settings className="text-accent w-5 h-5" />;
  if (t.includes('frein')) return <AlertTriangle className="text-red-400 w-5 h-5" />;
  return <Wrench className="text-blue-400 w-5 h-5" />;
};

export function MaintenanceTimeline({ carId }: { carId: string }) {
  const { data: services, isLoading, error } = useQuery<VehicleService[]>({
    queryKey: ['vehicle_services', carId],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const res = await fetch(`http://localhost:8000/api/v1/services/history/${carId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to fetch timeline');
      return res.json();
    }
  });

  if (isLoading) return <div className="text-gray-400 p-8 text-center animate-pulse">Chargement de l'historique...</div>;
  if (error) return <div className="text-red-400 p-8 text-center">Erreur lors du chargement</div>;
  if (!services || services.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center bg-slate-800/30 rounded-xl border border-slate-700/50">
        <div className="bg-slate-800 p-4 rounded-full mb-4">
          <Wrench className="h-8 w-8 text-slate-500" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">Aucun entretien enregistré</h3>
        <p className="text-sm text-gray-400 max-w-sm">
          Commencez à construire l'historique de votre véhicule pour augmenter sa valeur de revente.
        </p>
      </div>
    );
  }

  return (
    <div className="relative border-l-2 border-slate-700 ml-4 md:ml-6 space-y-8 py-4">
      {services.map((service, idx) => (
        <div key={service.id} className="relative pl-8 md:pl-10 group">
          {/* Timeline Dot */}
          <div className="absolute -left-[11px] top-1 h-5 w-5 rounded-full bg-slate-800 border-2 border-slate-600 group-hover:border-accent transition-colors flex items-center justify-center">
            <div className="h-2 w-2 rounded-full bg-slate-500 group-hover:bg-accent transition-colors" />
          </div>

          <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-5 hover:border-accent/50 transition-colors">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-slate-700/50 rounded-lg">
                  {getServiceIcon(service.service_type)}
                </div>
                <div>
                  <h4 className="text-white font-semibold text-lg">{service.service_type}</h4>
                  <div className="flex items-center text-xs text-gray-400 space-x-2 mt-1">
                    <Calendar className="w-3 h-3" />
                    <span>{format(new Date(service.date), 'dd MMMM yyyy', { locale: fr })}</span>
                    <span>•</span>
                    <span>{service.mileage.toLocaleString()} km</span>
                  </div>
                </div>
              </div>
              {service.cost && (
                <div className="text-right">
                  <span className="inline-block px-3 py-1 bg-accent/10 text-accent font-semibold rounded-full text-sm">
                    {service.cost} MAD
                  </span>
                </div>
              )}
            </div>

            {service.notes && (
              <p className="text-gray-400 text-sm mt-3 bg-slate-900/50 p-3 rounded-lg">
                {service.notes}
              </p>
            )}

            {service.receipt_url && (
              <div className="mt-4 flex">
                <a 
                  href={`http://localhost:8000${service.receipt_url}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 text-sm text-blue-400 hover:text-blue-300 bg-blue-400/10 px-3 py-2 rounded-lg transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <span>Voir la facture</span>
                </a>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
