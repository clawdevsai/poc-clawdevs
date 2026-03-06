"use client";
import { useEffect, useRef, useState } from "react";
import { getSSEUrl } from "./api";

export function useSSE(onEvent: () => void) {
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    function connect() {
      const es = new EventSource(getSSEUrl());
      esRef.current = es;

      es.addEventListener("kanban", () => {
        onEvent();
      });

      es.onopen = () => setConnected(true);

      es.onerror = () => {
        setConnected(false);
        es.close();
        setTimeout(connect, 4000);
      };
    }

    connect();
    return () => {
      esRef.current?.close();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return { connected };
}
