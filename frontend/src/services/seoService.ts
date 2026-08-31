import api from './api';

export interface ComparatifSeoVehicle {
  id: string;
  brand_name: string;
  brand_slug: string;
  brand_logo?: string;
  model_name: string;
  model_slug: string;
  trim_name: string;
  trim_slug: string;
  full_name: string;
  image_url?: string;
  body_type?: string;
  price_new_mad: number;
  promo_price_mad?: number;
  clef_en_main_mad: number;
  vignette_dgi_mad: number;
  warranty: string;
  specs: {
    fuel_type: string;
    fiscal_power_cv: string;
    engine_power_hp: number;
    torque_nm?: number;
    transmission: string;
    consumption_l_100: number;
    trunk_capacity_l: number;
    euro_ncap_stars: number;
  };
  radar_scores: {
    economie: number;
    puissance: number;
    espace: number;
    securite: number;
    ecologie: number;
  };
}

export interface ComparatifSeoData {
  slug: string;
  title: string;
  meta_description: string;
  self_contained_answer: string;
  updated_at: string;
  vehicle1: ComparatifSeoVehicle;
  vehicle2: ComparatifSeoVehicle;
  price_difference_mad: number;
  cheaper_vehicle: string;
  faqs: Array<{ question: string; answer: string }>;
  breadcrumbs: Array<{ name: string; item: string }>;
}

export interface CitySeoShowroom {
  id: string;
  name: string;
  dealership_name: string;
  address: string;
  phone?: string;
  city: string;
  brand_affiliations?: string[];
}

export interface CitySeoData {
  city_slug: string;
  city_name: string;
  title: string;
  meta_description: string;
  self_contained_answer: string;
  updated_at: string;
  showrooms_count: number;
  showrooms: CitySeoShowroom[];
  models: Array<{
    id: string;
    name: string;
    slug: string;
    brand_name: string;
    brand_slug: string;
    body_type?: string;
    hero_image_url?: string;
    starting_price_mad: number;
    trims_count: number;
  }>;
  min_price_mad: number;
  avg_price_mad: number;
  other_cities: Array<{ slug: string; name: string }>;
  faqs: Array<{ question: string; answer: string }>;
  breadcrumbs: Array<{ name: string; item: string }>;
}

export interface BrandSeoData {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  country_of_origin?: string;
  description?: string;
  title: string;
  meta_description: string;
  self_contained_answer: string;
  updated_at: string;
  models_count: number;
  min_price_mad: number;
  max_price_mad: number;
  available_body_types: string[];
  available_fuels: string[];
  warranty_years: number;
  models: Array<{
    id: string;
    name: string;
    slug: string;
    body_type?: string;
    hero_image_url?: string;
    starting_price_mad: number;
    trims_count: number;
  }>;
  faqs: Array<{ question: string; answer: string }>;
  breadcrumbs: Array<{ name: string; item: string }>;
}

export interface SeoHubData {
  pillar_url: string;
  financing_url: string;
  ai_advisor_url: string;
  brands: Array<{ name: string; slug: string; models_count: number }>;
  cities: Array<{ slug: string; name: string }>;
  popular_comparisons: Array<{ slug: string; title: string }>;
  featured_models: Array<{
    id: string;
    name: string;
    slug: string;
    brand_name: string;
    body_type?: string;
    hero_image_url?: string;
    starting_price_mad: number;
  }>;
}

export const seoService = {
  getComparatifData: async (slug: string): Promise<ComparatifSeoData> => {
    const res = await api.get<ComparatifSeoData>(`/v1/seo-pages/comparatif/${slug}`);
    return res.data;
  },

  getCityData: async (citySlug: string): Promise<CitySeoData> => {
    const res = await api.get<CitySeoData>(`/v1/seo-pages/city/${citySlug}`);
    return res.data;
  },

  getBrandData: async (brandSlug: string): Promise<BrandSeoData> => {
    const res = await api.get<BrandSeoData>(`/v1/seo-pages/brand/${brandSlug}`);
    return res.data;
  },

  getHubData: async (): Promise<SeoHubData> => {
    const res = await api.get<SeoHubData>(`/v1/seo-pages/hub`);
    return res.data;
  },
};

export default seoService;
