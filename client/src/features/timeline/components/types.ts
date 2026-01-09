import { z } from "zod";
import { NodeTypeSchema } from "@/services/types";

export const timelineNodeSchema = z
  .object({
    title: z.string().min(1, "Title is required").max(100, "Title is too long"),
    id: z.number().nullable(),
    type: NodeTypeSchema,

    parentId: z
      .union([z.string(), z.number(), z.null()])
      .transform((val) => {
        if (val === "" || val === "0" || val === 0 || val === null) return null;
        return Number(val);
      })
      .optional(),

    startDate: z.coerce.date({
      required_error: "Start date is required",
      invalid_type_error: "Start date is required",
    }),
    endDate: z.coerce.date().nullable().optional(),
    isCurrent: z.boolean().default(false),

    shortSummary: z.string().nullable().optional().or(z.literal("")),
    description: z.string().nullable().optional().or(z.literal("")),
    privateNotes: z.string().nullable().optional().or(z.literal("")),

    media: z.array(z.any()).optional(),
  })
  .superRefine((data, ctx) => {
    if (!data.isCurrent && !data.endDate) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "End date is required unless this is a current position",
        path: ["endDate"],
      });
    }

    if (data.endDate && data.startDate > data.endDate) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "End date cannot be earlier than start date",
        path: ["endDate"],
      });
    }
  });

export type TimelineNodeFormValues = z.infer<typeof timelineNodeSchema>;
