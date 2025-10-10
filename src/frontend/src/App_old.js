import React, { useState } from "react";
import Register from "./components/Register";
import Login from "./components/Login";
import MapView from "./components/MapView";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || null);

  const handleLogin = (token) => {
    localStorage.setItem("token", token);
    setToken(token);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <div style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>Geocaching MVP</h1>

      {!token ? (
        <div style={{ display: "flex", gap: 40 }}>
          <div style={{ width: 320 }}>
            <h2>Register</h2>
            <Register onRegistered={(t) => t && handleLogin(t)} />
          </div>

          <div style={{ width: 320 }}>
            <h2>Login</h2>
            <Login onLogin={(t) => t && handleLogin(t)} />
          </div>
        </div>
      ) : (
        <>
          <div style={{ marginBottom: 12 }}>
            <button onClick={handleLogout}>Log out</button>
          </div>

          <MapView token={token} />
        </>
      )}
    </div>
  );
}

export default App;
