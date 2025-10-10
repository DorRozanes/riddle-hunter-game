import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // Keep the JWT in memory + persist in localStorage
  const [accessToken, setAccessToken] = useState(() =>
    localStorage.getItem("accessToken")
  );

  // Called by <Login /> after successful authentication
  const login = (token) => {
    localStorage.setItem("accessToken", token);
    setAccessToken(token);
  };

  // Logout clears everything
  const logout = () => {
    localStorage.removeItem("accessToken");
    setAccessToken(null);
  };

  // On startup, reload token from localStorage if available
  useEffect(() => {
    const saved = localStorage.getItem("accessToken");
    if (saved) setAccessToken(saved);
  }, []);

  return (
    <AuthContext.Provider value={{ accessToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
