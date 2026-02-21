import { Loader2 } from "lucide-react";
import React, { useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { useGithubConnect } from "@/shared/hooks/useGithubConnect";

export const GithubCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const hasCalledAPI = useRef(false);
  const { processCallback, handleMissingParams } = useGithubConnect();

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");

    if (!code || !state) {
      handleMissingParams();
      return;
    }

    // Prevent React 18 strict mode double-firing
    if (hasCalledAPI.current) return;
    hasCalledAPI.current = true;

    void processCallback(code, state);
  }, [searchParams, processCallback, handleMissingParams]);

  return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-gray-50">
      <Loader2 className="w-8 h-8 text-black animate-spin mb-4" />
      <p className="text-gray-600 font-medium">
        Finalizing GitHub connection...
      </p>
    </div>
  );
};
