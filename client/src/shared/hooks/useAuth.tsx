import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import {
  AuthService,
  type User,
  type LoginRequest,
  type SignupRequest,
} from "../../services/auth";
import { TokenStorage } from "../../services/tokenStorage";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  signup: (userData: SignupRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = TokenStorage.getToken();
        if (token) {
          const userData = await AuthService.validateToken(token);
          setUser(userData);
        }
      } catch (error) {
        console.warn("Failed to validate token:", error);
        TokenStorage.removeTokens();
      } finally {
        setIsLoading(false);
      }
    };

    void initializeAuth();
  }, []);

  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await AuthService.login(credentials);

      TokenStorage.setToken(response.accessToken);

      setUser(response.user);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Login failed";
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData: SignupRequest): Promise<void> => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await AuthService.signup(userData);

      TokenStorage.setToken(response.accessToken);

      setUser(response.user);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Signup failed";
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    setIsLoading(true);
    TokenStorage.removeTokens();
    setUser(null);
    setError(null);
    setIsLoading(false);
  };

  const clearError = (): void => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    signup,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
