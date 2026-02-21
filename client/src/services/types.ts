import { z } from "zod";

const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string(),
  lastLogin: z.coerce.date(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});

export type User = z.infer<typeof UserSchema>;

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest extends LoginRequest {
  name: string;
}

export const AuthResponseSchema = z.object({
  user: UserSchema,
  accessToken: z.string(),
  tokenType: z.string(),
});

export type AuthResponse = z.infer<typeof AuthResponseSchema>;

export const NODE_TYPES = {
  WORK: "work",
  EDUCATION: "education",
  PROJECT: "project",
  MILESTONE: "milestone",
  CERTIFICATION: "certification",
  BLOG: "blog",
} as const;

export const NodeTypeSchema = z.nativeEnum(NODE_TYPES);
export type NodeType = z.infer<typeof NodeTypeSchema>;

export const DATE_GRANULARITY = {
  EXACT: "exact",
  MONTH: "month",
  YEAR: "year",
  SEASON: "season",
} as const;

const DateGranularitySchema = z.nativeEnum(DATE_GRANULARITY);
export type DateGranularity = z.infer<typeof DateGranularitySchema>;

const BaseTimelineNodeSchema = z.object({
  id: z.number(),
  timelineId: z.number(),
  parentId: z.number().nullable(),
  title: z.string(),
  type: NodeTypeSchema,
  startDate: z.coerce.date(),
  endDate: z.coerce.date().nullable().optional(),
  isCurrent: z.boolean(),
  shortSummary: z.string().optional(),
  description: z.string().optional(),
  privateNotes: z.string().optional(),
  dateGranularity: DateGranularitySchema,
  color: z.string(),
});

export type TimelineNode = z.infer<typeof BaseTimelineNodeSchema> & {
  children: TimelineNode[];
};

const TimelineNodeSchema: z.ZodType<TimelineNode> =
  BaseTimelineNodeSchema.extend({
    children: z.lazy(() => TimelineNodeSchema.array()),
  });

const TimelineSummarySchema = z.object({
  id: z.number(),
  userId: z.number(),
  title: z.string(),
  description: z.string().optional(),
  slug: z.string().optional(),
  isPublic: z.boolean(),
  defaultZoomLevel: z.number(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});

export type TimelineSummary = z.infer<typeof TimelineSummarySchema>;

export const TimelineSchema = TimelineSummarySchema.extend({
  nodes: z.array(TimelineNodeSchema),
});

export type Timeline = z.infer<typeof TimelineSchema>;

export interface TimelineCreateRequest {
  title: string;
  description?: string;
  slug?: string;
  isPublic: boolean;
  defaultZoomLevel: number;
}

export const APIErrorSchema = z.object({
  code: z.string(),
  message: z.string(),
  timestamp: z.coerce.date().optional(),
  details: z.record(z.any()).optional(),
});

export type APIError = z.infer<typeof APIErrorSchema>;

export const GithubAuthUrlResponseSchema = z.object({
  authUrl: z.string(),
});

export type GithubAuthUrlResponse = z.infer<typeof GithubAuthUrlResponseSchema>;
