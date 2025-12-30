import { useState, useEffect, useCallback } from "react";
import type { TimelineNodeFormValues } from "@/features/timeline/components/types";
import {
  adaptNodeToCreateRequest,
  adaptNodeToUpdateRequest,
} from "@/services/adapters";
import { TimelineService } from "@/services/timeline";
import type { Timeline } from "@/services/types";
import { useAuth } from "@/shared/hooks/useAuth";

const getErrorMessage = (err: unknown, fallback: string): string => {
  if (err instanceof Error) return err.message;
  if (typeof err === "object" && err !== null && "message" in err) {
    return String((err as { message: unknown }).message);
  }
  return fallback;
};

export const useTimeline = (timelineId: number) => {
  const { token } = useAuth();
  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTimeline = useCallback(async () => {
    if (!token || !timelineId) return;

    try {
      setIsLoading(true);
      const data = await TimelineService.getTimeline(timelineId);
      setTimeline(data);
      setError(null);
    } catch (err: unknown) {
      const msg = getErrorMessage(err, "Failed to create node");
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [token, timelineId]);

  useEffect(() => {
    void fetchTimeline();
  }, [fetchTimeline]);

  const createNode = async (data: TimelineNodeFormValues) => {
    if (!token) return;
    try {
      const payload = adaptNodeToCreateRequest(data, timelineId);
      await TimelineService.createNode(payload);
      await fetchTimeline();
      return true;
    } catch (err: unknown) {
      const msg = getErrorMessage(err, "Failed to create node");
      setError(msg);
      throw err;
    }
  };

  const updateNode = async (nodeId: number, data: TimelineNodeFormValues) => {
    if (!token) return;
    try {
      const payload = adaptNodeToUpdateRequest(data);
      await TimelineService.updateNode(nodeId, payload);
      await fetchTimeline();
      return true;
    } catch (err: unknown) {
      const msg = getErrorMessage(err, "Failed to create node");
      setError(msg);
      throw err;
    }
  };

  const deleteNode = async (nodeId: number) => {
    if (!token) return;
    try {
      await TimelineService.deleteNode(nodeId);
      await fetchTimeline();
      return true;
    } catch (err: unknown) {
      const msg = getErrorMessage(err, "Failed to create node");
      setError(msg);
      throw err;
    }
  };

  return {
    timeline,
    nodes: timeline?.nodes || [],
    isLoading,
    error,
    refresh: fetchTimeline,
    createNode,
    updateNode,
    deleteNode,
  };
};
