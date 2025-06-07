const getApiBaseUrl = () => {
  const apiBaseUrl = import.meta.env.VITE_API_URL;
  if (!apiBaseUrl) {
    throw new Error("VITE_API_URL is not defined in the environment variables");
  }
  return apiBaseUrl;
};

export const API_BASE_URL = getApiBaseUrl();
