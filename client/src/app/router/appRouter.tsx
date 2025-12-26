import React from "react";
import { Routes, Route, Navigate, Link } from "react-router-dom";
import { Login, Signup } from "@/features/auth";
import { Dashboard } from "@/features/dashboard";
import { Layout } from "@/shared/components/layout/layout";
import { ProtectedRoute } from "./protectedRoute";
import { ROUTES } from "./routes";

export const AppRouter: React.FC = () => (
  <Routes>
    {/* Public Routes - No Layout */}
    <Route
      path={ROUTES.LOGIN}
      element={
        <ProtectedRoute requireAuth={false}>
          <Layout>
            <Login />
          </Layout>
        </ProtectedRoute>
      }
    />
    <Route
      path={ROUTES.SIGNUP}
      element={
        <ProtectedRoute requireAuth={false}>
          <Layout>
            <Signup />
          </Layout>
        </ProtectedRoute>
      }
    />

    {/* Protected Routes - With Layout */}
    <Route
      path={ROUTES.DASHBOARD}
      element={
        <ProtectedRoute requireAuth>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      }
    />

    {/* Root redirect */}
    <Route
      path={ROUTES.HOME}
      element={<Navigate to={ROUTES.DASHBOARD} replace />}
    />

    {/* Catch all - 404 */}
    <Route
      path="*"
      element={
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
            <p className="text-gray-600 mb-4">Page not found</p>
            <Link
              to={ROUTES.DASHBOARD}
              className="text-blue-600 hover:underline"
            >
              Go to Dashboard
            </Link>
          </div>
        </div>
      }
    />
  </Routes>
);
