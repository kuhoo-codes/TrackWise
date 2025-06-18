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
  type: string;
}

export class AuthService {
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/login", credentials);
    return response.data;
  }

  static async signup(userData: SignupRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/signup", userData);
    return response.data;
  }

  static async validateToken(token: string): Promise<User> {
    const response = await api.get<User>("/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }

  static async refreshToken(): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/refresh");
    return response.data;
  }
}
