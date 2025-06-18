import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { ROUTES } from "../../../app/router/routes";
import type { SignupRequest } from "../../../services/auth";
import { useAuth } from "../../../shared/hooks/useAuth";
import { AuthForm } from "../components/authForm";
import { AuthSidePanel } from "./authSidePanel";

export const Signup: React.FC = () => {
  const { signup, isLoading, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSignup = async (data: SignupRequest) => {
    try {
      clearError();

      await signup(data);

      const from = location.state?.from?.pathname || ROUTES.DASHBOARD;
      void navigate(from, { replace: true });
    } catch (error) {
      console.error("Signup error:", error);
    }
  };

  return (
    <div className="w-full min-h-screen flex flex-col lg:flex-row">
      {/* Left side - Form (centered) */}
      <div className="w-full lg:w-1/2 bg-gray-100 flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-md">
          <AuthForm mode="signup" onSubmit={handleSignup} loading={isLoading} />
        </div>
      </div>

      <AuthSidePanel />
    </div>
  );
};
