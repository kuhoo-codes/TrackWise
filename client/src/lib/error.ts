import { AxiosError } from "axios";

export const getErrorMessage = (err: unknown, fallback: string): string => {
  if (err instanceof AxiosError && err.response?.data?.error?.message) {
    return String(err.response.data.error.message);
  }
  if (err instanceof AxiosError && err.message) {
    return err.message;
  }
  if (err instanceof Error) {
    return err.message;
  }
  if (typeof err === "object" && err !== null && "message" in err) {
    return String((err as { message: unknown }).message);
  }
  return fallback;
};
