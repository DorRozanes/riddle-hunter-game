import React, { useEffect, useRef, useState, useCallback, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { LocationContext } from "../context/LocationContext";
import EnemyApproaches from "./EnemyApproaches";

const API_BASE = process.env.REACT_APP_API_BASE;
const GMAPS_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

function loadGoogleScript(key) {
  return new Promise((resolve, reject) => {
    if (window.google && window.google.maps) return resolve(window.google);
    const id = "google-maps-script";
    if (document.getElementById(id)) {
      document
        .getElementById(id)
        .addEventListener("load", () => resolve(window.google));
      return;
    }
    const s = document.createElement("script");
    s.id = id;
    s.src = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=places`;
    s.async = true;
    s.defer = true;
    s.onload = () => resolve(window.google);
    s.onerror = reject;
    document.head.appendChild(s);
  });
}

function distanceMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export default function MapView() {
  const mapRef = useRef(null);
  const markerRef = useRef(null);       // user location
  const circleRef = useRef(null);       // accuracy circle
  const pinMarkerRef = useRef(null);    // manual pin
  const customMarkersRef = useRef([]);
  const watchIdRef = useRef(null);
  const enemyMarkersRef = useRef([]); // enemy markers on the map
  const [approachingEnemy, setApproachingEnemy] = useState(null);

  const { accessToken } = useContext(AuthContext);
  const { location, accuracy, setLocation } = useContext(LocationContext);

  const [pos, setPos] = useState(null);
  const [pinPos, setPinPos] = useState(null);
  const [placeInfo, setPlaceInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [gmapLoaded, setGmapLoaded] = useState(false);
  const [enemies, setEnemies] = useState([]);
  const [loadingEnemies, setLoadingEnemies] = useState(false);

  // Whenever location updates from the provider, sync it locally
  useEffect(() => {
    if (location) setPos(location);
  }, [location]);

  // --- Load Google Maps
  useEffect(() => {
    if (!GMAPS_KEY) {
      console.warn("REACT_APP_GOOGLE_MAPS_API_KEY not set.");
      return;
    }
    loadGoogleScript(GMAPS_KEY)
      .then(() => setGmapLoaded(true))
      .catch((err) => console.error("Failed to load Google Maps:", err));
  }, []);

  // --- Init map
  useEffect(() => {
    if (!gmapLoaded) return;
    const google = window.google;

    mapRef.current = new google.maps.Map(document.getElementById("map"), {
      center: { lat: 0, lng: 0 },
      zoom: 15,
    });

    // Add click listener for dropping a pin
    mapRef.current.addListener("click", (e) => {
      const latLng = { lat: e.latLng.lat(), lng: e.latLng.lng() };
      setPinPos(latLng);

      if (!pinMarkerRef.current) {
        pinMarkerRef.current = new google.maps.Marker({
          position: latLng,
          map: mapRef.current,
          title: "Dropped Pin",
          icon: "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
        });
      } else {
        pinMarkerRef.current.setPosition(latLng);
        pinMarkerRef.current.setMap(mapRef.current);
      }
    });
  }, [gmapLoaded]);

  // Save map reference
  const onLoad = useCallback(map => {
    mapRef.current = map;
  }, []);

  // Button handler
  const handleCenterMap = () => {
  if (mapRef.current && markerRef.current) {
    const pos = markerRef.current.getPosition();
    if (pos) {
      mapRef.current.panTo(pos);
      mapRef.current.setZoom(16);
      }
    }
  };

  // Update player marker when position changes
  useEffect(() => {
    if (!mapRef.current || !pos) return;

    const google = window.google;
    const latLng = { lat: pos.lat, lng: pos.lng };

    if (!markerRef.current) {
      markerRef.current = new google.maps.Marker({
        position: latLng,
        map: mapRef.current,
        icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        title: "You are here",
      });
      mapRef.current.panTo(latLng);
    } else {
      markerRef.current.setPosition(latLng);
    }

    // Draw accuracy circle
    if (accuracy > 200) {
      if (!circleRef.current) {
        circleRef.current = new google.maps.Circle({
          strokeColor: "#4285F4",
          strokeOpacity: 0.8,
          strokeWeight: 2,
          fillColor: "#4285F4",
          fillOpacity: 0.1,
          map: mapRef.current,
          center: latLng,
          radius: accuracy,
          clickable: false,
        });
      } else {
        circleRef.current.setCenter(latLng);
        circleRef.current.setRadius(accuracy);
      }
    } else if (circleRef.current) {
      circleRef.current.setMap(null);
      circleRef.current = null;
    }
  }, [pos]);

  // --- Fetch custom locations when map stops moving
useEffect(() => {
  if (!mapRef.current) return;
  const google = window.google;

  const fetchCustomLocations = async () => {
    const bounds = mapRef.current.getBounds();
    if (!bounds) return;

    const ne = bounds.getNorthEast();
    const sw = bounds.getSouthWest();

    try {
      const res = await fetch(`${API_BASE}/locations/custom_locations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          north: ne.lat(),
          east: ne.lng(),
          south: sw.lat(),
          west: sw.lng()
        }),
      });

      if (!res.ok) throw new Error(await res.text());
      const locations = await res.json();


      // Clear old markers
      customMarkersRef.current.forEach((m) => m.setMap(null));
      customMarkersRef.current = [];

      // Add new markers
      locations.forEach((loc) => {
        const marker = new google.maps.Marker({
          position: { lat: loc.lat, lng: loc.lng },
          map: mapRef.current,
          title: loc.name || "Custom Location",
          icon: "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
        });
        customMarkersRef.current.push(marker);

        marker.addListener("click", () => {
          setPlaceInfo(loc);
        });
      });
    } catch (err) {
      console.error("Error fetching custom locations:", err);
    }
  }
  // Use 'idle' instead of 'bounds_changed'
  const listener = mapRef.current.addListener("idle", fetchCustomLocations);

  return () => listener.remove();
}, [accessToken]);

// --- Function to fetch enemies from backend
async function fetchEnemies() {
if (!accessToken) return;
setLoadingEnemies(true);
try {
  const res = await fetch(`${API_BASE}/enemies/`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  setEnemies(data);
} catch (err) {
  console.error("Error fetching enemies:", err);
} finally {
  setLoadingEnemies(false);
}
};

// --- Function to spawn new enemies
async function spawnEnemies() {
if (!accessToken || !pos) return alert("No position yet");
setLoadingEnemies(true);
try {
  const res = await fetch(`${API_BASE}/enemies/spawn`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      latitude: pos.lat, longitude: pos.lng
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  console.log("Enemies spawned");
  await fetchEnemies(); // immediately refresh after spawning
} catch (err) {
  console.error("Spawn error:", err);
  alert("Spawn error: " + err.message);
} finally {
  setLoadingEnemies(false);
}
};

// --- Draw enemies on the map when enemies[] changes
useEffect(() => {
const google = window.google;
if (!mapRef.current || !window.google) return;

// Clear existing enemy markers
enemyMarkersRef.current.forEach((m) => m.setMap(null));
enemyMarkersRef.current = [];

enemies.forEach((enemy) => {
  console.log("Enemy:", enemy);
  const marker = new google.maps.Circle({
          strokeColor: "#EBB268",
          strokeOpacity: 0.8,
          strokeWeight: 2,
          fillColor: "#DEA862",
          fillOpacity: 0.1,
          map: mapRef.current,
          center: { lat: enemy.location.latitude, lng: enemy.location.longitude },
          radius: 40,
          clickable: false,
        });


  enemyMarkersRef.current.push(marker);
});
}, [enemies]);

// --- Optional: Auto-refresh enemies every 30s
useEffect(() => {
const interval = setInterval(() => {
  fetchEnemies();
}, 30000);
return () => clearInterval(interval);
}, [accessToken]);



// --- Manual lookup
async function askPlace() {
    const lat = pinPos?.lat ?? pos?.lat;
    const lng = pinPos?.lng ?? pos?.lng;
    if (!lat || !lng) return alert("No position yet");

    setLoading(true);
    setPlaceInfo(null);

    try {
      const res = await fetch(`${API_BASE}/locations/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({point: { latitude: lat, longitude: lng }}),
      });
      if (!res.ok) throw new Error(await res.text());
      const body = await res.json();
      setPlaceInfo(body);
    } catch (err) {
      console.error(err);
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
}

// Check an approaching enemy
useEffect(() => {
    if (!location || enemies.length === 0) return;

    let found = null;
    for (const e of enemies) {
      if (!e.location) continue;
      const dist = distanceMeters(
        location.lat,
        location.lng,
        e.location.latitude,
        e.location.longitude
      );

      // (a) player < 40m from enemy
      if (dist < 40) {
        found = { ...e, distance: dist };
        break;
      }

      // (b) player accuracy > 25m and pin < 40m from enemy
      if (accuracy > 25 && pinPos) {
        const distPin = distanceMeters(
          pinPos.lat,
          pinPos.lng,
          e.location.latitude,
          e.location.longitude
        );
        if (distPin < 40) {
          found = { ...e, distance: distPin };
          break;
        }
      }
    }

    setApproachingEnemy(found);
}, [location, accuracy, pinPos, enemies]);

  return (
    <div style={{ display: "flex", gap: 16 }}>
      <div>
      <div>
      <p><strong>Brave hero!</strong> Monsters have overrun our neighborhood!
      <br />
      Find the monsters (orange circles on the map) and defeat them!</p>
      </div>
        <div id="map" style={{ width: 640, height: 480, background: "#eee" }} />
        <div style={{ marginTop: 8 }}>
          <button onClick={askPlace} disabled={loading}>
            {loading ? "Checking…" : "What is this place?"}
          </button>
          {pinPos && (
            <button
              style={{ marginLeft: 8 }}
              onClick={() => {
                setPinPos(null);
                if (pinMarkerRef.current) {
                  pinMarkerRef.current.setMap(null);
                }
              }}
            >
              Clear Pin
            </button>
            )}
            <button
                onClick={handleCenterMap}
                style={{ marginLeft: 8 }}
            >
        📍 Center on Me
            </button>
            <button
                onClick={spawnEnemies}
                style={{ marginLeft: 8 }}
            >
        Spawn new enemies
            </button>
        </div>
      </div>

      <div style={{ width: 320 }}>
        <h3>Active Location</h3>
        {pinPos ? (
          <>
            <div>📍 Pin at:</div>
            <div>Lat: {pinPos.lat.toFixed(6)}</div>
            <div>Lng: {pinPos.lng.toFixed(6)}</div>
          </>
        ) : pos ? (
          <>
            <div>🛰️ GPS:</div>
            <div>Lat: {pos.lat.toFixed(6)}</div>
            <div>Lng: {pos.lng.toFixed(6)}</div>
            <div>Accuracy: {accuracy ?? "n/a"}m</div>
          </>
        ) : (
          <div>Waiting for location…</div>
        )}

        <h3>Place info</h3>
        {placeInfo ? (
            <div>
              <div>
                <p><strong>Name:</strong> {JSON.stringify(placeInfo.place.name, null, 2)}</p>
                <p><strong>Type:</strong> {JSON.stringify(placeInfo.place.place_types, null, 2)}</p>
              </div>
            </div>
        ) : (
          <div>No place info yet.</div>
        )}
      </div>

      {approachingEnemy && <EnemyApproaches enemy={approachingEnemy} />}
    </div>
  );
}
