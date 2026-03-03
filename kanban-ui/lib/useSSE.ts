"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { KanbanEvent, getSSEUrl } from "./api";

interface UseSSEReturn {
    events: KanbanEvent[];
    connected: boolean;
    lastEvent: KanbanEvent | null;
}

/**
 * React hook for subscribing to Kanban SSE events.
 * Automatically reconnects on failure.
 */
export function useSSE(onEvent?: (event: KanbanEvent) => void): UseSSEReturn {
    const [events, setEvents] = useState<KanbanEvent[]>([]);
    const [connected, setConnected] = useState(false);
    const [lastEvent, setLastEvent] = useState<KanbanEvent | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);
    const onEventRef = useRef(onEvent);
    onEventRef.current = onEvent;

    const connect = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        const url = getSSEUrl();
        const es = new EventSource(url);
        eventSourceRef.current = es;

        es.onopen = () => {
            setConnected(true);
        };

        es.addEventListener("kanban", (e: MessageEvent) => {
            try {
                const data: KanbanEvent = JSON.parse(e.data);
                setLastEvent(data);
                setEvents((prev) => [data, ...prev].slice(0, 100)); // Keep last 100
                if (onEventRef.current) {
                    onEventRef.current(data);
                }
            } catch {
                // ignore parse errors
            }
        });

        es.onerror = () => {
            setConnected(false);
            es.close();
            // Reconnect after 3 seconds
            setTimeout(() => {
                connect();
            }, 3000);
        };
    }, []);

    useEffect(() => {
        connect();
        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
        };
    }, [connect]);

    return { events, connected, lastEvent };
}
