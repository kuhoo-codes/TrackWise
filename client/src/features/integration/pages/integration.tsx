import { ExternalLink, RefreshCw, AlertCircle } from "lucide-react";
import React from "react";
import { SYNC_STATUS } from "@/services/types";
import { GithubInvertocat } from "@/shared/components/ui/asset/githubLogo";
import { useGithubConnect } from "@/shared/hooks/useGithubConnect";

export const Integrations: React.FC = () => {
  const {
    isConnected,
    syncStatus,
    lastSyncedAt,
    triggerSync,
    redirectToGithub,
  } = useGithubConnect();

  return (
    <div className="p-10 max-w-4xl mx-auto">
      <header className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
        <p className="text-muted-foreground mt-2">
          Connect and manage the data sources for your portfolio timelines.
        </p>
      </header>

      <div className="grid gap-6">
        {/* GitHub Card */}
        <div className="group border border-border bg-white rounded-xl p-6 transition-all hover:shadow-subtle">
          <div className="flex items-start justify-between">
            <div className="flex gap-4">
              <div className="w-12 h-12 rounded-lg bg-gray-900 flex items-center justify-center text-white">
                <GithubInvertocat className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-lg">GitHub</h3>
                <p className="text-sm text-muted-foreground">
                  Analyze pull requests, commits, and open-source contributions.
                </p>

                {isConnected && (
                  <div className="mt-4 flex items-center gap-4 text-xs">
                    <span className="flex items-center gap-1.5 text-green-600 font-medium">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-600" />
                      Connected
                    </span>
                    <span className="text-muted-foreground">
                      Last synced:{" "}
                      {lastSyncedAt
                        ? new Date(lastSyncedAt).toLocaleDateString()
                        : "Never"}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {!isConnected ? (
              <button
                onClick={() => void redirectToGithub()}
                className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-all"
              >
                Connect Account
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={() => void triggerSync()}
                  disabled={syncStatus === SYNC_STATUS.SYNCING}
                  className="p-2 border border-border rounded-lg hover:bg-secondary transition-colors disabled:opacity-50"
                  title="Sync Data"
                >
                  <RefreshCw
                    className={`w-4 h-4 ${syncStatus === SYNC_STATUS.SYNCING ? "animate-spin" : ""}`}
                  />
                </button>
                <button className="text-xs text-red-500 hover:underline px-2">
                  Disconnect
                </button>
              </div>
            )}
          </div>

          {syncStatus === SYNC_STATUS.FAILED && (
            <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg flex items-center gap-2 text-xs text-red-700">
              <AlertCircle className="w-4 h-4" />
              There was an error syncing your latest data. Please try
              re-connecting.
            </div>
          )}
        </div>

        {/* Placeholder for future integrations */}
        <div className="border border-dashed border-border rounded-xl p-6 opacity-60">
          <div className="flex items-center justify-between">
            <div className="flex gap-4">
              <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400">
                <ExternalLink className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-lg text-gray-400">LinkedIn</h3>
                <p className="text-sm text-muted-foreground">
                  Coming soon: Import work history and endorsements.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
