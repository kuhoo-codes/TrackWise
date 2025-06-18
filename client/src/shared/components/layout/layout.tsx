import React from "react";
import { Navbar } from "./navbar";

interface LayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => (
  <div className="w-full min-h-screen bg-gray-50">
    <Navbar />
    <div className="flex-1 flex">{children}</div>
  </div>
);
