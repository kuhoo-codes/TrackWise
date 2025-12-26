import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import { AuthForm } from "@/features/auth/components/authForm";
import { AuthSidePanel } from "@/features/auth/pages/authSidePanel";
import type { SignupRequest } from "@/services/auth";
import { useAuth } from "@/shared/hooks/useAuth";

export const Signup: React.FC = () => {
  const { signup, isLoading, clearError, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSignup = async (data: SignupRequest) => {
    clearError();

    await signup(data);

    const from = location.state?.from?.pathname || ROUTES.DASHBOARD;
    void navigate(from, { replace: true });
  };

  return (
    <div className="w-full min-h-screen flex flex-col lg:flex-row">
      {/* Left side - Form (centered) */}
      <div className="w-full lg:w-1/2 bg-gray-100 flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-md">
          {error && (
            <span className="text-red-500 mb-4 block">{error.message}</span>
          )}
          <AuthForm mode="signup" onSubmit={handleSignup} loading={isLoading} />
        </div>
      </div>

      <AuthSidePanel />
    </div>
  );
};
