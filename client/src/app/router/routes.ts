export const ROUTES = {
  // Public routes
  HOME: "/",
  LOGIN: "/login",
  SIGNUP: "/signup",

  // Protected routes
  DASHBOARD: "/dashboard",

  // Error routes
  NOT_FOUND: "/404",
  UNAUTHORIZED: "/unauthorized",
} as const;

export type RouteKey = keyof typeof ROUTES;
export type RoutePath = (typeof ROUTES)[RouteKey];
