import api from './api';

export interface BrandItem {
  id: string;
  name: string;
  slug: string;
  logo_url: string | null;
  country_of_origin: string | null;
  models_count: number;
  min_price_mad: number | null;
}

export interface ModelListItem {
  id: string;
  name: string;
  slug: string;
  brand: {
    id: string;
    name: string;
    slug: string;
    logo_url: string | null;
  };
  body_type: string;
  year_start: number;
  hero_image_url: string | null;
  starting_price_mad: number | null;
  max_price_mad: number | null;
  has_promo: boolean;
  available_fuels: string[];
  trims_count: number;
}

export interface PowertrainDetail {
  id: string | null;
  name: string | null;
  fuel_type: string | null;
  fiscal_power_cv: number | null;
  engine_power_hp: number | null;
  torque_nm: number | null;
  transmission: string | null;
  drivetrain?: string | null;
  consumption_l_100: number | null;
  co2_emissions_g_km: number | null;
}

export interface MoroccanTaxBreakdown {
  base_price_mad: number;
  promo_price_mad: number | null;
  effective_price_mad: number;
  vignette_dgi_mad: number;
  immatriculation_carte_grise_mad: number;
  luxury_tax_mad: number;
  frais_dossier_plaques_mad: number;
  total_taxes_and_fees_mad: number;
  total_clef_en_main_mad: number;
  is_hybrid_or_ev_exempt: boolean;
  luxury_tax_applied: boolean;
}

export interface TrimDetail {
  id: string;
  name: string;
  slug: string;
  price_new_mad: number;
  promo_price_mad: number | null;
  is_promo: boolean;
  warranty_years: number;
  warranty_km: number;
  trunk_capacity_l: number | null;
  euro_ncap_stars: number | null;
  image_url: string | null;
  available_colors: Array<{ name: string; hex: string; price_mad: number }>;
  model: {
    id: string;
    name: string;
    slug: string;
    body_type: string;
    year_start: number;
  };
  brand: {
    id: string;
    name: string;
    slug: string;
    logo_url: string | null;
    country_of_origin: string | null;
  };
  powertrain: PowertrainDetail | null;
  on_the_road_breakdown: MoroccanTaxBreakdown;
  equipment_by_category: Array<{
    category_name: string;
    icon: string;
    features: Array<{
      feature_id: string;
      name: string;
      description: string | null;
      status: 'SERIE' | 'OPTION' | 'NON_DISPO';
      option_price_mad: number;
    }>;
  }>;
}

export interface ModelDetail {
  id: string;
  name: string;
  slug: string;
  body_type: string;
  year_start: number;
  hero_image_url: string | null;
  brand: {
    id: string;
    name: string;
    slug: string;
    logo_url: string | null;
    country_of_origin: string | null;
  };
  starting_price_mad: number | null;
  trims: Array<{
    id: string;
    name: string;
    slug: string;
    price_new_mad: number;
    promo_price_mad: number | null;
    is_promo: boolean;
    warranty_years: number;
    warranty_km: number;
    trunk_capacity_l: number | null;
    euro_ncap_stars: number | null;
    image_url: string | null;
    available_colors: Array<{ name: string; hex: string; price_mad: number }>;
    powertrain: PowertrainDetail | null;
    on_the_road_breakdown: {
      vignette_mad: number;
      immatriculation_mad: number;
      luxury_tax_mad: number;
      frais_dossier_mad: number;
      total_clef_en_main_mad: number;
    };
  }>;
}

export interface ComparatorResponse {
  vehicles: Array<{
    id: string;
    name: string;
    slug: string;
    image_url: string | null;
    brand_name: string;
    brand_logo: string | null;
    brand_url?: string | null;
    model_name: string;
    model_url?: string | null;
    trim_name: string;
    trim_url?: string | null;
    ncap_report_url?: string | null;
    real_conso_url?: string | null;
    body_type: string;
    price_new_mad: number;
    promo_price_mad: number | null;
    clef_en_main_mad: number;
    vignette_dgi_mad: number;
    warranty: string;
    specs: {
      fuel_type: string;
      fiscal_power_cv: string;
      engine_power_hp: string;
      torque_nm: string;
      transmission: string;
      consumption_l_100: string;
      trunk_capacity_l: string;
      euro_ncap_stars: string;
    };
    radar_scores: {
      economie: number;
      puissance: number;
      espace: number;
      securite: number;
      ecologie: number;
    };
  }>;
  equipment_matrix: Array<{
    category_name: string;
    icon: string;
    features: Array<{
      feature_id: string;
      feature_name: string;
      has_difference: boolean;
      values_per_vehicle: Record<string, { status: 'SERIE' | 'OPTION' | 'NON_DISPO'; option_price_mad: number }>;
    }>;
  }>;
}

export interface ShowroomItem {
  id: string;
  name: string;
  city: string;
  address: string;
  phone: string | null;
  latitude: number | null;
  longitude: number | null;
  brands: string[];
  dealership: {
    id: string;
    name: string;
    website: string | null;
  };
}

export const newCatalogService = {
  async getBrands(): Promise<BrandItem[]> {
    const res = await api.get('/v1/new-cars/brands');
    return res.data;
  },

  async getModels(params?: {
    brand_slug?: string;
    body_type?: string;
    fuel_type?: string;
    transmission?: string;
    max_price?: number;
    min_price?: number;
  }): Promise<ModelListItem[]> {
    const res = await api.get('/v1/new-cars/models', { params });
    return res.data;
  },

  async getModelDetail(idOrSlug: string): Promise<ModelDetail> {
    const res = await api.get(`/v1/new-cars/models/${idOrSlug}`);
    return res.data;
  },

  async getTrimDetail(idOrSlug: string): Promise<TrimDetail> {
    const res = await api.get(`/v1/new-cars/trims/${idOrSlug}`);
    return res.data;
  },

  async compareTrims(trimIdsOrSlugs: string[]): Promise<ComparatorResponse> {
    const res = await api.post('/v1/comparator/compare', { trim_ids_or_slugs: trimIdsOrSlugs });
    return res.data;
  },

  async getShowrooms(params?: { city?: string; brand?: string }): Promise<ShowroomItem[]> {
    const res = await api.get('/v1/showrooms', { params });
    return res.data;
  },

  async bookTestDrive(payload: {
    trim_id: string;
    showroom_id?: string;
    full_name: string;
    phone_number: string;
    email?: string;
    city: string;
    preferred_date?: string;
    message?: string;
    cndp_consent_accepted: boolean;
  }) {
    const res = await api.post('/v1/leads/test-drive', payload);
    return res.data;
  },

  async requestProformaQuote(payload: {
    trim_id: string;
    showroom_id?: string;
    full_name: string;
    phone_number: string;
    email?: string;
    city: string;
    company_name?: string;
    cndp_consent_accepted: boolean;
  }) {
    const res = await api.post('/v1/leads/quote-proforma', payload);
    return res.data;
  }
};
