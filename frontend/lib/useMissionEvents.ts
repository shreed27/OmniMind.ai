"use client"

import { useEffect, useRef } from "react"

/**
 * Hook to connect to backend WebSocket and dispatch mission events
 */
export function useMissionEvents() {
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to backend WebSocket
    const connect = () => {
      const ws = new WebSocket("ws://localhost:8000/ws")

      ws.onopen = () => {
        console.log("✅ Connected to OmniMind.ai backend")
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Dispatch as custom event for MissionFlowPanel
          if (data.type === "event") {
            window.dispatchEvent(
              new CustomEvent("mission-event", {
                detail: {
                  event: data.event,
                  payload: data.payload || {},
                  timestamp: data.timestamp,
                  missionId: data.missionId,
                  confidence: data.confidence,
                },
              })
            )

            console.log(`📡 Mission event: ${data.event}`)
          }
        } catch (err) {
          console.error("Error parsing WebSocket message:", err)
        }
      }

      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
      }

      ws.onclose = () => {
        console.log("WebSocket disconnected, reconnecting in 3s...")
        setTimeout(connect, 3000)
      }

      wsRef.current = ws
    }

    connect()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])
}
