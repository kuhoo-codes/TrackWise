import { useState, useEffect, useCallback } from "react";
import { toast } from "react-hot-toast";
import type { CreateTimelineFormValues } from "@/features/dashboard/components/createTimelineModal";
import { getErrorMessage } from "@/lib/error";
import { TimelineService } from "@/services/timeline";
import type { TimelineSummary, TimelineCreateRequest } from "@/services/types";
import { useAuth } from "@/shared/hooks/useAuth";

export const useTimelines = () => {
  const { token } = useAuth();
  const [timelines, setTimelines] = useState<TimelineSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const fetchTimelines = useCallback(async () => {
    if (!token) return;
    try {
      setIsLoading(true);
      const data = await TimelineService.getTimelines();
      setTimelines(data);
    } catch (err: unknown) {
      const msg = getErrorMessage(err, "Failed to load timelines.");
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void fetchTimelines();
  }, [fetchTimelines]);

  const createTimeline = async (data: CreateTimelineFormValues) => {
    if (!token) return false;
    try {
      const payload: TimelineCreateRequest = {
        title: data.title,
        description: data.description ?? "",
        isPublic: data.isPublic,
        defaultZoomLevel: data.defaultZoomLevel,
      };
      await TimelineService.createTimeline(payload);
      await fetchTimelines();
      toast.success("Timeline created!");
      return true;
    } catch (err: unknown) {
      const msg = getErrorMessage(err, "Failed to create timeline.");
      toast.error(msg);
      return false;
    }
  };

  const deleteTimeline = async (id: number) => {
    if (!token) return false;
    try {
      setIsDeleting(true);
      await TimelineService.deleteTimeline(id);
      setTimelines((prev) => prev.filter((t) => t.id !== id));
      toast.success("Timeline deleted.");
      return true;
    } catch (err: unknown) {
      const msg = getErrorMessage(err, "Failed to delete timeline.");
      toast.error(msg);
      return false;
    } finally {
      setIsDeleting(false);
    }
  };

  return {
    timelines,
    isLoading,
    isDeleting,
    createTimeline,
    deleteTimeline,
    refresh: fetchTimelines,
  };
};
