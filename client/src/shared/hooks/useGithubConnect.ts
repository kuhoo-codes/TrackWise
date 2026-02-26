import { useState, useEffect, useCallback, useRef } from "react";
import { toast } from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import { getErrorMessage } from "@/lib/error";
import { GithubService } from "@/services/github";
import { SYNC_STATUS, type SyncStatus } from "@/services/types";

export const useGithubConnect = () => {
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(SYNC_STATUS.IDLE);
  const [lastSyncedAt, setLastSyncedAt] = useState<Date | null>(null);
  const pollingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const navigate = useNavigate();

  const fetchStatus = useCallback(async (isPolling = false) => {
    try {
      const data = await GithubService.getSyncStatus();

      setIsConnected(data.isConnected);
      setSyncStatus(data.syncStatus);
      setLastSyncedAt(data.lastSyncedAt);

      // ONLY show toasts if we are actively waiting for a sync to finish
      if (isPolling) {
        if (data.syncStatus === SYNC_STATUS.FAILED) {
          toast.error(`Sync Failed: ${data.lastSyncError || "Unknown error"}`);
        } else if (data.syncStatus === SYNC_STATUS.COMPLETED) {
          toast.success("GitHub sync completed successfully!");
        }
      }

      return data.syncStatus;
    } catch (err: unknown) {
      console.error("Failed to fetch GitHub status", err);
      return null;
    }
  }, []);

  const startPolling = useCallback(() => {
    if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);

    pollingTimerRef.current = setInterval(() => {
      void fetchStatus(true).then((status) => {
        if (status !== SYNC_STATUS.SYNCING && pollingTimerRef.current) {
          clearInterval(pollingTimerRef.current);
        }
      });
    }, 5000);
  }, [fetchStatus]);

  useEffect(() => {
    void fetchStatus(false).then((status) => {
      if (status === SYNC_STATUS.SYNCING) startPolling();
    });
  }, [fetchStatus, startPolling]);

  useEffect(
    () => () => {
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    },
    [],
  );

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

  const triggerSync = useCallback(async () => {
    try {
      setSyncStatus(SYNC_STATUS.SYNCING);
      await GithubService.startSync();
      toast.success("GitHub sync started in the background.");
      startPolling();
    } catch (err: unknown) {
      setSyncStatus(SYNC_STATUS.FAILED);

      const errorMessage = getErrorMessage(
        err,
        "Failed to start GitHub synchronization.",
      );
      toast.error(errorMessage);
    }
  }, [startPolling]);

  const handleMissingParams = useCallback(() => {
    toast.error("Invalid response from GitHub.");
    void navigate(ROUTES.DASHBOARD, { replace: true });
  }, [navigate]);

  return {
    isConnected,
    isRedirecting,
    syncStatus,
    redirectToGithub,
    lastSyncedAt,
    processCallback,
    handleMissingParams,
    triggerSync,
  };
};
