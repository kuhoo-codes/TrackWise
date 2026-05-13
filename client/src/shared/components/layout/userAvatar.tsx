// src/shared/components/ui/UserAvatar.tsx

import { User as UserIcon, Loader2 } from "lucide-react";
import React from "react";
import { useAuth } from "@/shared/hooks/useAuth";
import { useAvatar } from "@/shared/hooks/useAvatar";

interface UserAvatarProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

export const UserAvatar: React.FC<UserAvatarProps> = ({
  className,
  size = "md",
}) => {
  const { user } = useAuth();
  const { avatarUrl, isLoading } = useAvatar();

  if (!user) return <UserIcon className="w-4 h-4" />;

  const initials = user.name.substring(0, 2).toUpperCase();

  const sizeClasses = {
    sm: "h-8 w-8 text-[10px]",
    md: "h-12 w-12 text-sm",
    lg: "h-20 w-20 text-xl",
  };

  return (
    <div
      className={`
        ${sizeClasses[size]} 
        rounded-full flex items-center justify-center 
        bg-primary font-bold text-white uppercase tracking-tighter shadow-sm overflow-hidden
        relative ${className}
      `}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin opacity-50" />
      ) : user.hasAvatar && avatarUrl ? (
        <img
          src={avatarUrl}
          alt={user.name}
          className="h-full w-full object-cover"
        />
      ) : (
        <span>{initials}</span>
      )}
    </div>
  );
};
