import type { TimelineNodeFormValues } from "@/features/timeline/components/types";
import type {
  ApiUser,
  ApiAuthResponse,
  ApiTimelineSummary,
  ApiTimeline,
  ApiTimelineNode,
  ApiTimelineNodeCreateRequest,
  ApiTimelineNodeUpdateRequest,
  ApiTimelineCreateRequest,
} from "@/services/apiTypes";
import {
  NODE_TYPES,
  DATE_GRANULARITY,
  type User,
  type AuthResponse,
  type TimelineSummary,
  type Timeline,
  type TimelineNode,
  type NodeType,
  type DateGranularity,
  type TimelineCreateRequest,
} from "@/services/types";

export const adaptUser = (data: ApiUser): User => ({
  id: data.id,
  name: data.name,
  email: data.email,
  lastLogin: new Date(data.last_login),
  createdAt: new Date(data.created_at),
  updatedAt: new Date(data.updated_at),
});

export const adaptAuthResponse = (data: ApiAuthResponse): AuthResponse => ({
  user: adaptUser(data.user),
  accessToken: data.access_token,
  tokenType: data.token_type,
});

export const adaptTimelineSummary = (
  data: ApiTimelineSummary,
): TimelineSummary => ({
  id: data.id,
  userId: data.user_id,
  title: data.title,
  description: data.description || undefined,
  slug: data.slug || undefined,
  isPublic: data.is_public,
  defaultZoomLevel: data.default_zoom_level,
  createdAt: new Date(data.created_at),
  updatedAt: new Date(data.updated_at),
});

export const adaptTimeline = (data: ApiTimeline): Timeline => ({
  id: data.id,
  userId: data.user_id,
  title: data.title,
  description: data.description || undefined,
  slug: data.slug || undefined,
  isPublic: data.is_public,
  defaultZoomLevel: data.default_zoom_level,
  createdAt: new Date(data.created_at),
  updatedAt: new Date(data.updated_at),
  nodes: data.nodes.map(adaptTimelineNode),
});

export const adaptTimelineNode = (data: ApiTimelineNode): TimelineNode => ({
  id: data.id,
  timelineId: data.timeline_id,
  parentId: data.parent_id,
  title: data.title,
  type: data.type as NodeType,
  startDate: new Date(data.start_date),
  endDate: data.end_date ? new Date(data.end_date) : null,
  isCurrent: data.is_current,
  shortSummary: data.short_summary,
  description: data.description,
  privateNotes: data.private_notes,
  dateGranularity: data.date_granularity as DateGranularity,
  children: data.children?.map(adaptTimelineNode),
  color: getNodeColor(data.type as NodeType),
});

export const getNodeColor = (type: NodeType): string => {
  switch (type) {
    case NODE_TYPES.WORK:
      return "bg-blue-600";
    case NODE_TYPES.EDUCATION:
      return "bg-green-600";
    case NODE_TYPES.PROJECT:
      return "bg-purple-600";
    case NODE_TYPES.MILESTONE:
      return "bg-yellow-500";
    case NODE_TYPES.CERTIFICATION:
      return "bg-orange-500";
    case NODE_TYPES.BLOG:
      return "bg-pink-500";
    default:
      return "bg-gray-400";
  }
};

export const adaptTimelineCreateRequest = (
  data: TimelineCreateRequest,
): ApiTimelineCreateRequest => ({
  title: data.title,
  description: data.description || null,
  slug: data.slug || null,
  is_public: data.isPublic,
  default_zoom_level: data.defaultZoomLevel,
});

export const adaptNodeToCreateRequest = (
  data: TimelineNodeFormValues,
  timelineId: number,
): ApiTimelineNodeCreateRequest => ({
  timeline_id: timelineId,
  parent_id: data.parentId ?? null,
  title: data.title,
  type: data.type,
  start_date: data.startDate.toISOString(),
  end_date: data.endDate ? data.endDate.toISOString() : null,
  is_current: data.isCurrent,
  short_summary: data.shortSummary || undefined,
  description: data.description || undefined,
  private_notes: data.privateNotes || undefined,
  date_granularity: DATE_GRANULARITY.EXACT,
});

export const adaptNodeToUpdateRequest = (
  data: TimelineNodeFormValues,
): ApiTimelineNodeUpdateRequest => ({
  parent_id: data.parentId ?? null,
  title: data.title,
  type: data.type,
  start_date: data.startDate.toISOString(),
  end_date: data.endDate ? data.endDate.toISOString() : null,
  is_current: data.isCurrent,
  short_summary: data.shortSummary || undefined,
  description: data.description || undefined,
  private_notes: data.privateNotes || undefined,
  date_granularity: DATE_GRANULARITY.EXACT,
});
