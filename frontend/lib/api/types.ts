/** Types for the gateway API contract (see the project spec). */

export interface AuthUser {
  id: string;
  email: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export interface Link {
  id: string;
  short_code: string;
  long_url: string;
  short_url: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
}

export interface LinkList {
  items: Link[];
  limit: number;
  offset: number;
  total: number;
}

export interface DailyClicks {
  date: string;
  count: number;
}

export interface ReferrerCount {
  referrer: string;
  count: number;
}

export interface Stats {
  total_clicks: number;
  clicks_by_day: DailyClicks[];
  top_referrers: ReferrerCount[];
}
