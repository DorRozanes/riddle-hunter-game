import React from "react";
import { useNavigate } from "react-router-dom";

export default function EnemyApproaches({ enemy }) {
  const navigate = useNavigate();
  if (!enemy) return null;

  const getEnemyImage = (type) => {
    try {
      return `http://localhost/enemies/${type}.png`;
    } catch {
      return `http://localhost/enemies/troll.png`;
    }
  };

  const enemyId = enemy.id
  const goToRiddle = () => {
    if (!enemyId) return;
    navigate(`/riddle/${enemyId}`);
  };

  return (
    <div
      style={{
        position: "absolute",
        right: 0,
        top: 0,
        width: "300px",
        height: "100%",
        background: "rgba(0,0,0,0.7)",
        color: "#fff",
        padding: "16px",
      }}
    >
      <h3>A { enemy.enemy_type } approaches!</h3>
      <img
        src={getEnemyImage(enemy.enemy_type)}
        alt={enemy.enemy_type}
        style={{ width: 128, height: 192 }}
      />
      <p><strong>Human! Solve my riddle, or I will eat you!</strong></p>
      <button
      onClick={goToRiddle}
      style={{
        marginTop: "16px",
        padding: "10px 16px",
        backgroundColor: "#ff5555",
        border: "none",
        borderRadius: "8px",
        color: "white",
        fontWeight: "bold",
        cursor: "pointer",
        transition: "background 0.2s",
      }}
      onMouseEnter={(e) => (e.target.style.backgroundColor = "#ff3333")}
      onMouseLeave={(e) => (e.target.style.backgroundColor = "#ff5555")}
      >
        Solve the Riddle
      </button>
    </div>
  );
}
