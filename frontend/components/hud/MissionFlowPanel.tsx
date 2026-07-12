"use client"

import React, { useState, useEffect } from "react"
import { X } from "lucide-react"

interface MissionEvent {
  event: string
  payload: any
  timestamp: string
  missionId?: string
  confidence?: number
}

interface Executive {
  role: string
  concern: string
  recommendation: string
  confidence: number
}

interface Department {
  department_id: string
  type: string
  health: number
}

interface Worker {
  worker_id: string
  name: string
  role: string
  status: string
}

export function MissionFlowPanel({ onClose }: { onClose: () => void }) {
  const [events, setEvents] = useState<MissionEvent[]>([])
  const [currentMission, setCurrentMission] = useState<any>(null)
  const [executives, setExecutives] = useState<Executive[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [workers, setWorkers] = useState<Worker[]>([])
  const [currentStage, setCurrentStage] = useState<string>("idle")

  useEffect(() => {
    // Listen for mission events via window custom events
    const handleMissionEvent = (e: CustomEvent) => {
      const event = e.detail as MissionEvent
      setEvents((prev) => [...prev, event])

      // Update state based on event type
      switch (event.event) {
        case "MissionCreated":
          setCurrentMission(event.payload)
          setCurrentStage("Mission Created")
          break

        case "CEOBootStarted":
          setCurrentStage("CEO Analyzing Mission")
          break

        case "ExecutiveBoardMeetingStarted":
          setCurrentStage("Executive Board Meeting")
          setExecutives([])
          break

        case "ExecutiveRecommendation":
          setExecutives((prev) => [
            ...prev,
            {
              role: event.payload.executive,
              concern: event.payload.concern,
              recommendation: event.payload.recommendation,
              confidence: event.payload.confidence || 75,
            },
          ])
          break

        case "ExecutiveBoardMeetingCompleted":
          setCurrentStage("Organization Creation")
          break

        case "OrganizationCreated":
          setCurrentStage("Creating Departments")
          break

        case "DepartmentCreated":
          setDepartments((prev) => [
            ...prev,
            {
              department_id: event.payload.department_id,
              type: event.payload.type,
              health: event.payload.health || 100,
            },
          ])
          break

        case "WorkerSpawned":
          setWorkers((prev) => [
            ...prev,
            {
              worker_id: event.payload.worker_id,
              name: event.payload.name,
              role: event.payload.role,
              status: event.payload.status,
            },
          ])
          setCurrentStage("Workers Executing")
          break

        case "WorkerStatusChanged":
          setWorkers((prev) =>
            prev.map((w) =>
              w.worker_id === event.payload.worker_id
                ? { ...w, status: event.payload.status }
                : w
            )
          )
          break

        case "ReflectionStarted":
          setCurrentStage("Reflection & Learning")
          break

        case "MissionCompleted":
          setCurrentStage("Mission Completed ✓")
          break

        case "MissionFailed":
          setCurrentStage("Mission Failed ✗")
          break
      }
    }

    window.addEventListener("mission-event", handleMissionEvent as EventListener)

    return () => {
      window.removeEventListener("mission-event", handleMissionEvent as EventListener)
    }
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative w-[90vw] max-w-6xl h-[85vh] bg-[#161410] border-2 border-[#3d3525] rounded-lg overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-[#0b0a08] border-b-2 border-[#3d3525]">
          <div>
            <h2 className="text-lg font-bold text-[#c9a227] font-mono">
              MISSION EXECUTION FLOW
            </h2>
            <p className="text-xs text-[#a09888] mt-1">
              Live autonomous organization execution
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[#3d3525] rounded transition-colors"
          >
            <X className="w-5 h-5 text-[#a09888]" />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-col h-[calc(100%-80px)] overflow-hidden">
          {/* Current Stage */}
          <div className="px-6 py-4 bg-[#1c1914] border-b border-[#3d3525]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#a09888]">Current Stage:</p>
                <p className="text-xl font-bold text-white font-mono mt-1">
                  {currentStage}
                </p>
              </div>
              {currentMission && (
                <div className="text-right">
                  <p className="text-xs text-[#a09888]">Mission ID:</p>
                  <p className="text-sm text-[#c9a227] font-mono">
                    {currentMission.mission_id}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 overflow-auto p-6 space-y-6">
            {/* Executive Board */}
            {executives.length > 0 && (
              <div className="bg-[#0b0a08] border-2 border-[#3d3525] rounded-lg p-4">
                <h3 className="text-sm font-bold text-[#c9a227] mb-3 font-mono">
                  EXECUTIVE BOARD RECOMMENDATIONS
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {executives.map((exec, i) => (
                    <div
                      key={i}
                      className="bg-[#161410] border border-[#3d3525] rounded p-3"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-white">
                          {exec.role}
                        </span>
                        <span className="text-xs text-[#c9a227]">
                          {exec.confidence}% confidence
                        </span>
                      </div>
                      <p className="text-xs text-[#a09888] mb-1">
                        <span className="text-[#e8e2d8]">Concern:</span> {exec.concern}
                      </p>
                      <p className="text-xs text-[#a09888]">
                        <span className="text-[#e8e2d8]">Rec:</span>{" "}
                        {exec.recommendation}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Departments */}
            {departments.length > 0 && (
              <div className="bg-[#0b0a08] border-2 border-[#3d3525] rounded-lg p-4">
                <h3 className="text-sm font-bold text-[#c9a227] mb-3 font-mono">
                  DEPARTMENTS ({departments.length})
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {departments.map((dept) => (
                    <div
                      key={dept.department_id}
                      className="bg-[#161410] border border-[#3d3525] rounded p-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-white">
                          {dept.type}
                        </span>
                        <span className="text-xs text-[#4ade80]">
                          {dept.health}% health
                        </span>
                      </div>
                      <p className="text-xs text-[#a09888] mt-1 font-mono">
                        {dept.department_id}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Workers */}
            {workers.length > 0 && (
              <div className="bg-[#0b0a08] border-2 border-[#3d3525] rounded-lg p-4">
                <h3 className="text-sm font-bold text-[#c9a227] mb-3 font-mono">
                  WORKERS ({workers.length})
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {workers.map((worker) => (
                    <div
                      key={worker.worker_id}
                      className="bg-[#161410] border border-[#3d3525] rounded p-3"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-bold text-white">
                          {worker.name}
                        </span>
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            worker.status === "executing"
                              ? "bg-[#4ade80]/20 text-[#4ade80]"
                              : worker.status === "thinking"
                              ? "bg-[#facc15]/20 text-[#facc15]"
                              : "bg-[#a09888]/20 text-[#a09888]"
                          }`}
                        >
                          {worker.status}
                        </span>
                      </div>
                      <p className="text-xs text-[#a09888]">{worker.role}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Event Log */}
            <div className="bg-[#0b0a08] border-2 border-[#3d3525] rounded-lg p-4">
              <h3 className="text-sm font-bold text-[#c9a227] mb-3 font-mono">
                EVENT LOG ({events.length})
              </h3>
              <div className="space-y-2 max-h-64 overflow-auto">
                {events
                  .slice()
                  .reverse()
                  .map((event, i) => (
                    <div
                      key={i}
                      className="text-xs font-mono text-[#a09888] flex items-start gap-2"
                    >
                      <span className="text-[#c9a227] shrink-0">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                      <span className="text-white">{event.event}</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
