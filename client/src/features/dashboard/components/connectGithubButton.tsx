import { AlertTriangle, RefreshCw } from "lucide-react";
import React from "react";
import { SYNC_STATUS } from "@/services/types";
import { GithubInvertocat } from "@/shared/components/ui/asset/githubLogo";
import { useGithubConnect } from "@/shared/hooks/useGithubConnect";

export const ConnectGithubButton: React.FC = () => {
  const {
    isConnected,
    isRedirecting,
    redirectToGithub,
    syncStatus,
    triggerSync,
  } = useGithubConnect();

  if (!isConnected) {
    return (
      <button
        onClick={() => void redirectToGithub()}
        disabled={isRedirecting}
        className="flex items-center gap-2 px-3 py-2 border border-border rounded-lg hover:bg-secondary/50 transition-all text-sm font-medium text-muted-foreground hover:text-primary"
      >
        <GithubInvertocat className="w-4 h-4" />
        <span>{isRedirecting ? "Connecting..." : "Connect GitHub"}</span>
      </button>
    );
  }

  return (
    <button
      onClick={() => void triggerSync()}
      disabled={syncStatus === SYNC_STATUS.SYNCING}
      className={`p-2 rounded-lg border transition-all ${
        syncStatus === SYNC_STATUS.FAILED
          ? "border-red-200 text-red-600 bg-red-50"
          : "border-border text-muted-foreground hover:text-primary hover:bg-secondary/50"
      }`}
      title={
        syncStatus === SYNC_STATUS.FAILED
          ? "Sync Failed - Click to retry"
          : "Sync Repositories"
      }
    >
      {syncStatus === SYNC_STATUS.SYNCING ? (
        <RefreshCw className="w-4 h-4 animate-spin text-accent-blue" />
      ) : syncStatus === SYNC_STATUS.FAILED ? (
        <AlertTriangle className="w-4 h-4" />
      ) : (
        <RefreshCw className="w-4 h-4" />
      )}
    </button>
  );
};
