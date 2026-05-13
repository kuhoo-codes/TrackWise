import { handleServiceError } from "@/lib/error";
import { adaptAuthResponse, adaptUser } from "@/services/adapters";
import { api } from "@/services/api";
import type {
  User,
  LoginRequest,
  AuthResponse,
  SignupRequest,
  UserUpdateRequest,
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

  static async updateUser(data: UserUpdateRequest): Promise<User> {
    try {
      const response = await api.patch("/auth/me", data);
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

  static async getAvatarBlob(): Promise<Blob> {
    try {
      const response = await api.get("/auth/me/avatar", {
        responseType: "blob",
      });
      return response.data;
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async uploadAvatar(file: File): Promise<User> {
    try {
      const formData = new FormData();
      formData.append("file", file);

      await api.patch("/auth/me/avatar", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // Return the fresh user object to sync state
      return await this.validateToken();
    } catch (error) {
      throw handleServiceError(error);
    }
  }

  static async removeAvatar(): Promise<User> {
    try {
      await api.delete("/auth/me/avatar");
      // Return fresh user object (hasAvatar will be false)
      return await this.validateToken();
    } catch (error) {
      throw handleServiceError(error);
    }
  }
}
