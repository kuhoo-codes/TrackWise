import Axios, { type AxiosError } from "axios";
import { adaptAuthResponse, adaptUser } from "@/services/adapters";
import { api } from "@/services/api";
import type {
  User,
  LoginRequest,
  AuthResponse,
  SignupRequest,
  APIError,
} from "@/services/types";
import { APIErrorSchema } from "@/services/types";

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
      return adaptAuthResponse(response.data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async signup(userData: SignupRequest): Promise<AuthResponse> {
    try {
      const response = await api.post("/auth/signup", userData);
      return adaptAuthResponse(response.data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async logout(): Promise<void> {
    try {
      await api.delete("/auth/logout", {});
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async validateToken(): Promise<User> {
    try {
      const response = await api.get("/auth/me", {});
      return adaptUser(response.data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async refreshToken(): Promise<AuthResponse> {
    const response = await api.post("/auth/refresh");
    return adaptAuthResponse(response.data);
  }
}
