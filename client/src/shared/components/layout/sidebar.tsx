import { LayoutDashboard, Settings, Zap } from "lucide-react";
import React from "react";
import { NavLink } from "react-router-dom";
import { ROUTES } from "@/app/router/routes";
import { GithubInvertocat } from "@/shared/components/ui/asset/githubLogo";

const navItems = [
  { name: "Dashboard", href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { name: "Integrations", href: "/integrations", icon: GithubInvertocat },
  { name: "Settings", href: "/settings", icon: Settings },
];

export const Sidebar: React.FC = () => (
  <aside className="w-64 flex flex-col h-screen bg-sidebar border-r border-border/60">
    {/* Top: Brand/Logo */}
    <div className="p-6 flex items-center gap-3">
      <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
        <Zap className="text-white w-5 h-5" fill="currentColor" />
      </div>
      <span className="font-bold text-lg tracking-tight">TrackWise</span>
    </div>

    {/* Middle: Navigation */}
    <nav className="flex-1 px-4 space-y-1 mt-2">
      {navItems.map((item) => (
        <NavLink
          key={item.name}
          to={item.href}
          className={({ isActive }) => `
              flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-all
              ${
                isActive
                  ? "bg-secondary text-primary shadow-sm ring-1 ring-border"
                  : "text-muted-foreground hover:bg-secondary/50 hover:text-primary"
              }
            `}
        >
          <item.icon className="w-4 h-4" />
          {item.name}
        </NavLink>
      ))}
    </nav>
  </aside>
);
