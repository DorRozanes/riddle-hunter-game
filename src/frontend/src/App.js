// App.js
import React, { useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, AuthContext } from "./context/AuthContext";
import { LocationProvider } from "./context/LocationContext";
import Login from "./components/Login";
import Register from "./components/Register";
import AuthPage from "./components/AuthPage"
import MapView from "./components/MapView";
import RiddleView from "./components/RiddleView";

// Private route wrapper
const PrivateRoute = ({ children }) => {
  const { accessToken } = useContext(AuthContext);
  return accessToken ? children : <Navigate to="/" />;
};

// Login wrapper to inject onLogin
const LoginWrapper = () => {
  const { login } = useContext(AuthContext);
  return <AuthPage onLogin={login} />;
};

export default function App() {
  return (
    <AuthProvider>
      <LocationProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LoginWrapper />} />

            <Route
              path="/map"
              element={
                <PrivateRoute>
                  <MapView />
                </PrivateRoute>
              }
            />

            <Route
              path="/riddle/:enemyId"
              element={
                <PrivateRoute>
                  <RiddleView />
                </PrivateRoute>
              }
            />

            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </BrowserRouter>
      </LocationProvider>
    </AuthProvider>
  );
}
