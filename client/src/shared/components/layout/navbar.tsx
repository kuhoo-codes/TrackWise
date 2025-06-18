import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { ButtonComponent } from "../ui/button/button";

export const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const redirectToLogin = () => {
    void navigate("/login");
  };
  const redirectToSignup = () => {
    void navigate("/signup");
  };

  return (
    <nav className="bg-white border-b border-gray-200 fixed w-full top-0 z-50 relative">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-blue-600">TrackWise</h1>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {user?.name?.charAt(0)?.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {user?.name}
                  </span>
                </div>
                <ButtonComponent variant="secondary" size="sm" onClick={logout}>
                  Logout
                </ButtonComponent>
              </>
            ) : (
              <div className="flex items-center space-x-2">
                <ButtonComponent
                  variant="secondary"
                  size="sm"
                  onClick={redirectToLogin}
                >
                  Login
                </ButtonComponent>
                <ButtonComponent
                  variant="primary"
                  size="sm"
                  onClick={redirectToSignup}
                >
                  Sign Up
                </ButtonComponent>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
