import Axios from "axios";
import { API_BASE_URL } from "@/services/config";
import { TokenStorage } from "@/services/tokenStorage";

export const api = Axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = TokenStorage.getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  async (error) => Promise.reject(error),
);
