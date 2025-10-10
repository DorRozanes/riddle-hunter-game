import React, { useState } from "react";

export default function Register({ onRegistered }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const API = process.env.REACT_APP_API_BASE;

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password}),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || "Register failed");
      }
      const user = await res.json();
      // auto-login is optional — call /auth/login to get token; here we prompt user to login
      alert("Registered. Please login.");
      setUsername("");
      setPassword("");
      onRegistered && onRegistered(null);
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
        <button type="submit">Register</button>
      </div>
      {error && <div style={{ color: "red" }}>{error}</div>}
    </form>
  );
}
