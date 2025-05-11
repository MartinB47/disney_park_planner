import { useState, useEffect, useRef } from "react";

function useLivePosition(options = { enableHighAccuracy: true }) {
  const [position, setPosition] = useState(null);
  const [error, setError] = useState(null);
  const watcherId = useRef(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError(new Error("Geolocation not supported"));
      return;
    }

    // ask permission & get initial position
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setPosition({
          lat: coords.latitude,
          lon: coords.longitude,
          timestamp: coords.timestamp
        });

        //start watching continuously
        watcherId.current = navigator.geolocation.watchPosition(
          ({ coords }) => {
            setPosition({
              lat: coords.latitude,
              lon: coords.longitude,
              timestamp: coords.timestamp
            });
          },
          (err) => setError(err),
          options
        );
      },
      (err) => {
        // User denied or another error
        setError(err);
      },
      options
    );

    // Cleanup on unmount
    return () => {
      if (watcherId.current != null) {
        navigator.geolocation.clearWatch(watcherId.current);
      }
    };
  }, [options]);

  return { position, error };
}

// Example usage in a component
export default function App() {
  const { position, error } = useLivePosition();

  if (error){
    return <div>Error: {error.message}</div>;
  }
  if (!position){
    return <div>Waiting for location permission…</div>;
  }

  return (
    <div>
      <p>Lat: {position.lat}</p>
      <p>Lon: {position.lon}</p>
    </div>
  );
}