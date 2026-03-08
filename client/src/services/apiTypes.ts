import type { DateGranularity } from "@/services/types";

export interface ApiUser {
  id: number;
  name: string;
  email: string;
  last_login: string;
  created_at: string;
  updated_at: string;
}

export interface ApiAuthResponse {
  user: ApiUser;
  access_token: string;
  token_type: string;
}

export interface ApiTimelineSummary {
  id: number;
  user_id: number;
  title: string;
  description?: string | null;
  slug?: string | null;
  is_public: boolean;
  default_zoom_level: number;
  created_at: string;
  updated_at: string;
}

export interface ApiNodeArtifact {
  id: number;
  node_id: number;
  media_type: string;
  caption?: string | null;
}

export interface ApiTimelineNode {
  id: number;
  timeline_id: number;
  parent_id: number | null;
  title: string;
  type: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  short_summary?: string;
  description?: string;
  private_notes?: string;
  date_granularity: string;
  media: ApiNodeArtifact[];
  children: ApiTimelineNode[];
}

export interface ApiTimeline extends ApiTimelineSummary {
  nodes: ApiTimelineNode[];
}

export interface ApiTimelineCreateRequest {
  title: string;
  description?: string | null;
  slug?: string | null;
  is_public: boolean;
  default_zoom_level: number;
}

export interface ApiTimelineNodeCreateRequest {
  timeline_id: number;
  parent_id?: number | null;
  title: string;
  type: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  short_summary?: string | undefined;
  description?: string | undefined;
  private_notes?: string | undefined;
  date_granularity: DateGranularity;
  github_repo_id?: number;
  github_pr_id?: number;
}

export interface ApiTimelineNodeUpdateRequest {
  parent_id?: number | null;
  title: string;
  type: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  short_summary?: string | undefined;
  description?: string | undefined;
  private_notes?: string | undefined;
  date_granularity: DateGranularity;
  github_repo_id?: number;
  github_pr_id?: number;
}

export interface ApiGithubSyncStatus {
  is_connected: boolean;
  sync_status: string;
  last_synced_at: string | null;
  last_sync_error: string | null;
}

export interface ApiGithubRepository {
  id: number;
  full_name: string;
  html_url: string;
  updated_at: string;
}
