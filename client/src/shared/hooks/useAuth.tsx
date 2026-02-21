import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import { getErrorMessage } from "@/lib/error";
import { AuthService } from "@/services/auth";
import { TokenStorage } from "@/services/tokenStorage";
import {
  type User,
  type LoginRequest,
  type SignupRequest,
} from "@/services/types";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  errorMessage: string | null;
}
interface AuthContextType extends AuthState {
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  signup: (userData: SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  resetAuthState: () => void;
  token?: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    errorMessage: null,
  });

  const resetAuthState = () => {
    setState({
      user: null,
      isLoading: false,
      errorMessage: null,
    });
  };

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = TokenStorage.getToken();
        if (token) {
          const userData = await AuthService.validateToken();
          setState((prev) => ({ ...prev, user: userData }));
        } else {
          resetAuthState();
          return;
        }
      } catch (error) {
        setState((prev) => ({
          ...prev,
          errorMessage: getErrorMessage(error, "Failed to validate session"),
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
        errorMessage: null,
      });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        errorMessage: getErrorMessage(error, "Failed to login"),
        isLoading: false,
      }));
      throw error;
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
        errorMessage: null,
      });
    } catch (error) {
      setState((prev) => ({
        ...prev,
        errorMessage: getErrorMessage(error, "Failed to sign up"),
        isLoading: false,
      }));
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      const token = TokenStorage.getToken();
      if (token) {
        await AuthService.logout();
      }

      TokenStorage.removeTokens();
      resetAuthState();
    } catch (error) {
      const normalizedError = getErrorMessage(error, "Failed to logout");
      throw normalizedError;
    }
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
    errorMessage: state.errorMessage,
    login,
    signup,
    logout,
    clearError,
    resetAuthState,
    token: state.user ? TokenStorage.getToken() : null,
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
