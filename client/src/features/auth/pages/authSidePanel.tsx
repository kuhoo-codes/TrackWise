import React from "react";

export const AuthSidePanel: React.FC = () => (
  <div className="w-1/2 h-screen hidden lg:block">
    <img
      src="https://placehold.co/800x/667fff/ffffff.png?text=Welcome&font=Montserrat"
      alt="Auth Panel"
      className="object-contain w-full h-full rounded-lg"
    />
  </div>
);
