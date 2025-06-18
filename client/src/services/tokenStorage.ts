const TOKEN_KEY = "authToken";
const REFRESH_TOKEN_KEY = "refreshToken";

export class TokenStorage {
  static getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  static setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  static setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }

  static removeTokens(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  static hasToken(): boolean {
    return !!this.getToken();
  }
}
