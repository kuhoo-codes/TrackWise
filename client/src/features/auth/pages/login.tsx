import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import type { LoginRequest } from "@/services/auth";
import { ROUTES } from "../../../app/router/routes";
import { useAuth } from "../../../shared/hooks/useAuth";
import { AuthForm } from "../components/authForm";
import { AuthSidePanel } from "./authSidePanel";

export const Login: React.FC = () => {
  const { login, isLoading, clearError, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = async (data: LoginRequest) => {
    clearError();

    await login(data);

    const from = location.state?.from?.pathname || ROUTES.DASHBOARD;
    void navigate(from, { replace: true });
  };

  return (
    <div className="w-full min-h-screen flex flex-col lg:flex-row">
      {/* Left side - Form (centered) */}
      <div className="w-full lg:w-1/2 bg-gray-100 flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-md space-y-4">
          {/* Display error message if exists */}
          {error && (
            <span className="text-red-500 mb-4 block">{error.message}</span>
          )}
          <AuthForm mode="login" onSubmit={handleLogin} loading={isLoading} />
        </div>
      </div>
      <AuthSidePanel />
    </div>
  );
};
