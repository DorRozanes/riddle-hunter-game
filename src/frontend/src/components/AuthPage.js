// AuthPage.js
import React from "react";
import Login from "./Login";
import Register from "./Register";

export default function AuthPage({ onLogin }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        gap: "40px",
        padding: "40px",
        minHeight: "100vh",
        background: "#f7f7f7",
      }}
    >
      <div style={{ flex: "1 1 300px", maxWidth: 400 }}>
        <h2>Login</h2>
        <Login onLogin={onLogin} />
      </div>

      <div style={{ flex: "1 1 300px", maxWidth: 400 }}>
        <h2>Register</h2>
        <Register />
      </div>
    </div>
  );
}
