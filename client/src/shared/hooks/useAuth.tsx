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
  type APIError,
} from "../../services/auth";
import { TokenStorage } from "../../services/tokenStorage";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: APIError | null;
}
interface AuthContextType extends AuthState {
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  signup: (userData: SignupRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  resetAuthState: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    error: null,
  });

  const resetAuthState = () => {
    setState({
      user: null,
      isLoading: false,
      error: null,
    });
  };

  const handleError = (error: unknown): APIError => {
    if (isAPIError(error)) {
      return error;
    }
    return {
      code: "UNKNOWN_ERROR",
      message:
        error instanceof Error ? error.message : "An unknown error occurred",
    };
  };

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = TokenStorage.getToken();
        if (token) {
          const userData = await AuthService.validateToken(token);
          setState((prev) => ({ ...prev, user: userData }));
        } else {
          resetAuthState();
          return;
        }
      } catch (error) {
        setState((prev) => ({
          ...prev,
          error: handleError(error),
          user: null,
        }));
        TokenStorage.removeTokens();
      } finally {
        setState((prev) => ({ ...prev, isLoading: false }));
      }
    };

    void initializeAuth();
  }, []);

  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      const response = await AuthService.login(credentials);

      TokenStorage.setToken(response.accessToken);

      setState({
        user: response.user,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const normalizedError = handleError(error);
      setState((prev) => ({
        ...prev,
        error: normalizedError,
        isLoading: false,
      }));
      throw normalizedError;
    }
  };

  const signup = async (userData: SignupRequest): Promise<void> => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      const response = await AuthService.signup(userData);

      TokenStorage.setToken(response.accessToken);

      setState({
        user: response.user,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const normalizedError = handleError(error);
      setState((prev) => ({
        ...prev,
        error: normalizedError,
        isLoading: false,
      }));
      throw normalizedError;
    }
  };

  const logout = (): void => {
    TokenStorage.removeTokens();
    resetAuthState();
  };

  const clearError = (): void => {
    setState((prev) => ({
      ...prev,
      error: null,
    }));
  };

  const value: AuthContextType = {
    user: state.user,
    isAuthenticated: !!state.user,
    isLoading: state.isLoading,
    error: state.error,
    login,
    signup,
    logout,
    clearError,
    resetAuthState,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const isAPIError = (error: unknown): error is APIError =>
  typeof error === "object" &&
  error !== null &&
  "code" in error &&
  "message" in error &&
  typeof error.code === "string" &&
  typeof error.message === "string";

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
