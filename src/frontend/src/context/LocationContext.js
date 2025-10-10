import React, { createContext, useState, useEffect, useRef } from "react";

export const LocationContext = createContext(null);

export const LocationProvider = ({ children }) => {
  const [location, setLocation] = useState(null); // {lat, lng}
  const [accuracy, setAccuracy] = useState(null);
  const [error, setError] = useState(null);
  const watchIdRef = useRef(null);

  useEffect(() => {
    if (!("geolocation" in navigator)) {
      setError("Geolocation not supported in this browser");
      return;
    }

    // Watch position continuously
    watchIdRef.current = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude, longitude, accuracy } = pos.coords;
        setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setAccuracy(accuracy);
        setError(null);
      },
      (err) => {
        console.error("Geolocation error:", err);
        setError(err.message);
      },
      {
        enableHighAccuracy: true,
        maximumAge: 3000,
        timeout: 10000,
      }
    );

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  return (
    <LocationContext.Provider value={{ location, accuracy, error }}>
      {children}
    </LocationContext.Provider>
  );
};
