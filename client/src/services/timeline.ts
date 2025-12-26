import Axios, { type AxiosError } from "axios";
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
  APIErrorSchema,
  type TimelineSummary,
  type Timeline,
  type TimelineNode,
  type TimelineCreateRequest,
  type APIError,
} from "@/services/types";

export class TimelineService {
  private static handleError(error: unknown): APIError {
    if (Axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      const errorData = axiosError.response?.data;

      if (
        typeof errorData === "object" &&
        errorData !== null &&
        "error" in errorData
      ) {
        const parsed = APIErrorSchema.safeParse(errorData.error);
        if (parsed.success) return parsed.data;
      }

      if (typeof errorData === "object" && errorData !== null) {
        const parsed = APIErrorSchema.safeParse(errorData);
        if (parsed.success) return parsed.data;
      }

      return {
        code: axiosError.code || "AXIOS_ERROR",
        message: axiosError.message || "An unknown Axios error occurred",
      };
    }

    if (error instanceof Error) {
      return {
        code: "GENERIC_ERROR",
        message: error.message,
      };
    }

    return {
      code: "UNKNOWN_ERROR",
      message: "An unknown error occurred",
    };
  }

  static async getTimelines(): Promise<TimelineSummary[]> {
    try {
      const response = await api.get("/timelines/", {});
      return response.data.map(adaptTimelineSummary);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async getTimeline(timelineId: number): Promise<Timeline> {
    try {
      const response = await api.get(`/timelines/${timelineId}`, {});
      return adaptTimeline(response.data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async createTimeline(data: TimelineCreateRequest): Promise<Timeline> {
    const payload = adaptTimelineCreateRequest(data);
    try {
      const response = await api.post("/timelines", payload, {});

      return adaptTimeline(response.data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async deleteTimeline(timelineId: number): Promise<void> {
    try {
      await api.delete(`/timelines/${timelineId}`, {});
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async createNode(
    data: ApiTimelineNodeCreateRequest,
  ): Promise<TimelineNode> {
    try {
      const response = await api.post("/timelines/node", data, {});
      return adaptTimelineNode(response.data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async updateNode(
    nodeId: number,
    data: ApiTimelineNodeUpdateRequest,
  ): Promise<TimelineNode> {
    try {
      const response = await api.patch(`/timelines/node/${nodeId}`, data, {});
      return adaptTimelineNode(response.data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async deleteNode(nodeId: number): Promise<void> {
    try {
      await api.delete(`/timelines/node/${nodeId}`, {});
    } catch (error) {
      throw this.handleError(error);
    }
  }
}
