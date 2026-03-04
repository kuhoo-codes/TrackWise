import { handleServiceError } from "@/lib/error";
import { adaptGithubRepository, adaptGithubSyncStatus } from "./adapters";
import { api } from "./api";
import {
  type GithubAuthUrlResponse,
  type GithubSyncStatus,
  type GithubRepository,
} from "./types";

export class GithubService {
  static async getAuthUrl(): Promise<string> {
    try {
      const response = await api.get<GithubAuthUrlResponse>(
        "/integrations/github/auth-url",
      );
      return response.data.authUrl;
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async handleCallback(code: string, state: string): Promise<void> {
    try {
      await api.get(
        `/integrations/github/callback?code=${code}&state=${state}`,
      );
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async getSyncStatus(): Promise<GithubSyncStatus> {
    try {
      const response = await api.get(`/integrations/github/sync-status`);
      return adaptGithubSyncStatus(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async startSync(): Promise<void> {
    try {
      await api.get(`/integrations/github/sync`);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async getRepositories(): Promise<GithubRepository[]> {
    try {
      const response = await api.get(`/integrations/github/repositories`);
      return response.data.map(adaptGithubRepository);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async generateTimelines(repositoryIds: number[]): Promise<void> {
    try {
      await api.post(`/integrations/github/timelines`, repositoryIds);
    } catch (error) {
      throw handleServiceError(error);
    }
  }
}
