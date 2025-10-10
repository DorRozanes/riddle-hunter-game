// Login.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login({ onLogin }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const API = process.env.REACT_APP_API_BASE;

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password}),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || "Login failed");
      }
      const data = await res.json();
      const token = data.access_token || data.token;
      if (!token) throw new Error("No token returned");
      onLogin(token);
      navigate("/map");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form onSubmit={submit}>
      <div>
        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} required />
      </div>
      <div>
        <label>Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
      </div>
      <div style={{ marginTop: 8 }}>
        <button type="submit">Login</button>
      </div>
      {error && <div style={{ color: "red" }}>{error}</div>}
    </form>
  );
}
