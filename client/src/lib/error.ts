import Axios from "axios";
import { APIErrorSchema, type APIError } from "@/services/types";

export const handleServiceError = (error: unknown): APIError => {
  if (Axios.isAxiosError(error)) {
    const errorData = error.response?.data;

    if (
      typeof errorData === "object" &&
      errorData !== null &&
      "error" in errorData
    ) {
      const parsed = APIErrorSchema.safeParse(errorData.error);
      if (parsed.success) return parsed.data;
    }

    if (typeof errorData === "object" && errorData !== null) {
      const parsed = APIErrorSchema.safeParse(errorData);
      if (parsed.success) return parsed.data;
    }

    return {
      code: error.code || "AXIOS_ERROR",
      message: error.message || "An unknown network error occurred",
    };
  }

  if (error instanceof Error) {
    return {
      code: "GENERIC_ERROR",
      message: error.message,
    };
  }

  return {
    code: "UNKNOWN_ERROR",
    message: "An unexpected error occurred",
  };
};

export const getErrorMessage = (err: unknown, fallback: string): string => {
  const standardized = handleServiceError(err);
  return standardized.message || fallback;
};
