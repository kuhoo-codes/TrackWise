import { api } from "./api";
import type { GithubAuthUrlResponse } from "./types";

export class GithubService {
  static async getAuthUrl(): Promise<string> {
    const response = await api.get<GithubAuthUrlResponse>(
      "/integrations/github/auth-url",
    );
    return response.data.authUrl;
  }

  static async handleCallback(code: string, state: string): Promise<void> {
    await api.get(`/integrations/github/callback?code=${code}&state=${state}`);
  }
}
