"use client";

import React, { useState, useEffect } from 'react';

interface TimelineEvent {
  id: string;
  type: string;
  timestamp: string;
  payload: any;
}

export default function Timeline({ missionId }: { missionId: string }) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initial mock events
    setEvents([
      { id: '1', type: 'MissionStarted', timestamp: new Date(Date.now() - 3600000).toISOString(), payload: { detail: 'Mission initialized' } },
      { id: '2', type: 'TaskAssigned', timestamp: new Date(Date.now() - 1800000).toISOString(), payload: { detail: 'Task 1 assigned to worker A' } },
    ]);

    // Setup WebSocket connection
    let ws: WebSocket;
    const connectWs = () => {
      try {
        // We'll try to connect to the backend websocket gateway implemented in Phase 11
        // Usually, the url would come from an environment variable
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
        ws = new WebSocket(`${wsUrl}?mission_id=${missionId}`);

        ws.onopen = () => {
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setEvents(prev => [...prev, data]);
          } catch (e) {
            console.error("Failed to parse websocket message", e);
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          // Reconnect logic could go here
        };
      } catch (e) {
        console.error("Failed to connect to websocket", e);
      }
    };

    if (typeof window !== 'undefined') {
      connectWs();
    }

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [missionId]);

  return (
    <div className="border rounded-lg p-6 bg-white shadow-sm flex flex-col h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Mission Timeline</h2>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-xs text-gray-500">{isConnected ? 'Live' : 'Offline'}</span>
        </div>
      </div>
      
      <div className="flex flex-col gap-4 overflow-y-auto max-h-[500px]">
        {events.length === 0 ? (
          <div className="text-gray-500 text-sm italic">No events recorded yet.</div>
        ) : (
          events.map((evt, idx) => (
            <div key={evt.id || idx} className="flex gap-4 items-start relative pb-4">
              {idx !== events.length - 1 && (
                <div className="absolute left-1.5 top-5 w-0.5 h-full bg-gray-200"></div>
              )}
              <div className="w-3 h-3 mt-1.5 rounded-full bg-blue-500 flex-shrink-0 z-10"></div>
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-medium">{evt.type}</span>
                  <span className="text-xs text-gray-500">{new Date(evt.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {evt.payload?.detail || JSON.stringify(evt.payload)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
