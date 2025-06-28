import Axios, { type AxiosError } from "axios";
import { z } from "zod";
import { api } from "./api";

export interface User {
  id: string;
  name: string;
  email: string;
  lastLogin: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest extends LoginRequest {
  name: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  tokenType: string;
}

const APIErrorSchema = z.object({
  code: z.string(),
  message: z.string(),
  timestamp: z.coerce.date().optional(),
  details: z.record(z.any()).optional(),
});

export type APIError = z.infer<typeof APIErrorSchema>;

export class AuthService {
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

  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await api.post("/auth/login", credentials);
      const data = response.data;
      const authData: AuthResponse = {
        user: data.user,
        accessToken: data.access_token,
        tokenType: data.token_type,
      };
      return authData;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async signup(userData: SignupRequest): Promise<AuthResponse> {
    try {
      const response = await api.post("/auth/signup", userData);
      const data = response.data;
      const authData: AuthResponse = {
        user: data.user,
        accessToken: data.access_token,
        tokenType: data.token_type,
      };
      return authData;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async validateToken(token: string): Promise<User> {
    try {
      const response = await api.get<User>("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async refreshToken(): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/refresh");
    return response.data;
  }
}
