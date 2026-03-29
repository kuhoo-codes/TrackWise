import {
  ChevronRight,
  User,
  LogOut,
  Settings,
  ExternalLink,
} from "lucide-react";
import React, { useState, useRef, useEffect } from "react";
import { Outlet, useLocation, Link } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import { useAuth } from "@/shared/hooks/useAuth";
import { useGithubConnect } from "@/shared/hooks/useGithubConnect";
import { Sidebar } from "./sidebar";

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const { isConnected } = useGithubConnect();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const pathname = location.pathname.split("/").filter(Boolean);
  const currentPage = pathname[0]
    ? pathname[0].charAt(0).toUpperCase() + pathname[0].slice(1)
    : "Dashboard";

  return (
    <div className="flex h-screen w-full overflow-hidden bg-canvas">
      <Sidebar />

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <header className="h-14 flex items-center justify-between px-8 bg-white/80 backdrop-blur-md border-b border-border/60 sticky top-0 z-50">
          <div className="flex items-center gap-2 text-sm">
            <Link
              to={ROUTES.DASHBOARD}
              className="text-muted-foreground hover:text-primary transition-colors"
            >
              TrackWise
            </Link>
            <ChevronRight className="w-4 h-4 text-border" />
            <span className="font-medium text-primary">{currentPage}</span>
          </div>

          <div className="flex items-center gap-4 relative" ref={menuRef}>
            <div id="top-bar-actions" className="flex items-center gap-2" />

            <div className="h-4 w-px bg-border/60 mx-1" />

            {/* Avatar Button */}
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center gap-2 p-0.5 rounded-full hover:bg-secondary transition-all"
            >
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-[10px] font-bold text-white uppercase tracking-tighter shadow-sm">
                {user?.name?.substring(0, 2) || <User className="w-4 h-4" />}
              </div>
            </button>

            {/* Premium Dropdown Menu */}
            {isUserMenuOpen && (
              <div className="absolute right-0 top-10 mt-2 w-56 bg-white border border-border rounded-xl shadow-lg z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
                <div className="p-3 border-b border-border/40 bg-canvas/50">
                  <p className="text-sm font-semibold truncate">
                    {user?.name || "Developer"}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {user?.email || "user@example.com"}
                  </p>
                </div>

                <div className="p-1.5">
                  <Link
                    to="/settings"
                    onClick={() => setIsUserMenuOpen(false)}
                    className="flex items-center gap-3 px-3 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-secondary/50 rounded-lg transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                    Account Settings
                  </Link>
                  {isConnected && (
                    <a
                      href="https://github.com"
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-3 px-3 py-2 text-sm text-muted-foreground hover:text-primary hover:bg-secondary/50 rounded-lg transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      GitHub Profile
                    </a>
                  )}
                </div>

                <div className="p-1.5 border-t border-border/40">
                  <button
                    onClick={() => {
                      setIsUserMenuOpen(false);
                      void logout();
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto relative">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
