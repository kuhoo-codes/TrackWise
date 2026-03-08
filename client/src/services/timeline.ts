import { handleServiceError } from "@/lib/error";
import {
  adaptTimelineSummary,
  adaptTimeline,
  adaptTimelineNode,
  adaptTimelineCreateRequest,
} from "@/services/adapters";
import { api } from "@/services/api";
import type {
  ApiTimelineNodeCreateRequest,
  ApiTimelineNodeUpdateRequest,
} from "@/services/apiTypes";
import {
  type TimelineSummary,
  type Timeline,
  type TimelineNode,
  type TimelineCreateRequest,
} from "@/services/types";

export class TimelineService {
  static async getTimelines(): Promise<TimelineSummary[]> {
    try {
      const response = await api.get("/timelines/", {});
      return response.data.map(adaptTimelineSummary);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async getTimeline(timelineId: number): Promise<Timeline> {
    try {
      const response = await api.get(`/timelines/${timelineId}`, {});
      return adaptTimeline(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async createTimeline(data: TimelineCreateRequest): Promise<Timeline> {
    const payload = adaptTimelineCreateRequest(data);
    try {
      const response = await api.post("/timelines", payload, {});

      return adaptTimeline(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async deleteTimeline(timelineId: number): Promise<void> {
    try {
      await api.delete(`/timelines/${timelineId}`, {});
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async createNode(
    data: ApiTimelineNodeCreateRequest,
    media: File | null,
  ): Promise<TimelineNode> {
    try {
      const formData = new FormData();
      formData.append("timeline_node", JSON.stringify(data));
      if (media) {
        formData.append("media", media);
      }
      const response = await api.post("/timelines/node", formData, {});
      return adaptTimelineNode(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async updateNode(
    nodeId: number,
    data: ApiTimelineNodeUpdateRequest,
    media: File | null,
  ): Promise<TimelineNode> {
    try {
      const formData = new FormData();
      formData.append("timeline_node", JSON.stringify(data));
      if (media) {
        formData.append("media", media);
      }
      const response = await api.patch(
        `/timelines/node/${nodeId}`,
        formData,
        {},
      );
      return adaptTimelineNode(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async deleteNode(nodeId: number): Promise<void> {
    try {
      await api.delete(`/timelines/node/${nodeId}`, {});
    } catch (error) {
      throw handleServiceError(error);
    }
  }
}
