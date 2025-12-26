import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import { MINIMUM_PASSWORD_LENGTH } from "@/services/config";
import type { LoginRequest, SignupRequest } from "@/services/types";
import { ButtonComponent } from "@/shared/components/ui/button/button";
import { InputField } from "@/shared/components/ui/form/inputField";

interface AuthFormProps<T extends "login" | "signup"> {
  mode: T;
  onSubmit: (
    data: T extends "login" ? LoginRequest : SignupRequest,
  ) => Promise<void>;
  loading: boolean;
  error?: string | null;
  onClearError?: () => void;
}

export function AuthForm<T extends "login" | "signup">(
  props: AuthFormProps<T>,
): React.ReactElement {
  const { mode, onSubmit, loading, error, onClearError } = props;
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});

  useEffect(() => {
    if (error && onClearError) {
      const timeoutId = setTimeout(() => {
        onClearError();
      }, 5000);

      return () => clearTimeout(timeoutId);
    }
    return undefined;
  }, [error, onClearError]);

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    if (validationErrors[field]) {
      setValidationErrors((prev) => ({ ...prev, [field]: "" }));
    }

    if (error && onClearError) {
      onClearError();
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.email) {
      errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "Email is invalid";
    }

    if (!formData.password) {
      errors.password = "Password is required";
    } else if (formData.password.length < MINIMUM_PASSWORD_LENGTH) {
      errors.password = "Password must be at least 8 characters";
    }

    if (mode === "signup") {
      if (!formData.name) {
        errors.name = "Name is required";
      } else if (formData.name.length < 2) {
        errors.name = "Name must be at least 2 characters";
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      if (mode === "login") {
        const loginData: LoginRequest = {
          email: formData.email,
          password: formData.password,
        };
        await onSubmit(loginData as T extends "login" ? LoginRequest : never);
      } else {
        const signupData: SignupRequest = formData;
        await onSubmit(
          signupData as T extends "signup" ? SignupRequest : never,
        );
      }
    } catch (error) {
      console.error("Submission error:", error);
    }
  };

  const isLogin = mode === "login";
  const title = isLogin ? "Sign in to your account" : "Create your account";
  const buttonText = isLogin ? "Sign in" : "Sign up";
  const linkText = isLogin
    ? "Don't have an account?"
    : "Already have an account?";
  const linkAction = isLogin ? "Sign up" : "Sign in";
  const linkTo = isLogin ? ROUTES.SIGNUP : ROUTES.LOGIN;

  return (
    <div className="max-w-md w-full space-y-8">
      <div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {title}
        </h2>
      </div>

      <form className="mt-8 space-y-6" onSubmit={(e) => void handleSubmit(e)}>
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {mode === "signup" && (
            <InputField
              id="name"
              label="Full Name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange("name", e.target.value)}
              error={validationErrors.name}
              required
              disabled={loading}
            />
          )}

          <InputField
            id="email"
            label="Email Address"
            type="email"
            value={formData.email}
            onChange={(e) => handleInputChange("email", e.target.value)}
            error={validationErrors.email}
            required
            disabled={loading}
          />

          <InputField
            id="password"
            label="Password"
            type="password"
            value={formData.password}
            onChange={(e) => handleInputChange("password", e.target.value)}
            error={validationErrors.password}
            required
            disabled={loading}
          />
        </div>

        <div>
          <ButtonComponent
            variant="primary"
            size="lg"
            loading={loading}
            disabled={loading}
            className="w-full"
          >
            {buttonText}
          </ButtonComponent>
        </div>

        <div className="text-center">
          <span className="text-sm text-gray-600">
            {linkText}{" "}
            <Link
              to={linkTo}
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              {linkAction}
            </Link>
          </span>
        </div>
      </form>
    </div>
  );
}
