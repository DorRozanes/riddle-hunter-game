import React, { useEffect, useState, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

const API_BASE = process.env.REACT_APP_API_BASE;

export default function RiddlePage() {
  const { accessToken } = useContext(AuthContext);
  const { enemyId } = useParams();
  const [enemyType, setEnemyType] = useState(null);
  const [riddle, setRiddle] = useState(null);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

    const getEnemyImage = (type) => {
    try {
      return `http://localhost/enemies/${type}.png`;
    } catch {
      return `http://localhost/enemies/troll.png`;
    }
    };

  useEffect(() => {
    async function loadRiddle() {
      try {
        const res = await fetch(`${API_BASE}/enemies/${enemyId}/riddle`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        setRiddle(data.riddle);
        setEnemyType(data.enemy_type)
      } catch (err) {
        console.error(err);
      }
    }
    loadRiddle();
  }, [enemyId, accessToken]);

  async function submitAnswer() {
    try {
      const res = await fetch(`${API_BASE}/enemies/${enemyId}/defeat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ enemy_id: enemyId, answer }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <img
        src={getEnemyImage(enemyType)}
        alt={enemyType}
        style={{ width: 256, height: 384 }}
      />
      <h2>Human! Solve my riddle if you wish to live!</h2>
      {!riddle ? (
        <p>Loading riddle...</p>
      ) : (
        <>
          <p style={{ fontStyle: "italic" }}>{riddle}</p>
          <input
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Your answer"
            style={{ padding: 8, width: "60%" }}
          />
          <button onClick={submitAnswer} style={{ marginLeft: 8 }}>
            Submit
          </button>
        </>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <p>{result.message}</p>
          {result.success && (
            <button onClick={() => navigate("/map")}>Back to map</button>
          )}
        </div>
      )}
    </div>
  );
}
