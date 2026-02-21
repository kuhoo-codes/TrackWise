import { useState, useEffect, useCallback } from "react";
import { toast } from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import { getErrorMessage } from "@/lib/error";
import { GithubService } from "@/services/github";

export const useGithubConnect = () => {
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (localStorage.getItem("github_connected") === "true") {
      setIsConnected(true);
    }
  }, []);

  const redirectToGithub = useCallback(async () => {
    setIsRedirecting(true);

    try {
      const redirectUrl = await GithubService.getAuthUrl();
      window.location.href = redirectUrl;
    } catch (err: unknown) {
      toast.error(getErrorMessage(err, "Failed to initiate GitHub login."));
      setIsRedirecting(false);
    }
  }, []);

  const processCallback = useCallback(
    async (code: string, state: string) => {
      try {
        await GithubService.handleCallback(code, state);
        localStorage.setItem("github_connected", "true");
        toast.success("Connected to GitHub!");
      } catch (err: unknown) {
        const errorMsg = getErrorMessage(
          err,
          "Failed to verify GitHub connection.",
        );
        toast.error(errorMsg);
      } finally {
        void navigate(ROUTES.DASHBOARD, { replace: true });
      }
    },
    [navigate],
  );

  const handleMissingParams = useCallback(() => {
    toast.error("Invalid response from GitHub.");
    void navigate(ROUTES.DASHBOARD, { replace: true });
  }, [navigate]);

  return {
    isConnected,
    isRedirecting,
    redirectToGithub,
    processCallback,
    handleMissingParams,
  };
};
