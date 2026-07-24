import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Camera, Calendar, Gauge, Wrench, Loader2, UploadCloud } from 'lucide-react';
import { useState } from 'react';

type AddServiceFormData = {
  service_type: str;
  date_str: string;
  mileage: number;
  cost?: number;
  notes?: string;
  receipt?: FileList;
};

export function AddServiceForm({ carId, onSuccess }: { carId: string, onSuccess: () => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<AddServiceFormData>();
  const [preview, setPreview] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await fetch('http://localhost:8000/api/v1/services/add', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: data,
      });
      if (!response.ok) throw new Error('Failed to add service');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicle_services', carId] });
      onSuccess();
    }
  });

  const onSubmit = (data: AddServiceFormData) => {
    const formData = new FormData();
    formData.append('car_id', carId);
    formData.append('service_type', data.service_type);
    formData.append('date_str', data.date_str);
    formData.append('mileage', data.mileage.toString());
    if (data.cost) formData.append('cost', data.cost.toString());
    if (data.notes) formData.append('notes', data.notes);
    if (data.receipt && data.receipt.length > 0) {
      formData.append('receipt', data.receipt[0]);
    }

    mutation.mutate(formData);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Type d'entretien */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Type d'entretien</label>
          <div className="relative">
            <Wrench className="absolute left-3 top-3 h-5 w-5 text-gray-500" />
            <select
              {...register('service_type', { required: 'Requis' })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white focus:ring-2 focus:ring-accent outline-none"
            >
              <option value="">Sélectionner...</option>
              <option value="Vidange">Vidange</option>
              <option value="Pneus">Pneus</option>
              <option value="Freinage">Freinage</option>
              <option value="Contrôle Technique">Contrôle Technique</option>
              <option value="Autre">Autre</option>
            </select>
          </div>
          {errors.service_type && <span className="text-red-400 text-sm">{errors.service_type.message}</span>}
        </div>

        {/* Date */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Date</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-3 h-5 w-5 text-gray-500" />
            <input
              type="date"
              {...register('date_str', { required: 'Requis' })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white focus:ring-2 focus:ring-accent outline-none"
            />
          </div>
          {errors.date_str && <span className="text-red-400 text-sm">{errors.date_str.message}</span>}
        </div>

        {/* Kilométrage */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Kilométrage (km)</label>
          <div className="relative">
            <Gauge className="absolute left-3 top-3 h-5 w-5 text-gray-500" />
            <input
              type="number"
              {...register('mileage', { required: 'Requis', min: 0 })}
              placeholder="ex: 120500"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-white focus:ring-2 focus:ring-accent outline-none"
            />
          </div>
          {errors.mileage && <span className="text-red-400 text-sm">{errors.mileage.message}</span>}
        </div>
        
        {/* Cost */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Coût (MAD)</label>
          <input
            type="number"
            {...register('cost', { min: 0 })}
            placeholder="Optionnel"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 px-4 text-white focus:ring-2 focus:ring-accent outline-none"
          />
        </div>
      </div>

      {/* Upload Facture Mobile-First */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Facture ou Reçu</label>
        <div className="relative w-full border-2 border-dashed border-slate-600 rounded-xl overflow-hidden hover:border-accent transition-colors">
          <input
            type="file"
            accept="image/*"
            capture="environment"
            {...register('receipt')}
            onChange={(e) => {
                register('receipt').onChange(e);
                handleImageChange(e);
            }}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          />
          <div className="flex flex-col items-center justify-center p-8 bg-slate-800/50">
            {preview ? (
              <img src={preview} alt="Facture" className="max-h-48 rounded-lg object-contain" />
            ) : (
              <>
                <div className="bg-slate-700 p-4 rounded-full mb-3">
                  <Camera className="h-8 w-8 text-accent" />
                </div>
                <p className="text-sm text-gray-300 font-medium">Prendre une photo ou importer</p>
              </>
            )}
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Notes</label>
        <textarea
          {...register('notes')}
          rows={3}
          placeholder="Détails de l'intervention..."
          className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 px-4 text-white focus:ring-2 focus:ring-accent outline-none resize-none"
        ></textarea>
      </div>

      <button
        type="submit"
        disabled={mutation.isPending}
        className="w-full bg-accent hover:bg-accent/90 text-white font-bold py-4 rounded-xl flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
      >
        {mutation.isPending ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Enregistrement...</span>
          </>
        ) : (
          <span>Ajouter l'entretien</span>
        )}
      </button>
    </form>
  );
}
