import Axios from "axios";
import { API_BASE_URL } from "@/services/config";

export const api = Axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});
