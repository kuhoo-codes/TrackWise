import React from "react";
import { Routes, Route, Navigate, Link, useParams } from "react-router-dom";
import { Login, Signup } from "@/features/auth";
import { Dashboard } from "@/features/dashboard";
import { GithubCallback } from "@/features/dashboard/pages/githubCallback";
import { Integrations } from "@/features/integration/pages/integration";
import { Timeline } from "@/features/timeline/pages/timeline";
import { AppLayout } from "@/shared/components/layout/appLayout";
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
    {/* --- PUBLIC ROUTES --- */}
    <Route
      path={ROUTES.LOGIN}
      element={
        <ProtectedRoute requireAuth={false}>
          <Login />
        </ProtectedRoute>
      }
    />
    <Route
      path={ROUTES.SIGNUP}
      element={
        <ProtectedRoute requireAuth={false}>
          <Signup />
        </ProtectedRoute>
      }
    />

    {/* --- AUTHENTICATED ROUTES (With Sidebar/TopBar) --- */}
    <Route
      element={
        <ProtectedRoute requireAuth>
          <AppLayout />
        </ProtectedRoute>
      }
    >
      <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
      <Route
        path={`${ROUTES.TIMELINE}/:timelineId`}
        element={<TimelinePageWrapper />}
      />
      <Route path={ROUTES.GITHUB_CALLBACK} element={<GithubCallback />} />

      <Route path="/integrations" element={<Integrations />} />
      <Route path="/settings" element={<div>Settings Page</div>} />
    </Route>

    {/* --- REDIRECTS --- */}
    <Route path="/" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
    <Route
      path="*"
      element={<div className="p-20 text-center">404: Not Found</div>}
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
