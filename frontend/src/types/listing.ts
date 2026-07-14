/**
 * types/listing.ts — Interfaces annonces (miroir du schema Pydantic backend).
 */

import type { Vehicle } from './vehicle';

export type ListingStatus = 'draft' | 'active' | 'sold' | 'expired' | 'flagged';

export interface Listing {
  id: string;
  vehicle_id: string;
  status: ListingStatus;
  published_at?: string;
  sold_at?: string;
  expires_at?: string;

  // Anti-fraude (nullable)
  fraud_score?: number;
  fraud_flags: unknown[];
  is_manually_reviewed: boolean;

  // Média
  images_urls: string[];
  thumbnail_url?: string;
  video_url?: string;

  // Stats
  view_count: number;
  contact_count: number;
  favorite_count: number;

  // Promotion
  is_boosted: boolean;
  boost_expires_at?: string;

  created_at: string;
  updated_at: string;

  // Relation
  vehicle?: Vehicle;
}

export interface ListingCreatePayload {
  vehicle_id: string;
  images_urls?: string[];
  thumbnail_url?: string;
  status?: ListingStatus;
}

export interface Review {
  id: string;
  author_id: string;
  target_type: 'vehicle' | 'seller';
  vehicle_id?: string;
  seller_id?: string;
  rating: number;
  title?: string;
  comment: string;
  sentiment_score?: number;
  sentiment_label?: string;
  key_phrases?: string[];
  is_approved: boolean;
  is_flagged: boolean;
  created_at: string;
  author?: import('./user').UserBrief;
}
