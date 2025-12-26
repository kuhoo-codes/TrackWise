import React from "react";
import { Routes, Route, Navigate, Link, useParams } from "react-router-dom";
import { Login, Signup } from "@/features/auth";
import { Dashboard } from "@/features/dashboard";
import { Timeline } from "@/features/timeline/pages/timeline";
import { Layout } from "@/shared/components/layout/layout";
import { ProtectedRoute } from "./protectedRoute";
import { ROUTES } from "./routes";

const TimelinePageWrapper: React.FC = () => {
  const { timelineId } = useParams<{ timelineId: string }>();
  if (!timelineId || isNaN(Number(timelineId))) {
    return <Navigate to={ROUTES.DASHBOARD} replace />;
  }

  return (
    <div className="h-[calc(100vh-64px)] w-full">
      <Timeline timelineId={Number(timelineId)} />
    </div>
  );
};

export const AppRouter: React.FC = () => (
  <Routes>
    {/* --- Public Routes --- */}
    <Route
      path={ROUTES.LOGIN}
      element={
        <Layout>
          <Login />
        </Layout>
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

    {/* --- Protected Routes --- */}

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

    <Route
      path={`${ROUTES.TIMELINE}/:timelineId`}
      element={
        <ProtectedRoute requireAuth>
          <Layout>
            <TimelinePageWrapper />
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
        <Layout>
          <div className="min-h-[50vh] flex items-center justify-center">
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
        </Layout>
      }
    />
  </Routes>
);
