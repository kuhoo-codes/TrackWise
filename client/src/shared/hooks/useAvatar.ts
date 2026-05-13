// src/shared/hooks/useAvatar.ts

import { useState, useEffect, useCallback } from "react";
import { AuthService } from "@/services/auth";
import { useAuth } from "./useAuth";

export const useAvatar = () => {
  const { user, refreshUser } = useAuth();

  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (!user?.hasAvatar) {
      setAvatarUrl(null);
      return;
    }

    let objectUrl: string | null = null;

    const fetchAvatar = async () => {
      setIsLoading(true);
      try {
        const blob = await AuthService.getAvatarBlob();
        objectUrl = URL.createObjectURL(blob);
        setAvatarUrl(objectUrl);
      } catch (error) {
        console.error("Failed to fetch avatar:", error);
        setAvatarUrl(null);
      } finally {
        setIsLoading(false);
      }
    };

    void fetchAvatar();

    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [user?.hasAvatar, user?.updatedAt]);

  const uploadAvatar = useCallback(
    async (file: File) => {
      setIsProcessing(true);
      try {
        const updatedUser = await AuthService.uploadAvatar(file);
        refreshUser(updatedUser);
      } finally {
        setIsProcessing(false);
      }
    },
    [refreshUser],
  );

  const removeAvatar = useCallback(async () => {
    setIsProcessing(true);
    try {
      const updatedUser = await AuthService.removeAvatar();
      refreshUser(updatedUser);
    } finally {
      setIsProcessing(false);
    }
  }, [refreshUser]);

  return {
    avatarUrl,
    isLoading,
    isProcessing,
    uploadAvatar,
    removeAvatar,
  };
};
