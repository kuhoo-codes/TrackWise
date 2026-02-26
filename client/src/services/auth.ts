import { handleServiceError } from "@/lib/error";
import { adaptAuthResponse, adaptUser } from "@/services/adapters";
import { api } from "@/services/api";
import type {
  User,
  LoginRequest,
  AuthResponse,
  SignupRequest,
} from "@/services/types";

export class AuthService {
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await api.post("/auth/login", credentials);
      return adaptAuthResponse(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async signup(userData: SignupRequest): Promise<AuthResponse> {
    try {
      const response = await api.post("/auth/signup", userData);
      return adaptAuthResponse(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async logout(): Promise<void> {
    try {
      await api.delete("/auth/logout", {});
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async validateToken(): Promise<User> {
    try {
      const response = await api.get("/auth/me", {});
      return adaptUser(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async refreshToken(): Promise<AuthResponse> {
    try {
      const response = await api.post("/auth/refresh");
      return adaptAuthResponse(response.data);
    } catch (error) {
      throw handleServiceError(error);
    }
  }
}
