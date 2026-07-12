"use client";

import React, { useState, useMemo, useEffect } from "react";
import { useStudio } from "@/lib/store";
import type { SeatState, TaskItem, ChatMessage } from "@/types/game";
import {
  Activity,
  Cpu,
  Layers,
  Network,
  Play,
  Square,
  Users,
  Terminal,
  Settings,
  Clock,
  Coins,
  TrendingUp,
  Bot,
  ShieldAlert,
  Brain,
  Compass,
  FolderGit2,
  CheckCircle,
  AlertCircle,
  Sparkles,
  ChevronRight,
  Maximize2,
  RefreshCw,
  Search,
} from "lucide-react";

interface EnterpriseOSConsoleProps {
  onClose: () => void;
  onOpenDirectChat?: (seatId: string) => void;
}

type TabId = "dashboard" | "graph" | "debate" | "timeline" | "analytics";

export default function EnterpriseOSConsole({ onClose, onOpenDirectChat }: EnterpriseOSConsoleProps) {
  const { state, assignTask } = useStudio();
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Form states for launching mission
  const [missionName, setMissionName] = useState("");
  const [missionGoal, setMissionGoal] = useState("");
  const [missionBudget, setMissionBudget] = useState("50.00");
  const [missionPriority, setMissionPriority] = useState("high");

  // System status metrics
  const activeMission = useMemo(() => {
    // Find first unfinished or most recent task as the current mission
    if (state.tasks.length === 0) return null;
    return state.tasks[0];
  }, [state.tasks]);

  const stats = useMemo(() => {
    const totalTasks = state.tasks.length;
    const completedTasks = state.tasks.filter((t) => t.status === "completed").length;
    const failedTasks = state.tasks.filter((t) => t.status === "failed").length;
    const activeTasks = state.tasks.filter(
      (t) => t.status === "running" || t.status === "returning" || t.status === "submitted",
    ).length;

    const assignedSeatsCount = state.seats.filter((s) => s.assigned).length;
    const totalSeatsCount = state.seats.length;

    return {
      totalTasks,
      completedTasks,
      failedTasks,
      activeTasks,
      assignedSeatsCount,
      totalSeatsCount,
    };
  }, [state.tasks, state.seats]);

  // Handle mission launch
  const handleLaunchMission = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!missionGoal.trim()) return;

    // Compose a rich system-first mission task
    const compositeTask = `[MISSION: ${missionName || "Unnamed Mission"}] [BUDGET: $${missionBudget}] [PRIORITY: ${missionPriority.toUpperCase()}] ${missionGoal}`;
    
    // Create the mission in our FastAPI backend
    try {
      const response = await fetch("http://localhost:8000/api/v1/missions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: missionName || "Unnamed Mission",
          objective: missionGoal,
          budget: parseFloat(missionBudget) || 50.0,
          priority: missionPriority,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        console.log("Mission initialized in FastAPI backend:", data);
      } else {
        console.warn("FastAPI backend returned an error:", response.statusText);
      }
    } catch (err) {
      console.warn("Could not reach FastAPI backend (running local fallback):", err);
    }

    assignTask(compositeTask);
    
    // Clear form and open debate tab to watch the board execute
    setMissionGoal("");
    setMissionName("");
    setActiveTab("debate");
  };

  // Map raw seats to executive board roles
  const boardNodes = useMemo(() => {
    const roles = [
      { role: "CEO", title: "Chief Executive Officer", dept: "Strategy", color: "#c9a227" },
      { role: "CTO", title: "Chief Technology Officer", dept: "Technology", color: "#4895ef" },
      { role: "COO", title: "Chief Operations Officer", dept: "Operations", color: "#4ade80" },
      { role: "CFO", title: "Chief Financial Officer", dept: "Finance", color: "#f77f00" },
      { role: "CMO", title: "Chief Marketing Officer", dept: "Marketing", color: "#e0115f" },
    ];

    return state.seats.map((seat, idx) => {
      const roleInfo = roles[idx % roles.length];
      return {
        ...seat,
        role: roleInfo.role,
        roleTitle: seat.roleTitle || roleInfo.title,
        dept: roleInfo.dept,
        color: roleInfo.color,
      };
    });
  }, [state.seats]);

  // Selected node details
  const selectedNode = useMemo(() => {
    if (!selectedNodeId) return null;
    return boardNodes.find((n) => n.seatId === selectedNodeId) || null;
  }, [selectedNodeId, boardNodes]);

  // Default selection to first node if none selected
  useEffect(() => {
    if (!selectedNodeId && boardNodes.length > 0) {
      setSelectedNodeId(boardNodes[0].seatId);
    }
  }, [boardNodes, selectedNodeId]);

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-[#0b0a08]/95 backdrop-blur-xl text-[#e8e2d8] font-sans overflow-hidden">
      
      {/* GLOWING OS GRID LINES */}
      <div className="absolute inset-0 bg-[radial-gradient(#1a1712_1px,transparent_1px)] [background-size:16px_16px] opacity-20 pointer-events-none" />

      {/* HEADER BAR */}
      <header className="relative flex items-center justify-between px-6 py-4 border-b border-[#2a241b] bg-[#12100c]/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 border-2 border-[#c9a227] rounded-lg shadow-[0_0_15px_rgba(201,162,39,0.2)] animate-pulse">
            <Brain className="w-5 h-5 text-[#c9a227]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm tracking-widest font-black text-[#c9a227]">OMNIMIND.AI</span>
              <span className="px-1.5 py-0.5 font-mono text-[8px] bg-[#c9a227]/20 border border-[#c9a227]/30 text-[#c9a227] rounded tracking-wide">ENTERPRISE OS v1.0</span>
            </div>
            <p className="text-[10px] text-[#a09888] font-mono uppercase tracking-wider">Autonomous Organization Operating Kernel</p>
          </div>
        </div>

        {/* STATS TICKER */}
        <div className="hidden lg:flex items-center gap-8 font-mono text-[10px]">
          <div className="flex items-center gap-2">
            <span className="text-[#a09888]">ORG IQ:</span>
            <span className="text-[#4ade80] font-bold">148.4</span>
          </div>
          <div className="w-[1px] h-4 bg-[#2a241b]" />
          <div className="flex items-center gap-2">
            <span className="text-[#a09888]">MEM DEPTH:</span>
            <span className="text-white">12.8M tokens</span>
          </div>
          <div className="w-[1px] h-4 bg-[#2a241b]" />
          <div className="flex items-center gap-2">
            <span className="text-[#a09888]">ACTIVE OBJECTIVES:</span>
            <span className="text-[#facc15] font-bold animate-pulse">{stats.activeTasks}</span>
          </div>
          <div className="w-[1px] h-4 bg-[#2a241b]" />
          <div className="flex items-center gap-2">
            <span className="text-[#a09888]">CONNECTED DEPARTMENTS:</span>
            <span className="text-[#4ade80] font-bold">{stats.assignedSeatsCount}/5</span>
          </div>
        </div>

        {/* CLOSE CONTROL */}
        <button
          onClick={onClose}
          className="relative px-4 py-2 font-mono text-xs border border-[#4a4238] hover:border-[#c9a227] hover:text-[#c9a227] rounded bg-[#252219]/40 cursor-pointer transition-all duration-200 uppercase tracking-widest shadow-[inset_0_1px_2px_rgba(255,255,255,0.05)]"
        >
          Close OS Console
        </button>
      </header>

      {/* VIEW NAVIGATION TABS */}
      <div className="relative flex items-center justify-between px-6 py-2 border-b border-[#2a241b] bg-[#12100c]/40 z-10">
        <div className="flex gap-1.5 overflow-x-auto">
          {(
            [
              { id: "dashboard", label: "🚀 Mission Dashboard", desc: "Command & Control" },
              { id: "graph", label: "🕸️ Org Mind & Graph", desc: "Interactive Architecture" },
              { id: "debate", label: "🏛️ Executive Board", desc: "Live Boardroom Debates" },
              { id: "timeline", label: "🕒 Event Timeline", desc: "Milestones & Activity" },
              { id: "analytics", label: "📊 Observatory & Analytics", desc: "Observatory & Blackboard" },
            ] as const
          ).map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-col items-start px-4 py-2.5 rounded-lg border transition-all duration-200 cursor-pointer min-w-[150px] md:min-w-[180px] ${
                  isActive
                    ? "bg-[#252219]/80 border-[#c9a227] shadow-[0_0_15px_rgba(201,162,39,0.05)]"
                    : "bg-transparent border-transparent hover:bg-[#252219]/20 hover:border-[#4a4238]/60"
                }`}
              >
                <span className={`font-mono text-[11px] font-bold tracking-wider ${isActive ? "text-[#c9a227]" : "text-[#e8e2d8]"}`}>
                  {tab.label}
                </span>
                <span className="text-[8px] text-[#a09888] font-mono uppercase tracking-wide mt-0.5">
                  {tab.desc}
                </span>
              </button>
            );
          })}
        </div>
        
        {/* NETWORK HEURISTIC */}
        <div className="hidden sm:flex items-center gap-2 font-mono text-[9px] text-[#a09888]">
          <span className="w-1.5 h-1.5 bg-[#4ade80] rounded-full animate-ping" />
          <span>SYS HEURISTICS: STABLE</span>
        </div>
      </div>

      {/* CORE WORKSPACE CONTENT AREA */}
      <div className="flex-1 overflow-hidden relative">
        
        {/* TAB 1: MISSION DASHBOARD */}
        {activeTab === "dashboard" && (
          <div className="h-full overflow-y-auto p-6 flex flex-col xl:flex-row gap-6">
            
            {/* LEFT SIDE: CRITICAL STATS & ACTIVE MISSION VIEW */}
            <div className="flex-1 flex flex-col gap-6">
              
              {/* CURRENT MISSION STATUS BOARD */}
              <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/60 p-6 shadow-inner relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-radial-gradient from-[#c9a227]/5 to-transparent pointer-events-none" />
                
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className="px-2 py-0.5 font-mono text-[8px] bg-[#c9a227]/10 border border-[#c9a227]/20 text-[#c9a227] rounded tracking-widest uppercase">Active Objective</span>
                    <h2 className="text-xl font-bold font-sans tracking-tight mt-1 text-white">
                      {activeMission ? (activeMission.message.startsWith("[MISSION:") ? activeMission.message.split("]")[0].replace("[MISSION:", "").trim() : "Main System Executive Thread") : "No Active Mission"}
                    </h2>
                    <p className="text-xs text-[#a09888] font-mono mt-1">
                      {activeMission ? activeMission.message.replace(/\[[^\]]+\]/g, "").trim() : "The operating system is currently idle. Define a mission goal below to coordinate departments."}
                    </p>
                  </div>
                  {activeMission && (
                    <div className="flex flex-col items-end">
                      <span className={`px-2 py-1 font-mono text-[9px] rounded uppercase tracking-wider font-bold border ${
                        activeMission.status === "running" || activeMission.status === "returning"
                          ? "bg-[#facc15]/10 border-[#facc15]/30 text-[#facc15] animate-pulse"
                          : activeMission.status === "completed"
                          ? "bg-[#4ade80]/10 border-[#4ade80]/30 text-[#4ade80]"
                          : activeMission.status === "failed"
                          ? "bg-[#ef4444]/10 border-[#ef4444]/30 text-[#ef4444]"
                          : "bg-[#a09888]/10 border-[#a09888]/30 text-[#a09888]"
                      }`}>
                        {activeMission.status}
                      </span>
                    </div>
                  )}
                </div>

                {activeMission ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-[#2a241b] font-mono text-[10px]">
                    <div className="flex flex-col gap-1">
                      <span className="text-[#a09888] uppercase tracking-wider">Mission ID</span>
                      <span className="text-white font-bold">{activeMission.taskId}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[#a09888] uppercase tracking-wider">Thread Status</span>
                      <span className="text-[#4ade80] flex items-center gap-1.5 font-bold">
                        <span className="w-1.5 h-1.5 bg-[#4ade80] rounded-full animate-ping" />
                        Live streaming
                      </span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[#a09888] uppercase tracking-wider">Launched</span>
                      <span className="text-white">{new Date(activeMission.createdAt).toLocaleTimeString()}</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[#a09888] uppercase tracking-wider">Execution Hub</span>
                      <span className="text-[#c9a227] font-bold">CEO Office</span>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <Sparkles className="w-8 h-8 text-[#4a4238] animate-bounce mb-2" />
                    <span className="text-xs text-[#a09888] font-mono">Kernel standby. Ready to spawn organizations.</span>
                  </div>
                )}
              </div>

              {/* STATS GRID CARDS */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/30 p-4 font-mono">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] text-[#a09888] uppercase tracking-wider">Total Actions</span>
                    <Terminal className="w-3.5 h-3.5 text-[#c9a227]" />
                  </div>
                  <div className="text-2xl font-bold text-white">{stats.totalTasks}</div>
                  <div className="text-[8px] text-[#a09888] uppercase tracking-wide mt-1">Dispatched to nodes</div>
                </div>

                <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/30 p-4 font-mono">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] text-[#a09888] uppercase tracking-wider">Completed / Failed</span>
                    <CheckCircle className="w-3.5 h-3.5 text-[#4ade80]" />
                  </div>
                  <div className="text-2xl font-bold text-white flex items-center gap-2">
                    <span className="text-[#4ade80]">{stats.completedTasks}</span>
                    <span className="text-[#4a4238]">/</span>
                    <span className="text-[#ef4444]">{stats.failedTasks}</span>
                  </div>
                  <div className="text-[8px] text-[#a09888] uppercase tracking-wide mt-1">Mission accuracy index</div>
                </div>

                <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/30 p-4 font-mono">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] text-[#a09888] uppercase tracking-wider">Connected Boards</span>
                    <Users className="w-3.5 h-3.5 text-[#4895ef]" />
                  </div>
                  <div className="text-2xl font-bold text-white">5 / 5</div>
                  <div className="text-[8px] text-[#a09888] uppercase tracking-wide mt-1">Operational divisions</div>
                </div>
              </div>

              {/* MISSION CONSOLE GRAPH PROGRESS */}
              <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/60 p-6 flex-1 flex flex-col min-h-[220px]">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-[#c9a227]" />
                    <h3 className="font-mono text-xs font-bold tracking-wider uppercase text-white">Execution Telemetry</h3>
                  </div>
                  <span className="text-[9px] text-[#a09888] font-mono uppercase tracking-widest">Real-time status</span>
                </div>

                <div className="flex-1 flex flex-col justify-center gap-4">
                  {/* METRIC 1: COMPILATION / COMPLETION RATE */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between font-mono text-[10px]">
                      <span className="text-[#a09888] uppercase">MISSION COMPLETION RATIO</span>
                      <span className="text-[#4ade80] font-bold">
                        {stats.totalTasks > 0 ? Math.round((stats.completedTasks / stats.totalTasks) * 100) : 100}%
                      </span>
                    </div>
                    <div className="h-2 bg-[#2a241b] rounded overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#c9a227] to-[#4ade80] transition-all duration-500"
                        style={{ width: `${stats.totalTasks > 0 ? (stats.completedTasks / stats.totalTasks) * 100 : 100}%` }}
                      />
                    </div>
                  </div>

                  {/* METRIC 2: BUDGET EXPENSE */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between font-mono text-[10px]">
                      <span className="text-[#a09888] uppercase">BUDGET EXHAUSTION METRIC</span>
                      <span className="text-[#facc15] font-bold">$12.40 / $50.00</span>
                    </div>
                    <div className="h-2 bg-[#2a241b] rounded overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#4895ef] to-[#facc15] transition-all duration-500"
                        style={{ width: "24.8%" }}
                      />
                    </div>
                  </div>

                  {/* METRIC 3: MODEL ACCURACY AND INTEGRITY */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between font-mono text-[10px]">
                      <span className="text-[#a09888] uppercase">KNOWLEDGE PLASTICITY INDEX</span>
                      <span className="text-[#4ade80] font-bold">96.8%</span>
                    </div>
                    <div className="h-2 bg-[#2a241b] rounded overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#c9a227] to-[#4ade80] transition-all duration-500"
                        style={{ width: "96.8%" }}
                      />
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* RIGHT SIDE: BEAUTIFUL MISSION CONTROL FORM */}
            <div className="w-full xl:w-[420px] flex flex-col gap-6">
              <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/80 p-6 flex flex-col h-full relative">
                
                <div className="flex items-center gap-2 mb-4 pb-4 border-b border-[#2a241b]">
                  <Play className="w-4 h-4 text-[#c9a227]" />
                  <h3 className="font-mono text-xs font-bold tracking-wider uppercase text-white">Launch New Mission</h3>
                </div>

                <form onSubmit={handleLaunchMission} className="flex-1 flex flex-col gap-4 font-mono">
                  
                  {/* MISSION TITLE */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[9px] text-[#a09888] uppercase tracking-wider">Mission Objective / Name</label>
                    <input
                      type="text"
                      placeholder="e.g. Build API Scraper, Launch Marketing Strategy"
                      value={missionName}
                      onChange={(e) => setMissionName(e.target.value)}
                      className="px-3 py-2 bg-[#0b0a08] border border-[#4a4238] rounded focus:border-[#c9a227] focus:outline-none text-xs text-white"
                      required
                    />
                  </div>

                  {/* PARAMETERS GRID */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[9px] text-[#a09888] uppercase tracking-wider">Allocated Budget ($)</label>
                      <div className="relative">
                        <Coins className="absolute left-2.5 top-2 w-3.5 h-3.5 text-[#a09888]" />
                        <input
                          type="number"
                          value={missionBudget}
                          onChange={(e) => setMissionBudget(e.target.value)}
                          className="w-full pl-8 pr-3 py-2 bg-[#0b0a08] border border-[#4a4238] rounded focus:border-[#c9a227] focus:outline-none text-xs text-white"
                        />
                      </div>
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-[9px] text-[#a09888] uppercase tracking-wider">Priority Level</label>
                      <select
                        value={missionPriority}
                        onChange={(e) => setMissionPriority(e.target.value)}
                        className="px-2 py-2 bg-[#0b0a08] border border-[#4a4238] rounded focus:border-[#c9a227] focus:outline-none text-xs text-white cursor-pointer"
                      >
                        <option value="low">LOW</option>
                        <option value="medium">MEDIUM</option>
                        <option value="high">HIGH</option>
                        <option value="critical">CRITICAL</option>
                      </select>
                    </div>
                  </div>

                  {/* MISSION STATEMENT DETAILS */}
                  <div className="flex-1 flex flex-col gap-1.5">
                    <label className="text-[9px] text-[#a09888] uppercase tracking-wider">Detailed Goal Statement</label>
                    <textarea
                      placeholder="Detail your organizational objectives here... (e.g., CTO: Scrape historical stock data, CFO: Validate data with a Python validator, CEO: Synthesize a full trading strategy)."
                      value={missionGoal}
                      onChange={(e) => setMissionGoal(e.target.value)}
                      className="flex-1 px-3 py-2 bg-[#0b0a08] border border-[#4a4238] rounded focus:border-[#c9a227] focus:outline-none text-xs text-white resize-none min-h-[120px]"
                      required
                    />
                  </div>

                  {/* SUBMIT BUTTON */}
                  <button
                    type="submit"
                    className="w-full mt-4 py-3 bg-gradient-to-r from-[#c9a227] to-[#e5ba31] text-[#0b0a08] rounded font-bold uppercase tracking-widest text-xs cursor-pointer hover:shadow-[0_0_20px_rgba(201,162,39,0.3)] transition-all duration-200"
                  >
                    Deploy Living Organization
                  </button>
                </form>

              </div>
            </div>

          </div>
        )}

        {/* TAB 2: INTERACTIVE ORG MIND & GRAPH */}
        {activeTab === "graph" && (
          <div className="h-full flex flex-col lg:flex-row">
            
            {/* SVG GRAPH AREA */}
            <div className="flex-1 relative border-r border-[#2a241b] p-6 flex items-center justify-center bg-[#0d0c0a]/50">
              
              {/* LEGEND overlay */}
              <div className="absolute top-6 left-6 border border-[#2a241b] rounded-lg bg-[#12100c]/80 p-3 flex flex-col gap-2 font-mono text-[9px] z-10">
                <span className="text-[#a09888] font-bold uppercase tracking-wider mb-1">Status Legend</span>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#c9a227]" />
                  <span>CEO Executive Node</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#4ade80] animate-pulse" />
                  <span>Busy / Executing Task</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#4895ef]" />
                  <span>Idle / Core Standby</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444]" />
                  <span>Task Execution Failure</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#6b7280]" />
                  <span>Unassigned Node</span>
                </div>
              </div>

              {/* BEAUTIFUL DESIGNED ORG CHART SVG */}
              <div className="relative w-[800px] h-[480px] mx-auto scale-[0.82] md:scale-100 transition-all origin-center shrink-0">
                <svg className="w-full h-full absolute inset-0 pointer-events-none" viewBox="0 0 800 480" xmlns="http://www.w3.org/2000/svg">
                  {/* GLOW DEFS */}
                  <defs>
                    <linearGradient id="ceo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#c9a227" />
                      <stop offset="100%" stopColor="#f39c12" />
                    </linearGradient>
                    <filter id="glow-line" x="-10%" y="-10%" width="120%" height="120%">
                      <feGaussianBlur stdDeviation="4" result="blur" />
                      <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                  </defs>

                  {/* CUBIC BEZIER PATHS connecting CEO (400, 60) to department heads */}
                  {/* To CTO (100, 240) */}
                  <path
                    d="M 400 70 C 400 150, 100 150, 100 240"
                    stroke="#4895ef"
                    strokeWidth="2.5"
                    fill="none"
                    strokeDasharray="5,5"
                    opacity="0.8"
                    className="animate-[dash_15s_linear_infinite]"
                  />
                  {/* To COO (250, 240) */}
                  <path
                    d="M 400 70 C 400 150, 250 150, 250 240"
                    stroke="#4ade80"
                    strokeWidth="2.5"
                    fill="none"
                    strokeDasharray="5,5"
                    opacity="0.8"
                    className="animate-[dash_15s_linear_infinite]"
                  />
                  {/* To CFO (400, 240) */}
                  <path
                    d="M 400 70 L 400 240"
                    stroke="#f77f00"
                    strokeWidth="2.5"
                    fill="none"
                    strokeDasharray="5,5"
                    opacity="0.8"
                    className="animate-[dash_15s_linear_infinite]"
                  />
                  {/* To CMO (550, 240) */}
                  <path
                    d="M 400 70 C 400 150, 550 150, 550 240"
                    stroke="#e0115f"
                    strokeWidth="2.5"
                    fill="none"
                    strokeDasharray="5,5"
                    opacity="0.8"
                    className="animate-[dash_15s_linear_infinite]"
                  />
                  {/* To CSO (700, 240) */}
                  <path
                    d="M 400 70 C 400 150, 700 150, 700 240"
                    stroke="#94a3b8"
                    strokeWidth="2.5"
                    fill="none"
                    strokeDasharray="5,5"
                    opacity="0.8"
                    className="animate-[dash_15s_linear_infinite]"
                  />

                  {/* Connecting Workers from Department Heads to active worker leaves */}
                  {/* CTO workers */}
                  <path d="M 100 275 L 50 380" stroke="#4895ef" strokeWidth="1.5" fill="none" opacity="0.4" />
                  <path d="M 100 275 L 150 380" stroke="#4895ef" strokeWidth="1.5" fill="none" opacity="0.4" />
                  {/* COO worker */}
                  <path d="M 250 275 L 250 380" stroke="#4ade80" strokeWidth="1.5" fill="none" opacity="0.4" />
                  {/* CFO worker */}
                  <path d="M 400 275 L 400 380" stroke="#f77f00" strokeWidth="1.5" fill="none" opacity="0.4" />
                  {/* CMO worker */}
                  <path d="M 550 275 L 550 380" stroke="#e0115f" strokeWidth="1.5" fill="none" opacity="0.4" />
                </svg>

                {/* GRAPH INTERACTIVE NODES rendered as absolutely positioned HTML elements */}
                
                {/* 1. CEO NODE (Strategy / Root) */}
                <button
                  onClick={() => setSelectedNodeId(boardNodes[0]?.seatId || null)}
                  className={`absolute left-[325px] top-[20px] w-[150px] h-[80px] p-2 border rounded-xl flex flex-col items-center justify-center gap-0.5 cursor-pointer transition-all duration-300 ${
                    selectedNodeId === boardNodes[0]?.seatId
                      ? "bg-[#252219] border-[#c9a227] shadow-[0_0_30px_rgba(201,162,39,0.35)] scale-105"
                      : "bg-[#12100c]/90 border-[#2a241b] hover:border-[#c9a227]/50"
                  }`}
                  style={{ zIndex: 10 }}
                >
                  <Brain className="w-5 h-5 text-[#c9a227]" />
                  <span className="font-mono text-[8px] font-bold text-[#c9a227] tracking-wider">OMNIMIND CORE</span>
                  <span className="text-[11px] font-bold text-white tracking-tight">{boardNodes[0]?.label || "CEO (Alice)"}</span>
                  <span className="font-mono text-[7px] text-[#a09888] uppercase tracking-widest">Strategy Chief</span>
                </button>

                {/* 2. CTO NODE (Technology Head) */}
                <button
                  onClick={() => setSelectedNodeId(boardNodes[1]?.seatId || null)}
                  className={`absolute left-[35px] top-[205px] w-[130px] h-[70px] p-2 border rounded-xl flex flex-col items-center justify-center gap-0.5 cursor-pointer transition-all duration-300 ${
                    selectedNodeId === boardNodes[1]?.seatId
                      ? "bg-[#252219] border-[#4895ef] shadow-[0_0_20px_rgba(72,149,239,0.35)] scale-105"
                      : "bg-[#12100c]/90 border-[#2a241b] hover:border-[#4895ef]/50"
                  }`}
                  style={{ zIndex: 10 }}
                >
                  <Cpu className="w-4 h-4 text-[#4895ef]" />
                  <span className="font-mono text-[8px] font-bold text-[#4895ef] tracking-wider">TECH SYSTEMS</span>
                  <span className="text-[10px] font-bold text-white tracking-tight">{boardNodes[1]?.label || "CTO (Bob)"}</span>
                  <span className="font-mono text-[7px] text-[#a09888] uppercase tracking-widest">Tech Architect</span>
                </button>

                {/* 3. COO NODE (Operations / Dispatcher) */}
                <button
                  onClick={() => setSelectedNodeId(boardNodes[2]?.seatId || null)}
                  className={`absolute left-[185px] top-[205px] w-[130px] h-[70px] p-2 border rounded-xl flex flex-col items-center justify-center gap-0.5 cursor-pointer transition-all duration-300 ${
                    selectedNodeId === boardNodes[2]?.seatId
                      ? "bg-[#252219] border-[#4ade80] shadow-[0_0_20px_rgba(74,222,128,0.35)] scale-105"
                      : "bg-[#12100c]/90 border-[#2a241b] hover:border-[#4ade80]/50"
                  }`}
                  style={{ zIndex: 10 }}
                >
                  <Layers className="w-4 h-4 text-[#4ade80]" />
                  <span className="font-mono text-[8px] font-bold text-[#4ade80] tracking-wider">OPS SYSTEMS</span>
                  <span className="text-[10px] font-bold text-white tracking-tight">{boardNodes[2]?.label || "COO (Carol)"}</span>
                  <span className="font-mono text-[7px] text-[#a09888] uppercase tracking-widest">Operations Head</span>
                </button>

                {/* 4. CFO NODE (Finance / Budgeting) */}
                <button
                  onClick={() => setSelectedNodeId(boardNodes[3]?.seatId || null)}
                  className={`absolute left-[335px] top-[205px] w-[130px] h-[70px] p-2 border rounded-xl flex flex-col items-center justify-center gap-0.5 cursor-pointer transition-all duration-300 ${
                    selectedNodeId === boardNodes[3]?.seatId
                      ? "bg-[#252219] border-[#f77f00] shadow-[0_0_20px_rgba(247,127,0,0.35)] scale-105"
                      : "bg-[#12100c]/90 border-[#2a241b] hover:border-[#f77f00]/50"
                  }`}
                  style={{ zIndex: 10 }}
                >
                  <Coins className="w-4 h-4 text-[#f77f00]" />
                  <span className="font-mono text-[8px] font-bold text-[#f77f00] tracking-wider">FIN SYSTEMS</span>
                  <span className="text-[10px] font-bold text-white tracking-tight">{boardNodes[3]?.label || "CFO (Dave)"}</span>
                  <span className="font-mono text-[7px] text-[#a09888] uppercase tracking-widest">Financial Chief</span>
                </button>

                {/* 5. CMO NODE (Marketing / Outreach) */}
                <button
                  onClick={() => setSelectedNodeId(boardNodes[4]?.seatId || null)}
                  className={`absolute left-[485px] top-[205px] w-[130px] h-[70px] p-2 border rounded-xl flex flex-col items-center justify-center gap-0.5 cursor-pointer transition-all duration-300 ${
                    selectedNodeId === boardNodes[4]?.seatId
                      ? "bg-[#252219] border-[#e0115f] shadow-[0_0_20px_rgba(224,17,95,0.35)] scale-105"
                      : "bg-[#12100c]/90 border-[#2a241b] hover:border-[#e0115f]/50"
                  }`}
                  style={{ zIndex: 10 }}
                >
                  <TrendingUp className="w-4 h-4 text-[#e0115f]" />
                  <span className="font-mono text-[8px] font-bold text-[#e0115f] tracking-wider">CMO MARKETING</span>
                  <span className="text-[10px] font-bold text-white tracking-tight">{boardNodes[4]?.label || "CMO (Eve)"}</span>
                  <span className="font-mono text-[7px] text-[#a09888] uppercase tracking-widest">Outreach Head</span>
                </button>

                {/* 6. CSO NODE (Security / Legal / Offline Continuity) */}
                <button
                  className="absolute left-[635px] top-[205px] w-[130px] h-[70px] p-2 border rounded-xl flex flex-col items-center justify-center gap-0.5 cursor-not-allowed bg-[#12100c]/30 border-[#4a4238]/40"
                  style={{ zIndex: 10 }}
                  title="CSO division stand-by"
                >
                  <ShieldAlert className="w-4 h-4 text-[#94a3b8] opacity-60" />
                  <span className="font-mono text-[8px] font-bold text-[#94a3b8] opacity-60 tracking-wider">CSO SECURITY</span>
                  <span className="text-[10px] font-bold text-white/50 tracking-tight">CSO (Standby)</span>
                  <span className="font-mono text-[7px] text-[#a09888] opacity-55 uppercase tracking-widest">Security Chief</span>
                </button>

                {/* SUB-LEVEL WORKER LEAVES */}
                <div className="absolute left-[5px] top-[380px] w-[90px] p-1.5 border border-[#2a241b] rounded-lg bg-[#12100c]/90 font-mono text-[7px] flex flex-col items-center justify-center text-[#a09888]">
                  <Bot className="w-3 h-3 text-[#4895ef] mb-0.5" />
                  <span className="font-semibold text-white/80">Python Node</span>
                </div>
                <div className="absolute left-[105px] top-[380px] w-[90px] p-1.5 border border-[#2a241b] rounded-lg bg-[#12100c]/90 font-mono text-[7px] flex flex-col items-center justify-center text-[#a09888]">
                  <Bot className="w-3 h-3 text-[#4895ef] mb-0.5" />
                  <span className="font-semibold text-white/80">Browser Node</span>
                </div>
                <div className="absolute left-[205px] top-[380px] w-[90px] p-1.5 border border-[#2a241b] rounded-lg bg-[#12100c]/90 font-mono text-[7px] flex flex-col items-center justify-center text-[#a09888]">
                  <Bot className="w-3 h-3 text-[#4ade80] mb-0.5" />
                  <span className="font-semibold text-white/80">CLI Terminal</span>
                </div>
                <div className="absolute left-[355px] top-[380px] w-[90px] p-1.5 border border-[#2a241b] rounded-lg bg-[#12100c]/90 font-mono text-[7px] flex flex-col items-center justify-center text-[#a09888]">
                  <Bot className="w-3 h-3 text-[#f77f00] mb-0.5" />
                  <span className="font-semibold text-white/80">DB Auditor</span>
                </div>
                <div className="absolute left-[505px] top-[380px] w-[90px] p-1.5 border border-[#2a241b] rounded-lg bg-[#12100c]/90 font-mono text-[7px] flex flex-col items-center justify-center text-[#a09888]">
                  <Bot className="w-3 h-3 text-[#e0115f] mb-0.5" />
                  <span className="font-semibold text-white/80">Promo Sync</span>
                </div>

              </div>
            </div>

            {/* NODE INSPECTOR RIGHT PANEL */}
            <div className="w-full lg:w-[350px] bg-[#12100c]/80 p-6 flex flex-col font-mono">
              <div className="pb-4 border-b border-[#2a241b] flex items-center gap-2 mb-4">
                <Settings className="w-4 h-4 text-[#c9a227]" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Node Inspector</h3>
              </div>

              {selectedNode ? (
                <div className="flex-1 flex flex-col gap-5">
                  <div>
                    <span className="text-[8px] px-1.5 py-0.5 rounded uppercase font-bold tracking-widest bg-opacity-20 border"
                      style={{
                        borderColor: `${selectedNode.color}50`,
                        color: selectedNode.color,
                        backgroundColor: `${selectedNode.color}20`
                      }}
                    >
                      {selectedNode.dept} Department
                    </span>
                    <h4 className="text-lg font-bold text-white font-sans mt-2">{selectedNode.label}</h4>
                    <p className="text-[10px] text-[#a09888] font-mono tracking-wider">{selectedNode.roleTitle}</p>
                  </div>

                  <div className="flex flex-col gap-2.5 bg-[#0b0a08] border border-[#2a241b] p-3 rounded-lg text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-[#a09888]">STATUS:</span>
                      <span className="font-bold flex items-center gap-1" style={{ color: selectedNode.status === "running" ? "#4ade80" : selectedNode.status === "failed" ? "#ef4444" : "#4895ef" }}>
                        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: selectedNode.status === "running" ? "#4ade80" : selectedNode.status === "failed" ? "#ef4444" : "#4895ef" }} />
                        {selectedNode.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#a09888]">SEAT IDENTITY:</span>
                      <span className="text-white">{selectedNode.seatId}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#a09888]">DOCK TYPE:</span>
                      <span className="text-white uppercase font-bold">{selectedNode.seatType}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#a09888]">COGNITIVE MODEL:</span>
                      <span className="text-[#c9a227]">Gemini 2.5 Flash</span>
                    </div>
                  </div>

                  <div className="flex-1 border border-[#2a241b] rounded-lg p-4 bg-[#12100c]/40 text-[10px] flex flex-col justify-between mb-2">
                    <div>
                      <span className="text-[8px] text-[#a09888] uppercase tracking-wider font-bold">Active Instruction snippet</span>
                      <p className="text-xs text-[#e8e2d8] mt-1.5 leading-relaxed italic">
                        {selectedNode.taskSnippet ? `"${selectedNode.taskSnippet}"` : '"Standing by for executive commands from CEO node..."'}
                      </p>
                    </div>
                    {selectedNode.startedAt && (
                      <div className="pt-3 border-t border-[#2a241b] text-[8px] text-[#a09888] flex justify-between">
                        <span>TASK DEPLOYED</span>
                        <span>{new Date(selectedNode.startedAt).toLocaleTimeString()}</span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => onOpenDirectChat?.(selectedNode.seatId)}
                    className="w-full py-2.5 text-black font-bold rounded-lg uppercase tracking-wider text-[9px] cursor-pointer hover:brightness-110 transition-all duration-200"
                    style={{
                      backgroundColor: selectedNode.color,
                      boxShadow: `0 0 15px ${selectedNode.color}40`,
                    }}
                  >
                    💬 Direct Link: Chat & Iterate
                  </button>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center">
                  <Bot className="w-8 h-8 text-[#2a241b] animate-bounce mb-2" />
                  <span className="text-xs text-[#a09888]">Select any node in the graph map to inspect credentials.</span>
                </div>
              )}
            </div>

          </div>
        )}

        {/* TAB 3: EXECUTIVE BOARD DEBATE */}
        {activeTab === "debate" && (
          <div className="h-full flex flex-col p-6">
            
            {/* BOARD CHAT BOX PANEL */}
            <div className="flex-1 border border-[#2a241b] rounded-xl bg-[#12100c]/80 flex flex-col overflow-hidden relative">
              <div className="absolute inset-0 bg-[radial-gradient(#1a1712_1.5px,transparent_1.5px)] [background-size:24px_24px] opacity-10 pointer-events-none" />
              
              {/* Board title / header */}
              <div className="px-5 py-3 border-b border-[#2a241b] bg-[#12100c]/90 flex items-center justify-between z-10">
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#c9a227]" />
                  <span className="font-mono text-[11px] font-bold tracking-wider text-white uppercase">Boardroom Live Dialogue Stream</span>
                </div>
                <div className="flex items-center gap-4 font-mono text-[9px] text-[#a09888]">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-[#4ade80] animate-ping" />
                    Board Active
                  </span>
                  <span>TOTAL DISCUSSIONS: {state.chatMessages.length}</span>
                </div>
              </div>

              {/* Debate message history content */}
              <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-4 z-10 font-mono">
                {state.chatMessages.length > 0 ? (
                  state.chatMessages.map((msg, idx) => {
                    // Match msg actorName or role to find styled colors
                    const isSystem = msg.role === "system";
                    const isUser = msg.role === "user";
                    const isTool = msg.role === "tool";
                    
                    let senderLabel = msg.actorName || (isUser ? "CEO" : "Executive Board");
                    let badgeColor = "#c9a227";
                    let badgeBg = "rgba(201, 162, 39, 0.15)";
                    let borderClass = "border-[#c9a227]/20";

                    // Custom styling based on board roles
                    if (senderLabel.toLowerCase().includes("cto") || senderLabel.toLowerCase().includes("bob")) {
                      senderLabel = "CTO (Bob)";
                      badgeColor = "#4895ef";
                      badgeBg = "rgba(72, 149, 239, 0.15)";
                      borderClass = "border-[#4895ef]/20";
                    } else if (senderLabel.toLowerCase().includes("coo") || senderLabel.toLowerCase().includes("carol")) {
                      senderLabel = "COO (Carol)";
                      badgeColor = "#4ade80";
                      badgeBg = "rgba(74, 222, 128, 0.15)";
                      borderClass = "border-[#4ade80]/20";
                    } else if (senderLabel.toLowerCase().includes("cfo") || senderLabel.toLowerCase().includes("dave")) {
                      senderLabel = "CFO (Dave)";
                      badgeColor = "#f77f00";
                      badgeBg = "rgba(247, 127, 0, 0.15)";
                      borderClass = "border-[#f77f00]/20";
                    } else if (isSystem) {
                      senderLabel = "SYS KERNEL";
                      badgeColor = "#ef4444";
                      badgeBg = "rgba(239, 68, 68, 0.15)";
                      borderClass = "border-[#ef4444]/20";
                    } else if (isTool) {
                      senderLabel = `TOOL INTERFACE [${(msg as any).toolName}]`;
                      badgeColor = "#a09888";
                      badgeBg = "rgba(160, 152, 136, 0.15)";
                      borderClass = "border-[#a09888]/20";
                    }

                    return (
                      <div
                        key={msg.id || idx}
                        className={`flex flex-col p-4 rounded-lg border bg-[#0b0a08]/60 ${borderClass} relative`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span
                              className="px-2 py-0.5 rounded font-bold text-[9px] tracking-wider uppercase"
                              style={{ color: badgeColor, backgroundColor: badgeBg }}
                            >
                              {senderLabel}
                            </span>
                            {msg.role && (
                              <span className="text-[8px] text-[#a09888] uppercase font-bold tracking-widest">
                                [{msg.role}]
                              </span>
                            )}
                          </div>
                          <span className="text-[8px] text-[#4a4238]">
                            {new Date(msg.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        
                        <p className="text-xs text-[#e8e2d8] leading-relaxed select-text whitespace-pre-wrap">
                          {msg.content}
                        </p>
                        
                        {/* Stream indicators */}
                        {msg.role === "assistant" && (msg as any).streaming && (
                          <span className="absolute bottom-2 right-2 w-1.5 h-1.5 bg-[#4ade80] rounded-full animate-ping" />
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center py-12">
                    <Users className="w-12 h-12 text-[#2a241b] animate-pulse mb-3" />
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider">Boardroom Currently Idle</h4>
                    <p className="text-xs text-[#a09888] max-w-md leading-relaxed mt-1.5">
                      The Board is standing by. When you deploy a mission on the dashboard, the CEO, CTO, and CFO will debate objective constraints and compile the execution timeline here.
                    </p>
                  </div>
                )}
              </div>
            </div>

          </div>
        )}

        {/* TAB 4: SYSTEM EVENT TIMELINE */}
        {activeTab === "timeline" && (
          <div className="h-full p-6 overflow-y-auto">
            <div className="max-w-3xl mx-auto flex flex-col gap-6">
              
              <div className="flex items-center justify-between pb-4 border-b border-[#2a241b] font-mono">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-[#c9a227]" />
                  <span className="text-xs font-bold uppercase tracking-wider text-white">Milestone Event Log</span>
                </div>
                <span className="text-[9px] text-[#a09888] uppercase tracking-widest">Running chronicles</span>
              </div>

              {state.tasks.length > 0 ? (
                <div className="relative pl-6 border-l-2 border-[#2a241b] flex flex-col gap-6 font-mono">
                  {state.tasks.map((task) => {
                    const isCompleted = task.status === "completed";
                    const isFailed = task.status === "failed";
                    const isRunning = task.status === "running" || task.status === "returning";

                    return (
                      <div key={task.taskId} className="relative">
                        {/* Timeline node bullet */}
                        <div className={`absolute -left-[31px] top-1 w-2.5 h-2.5 rounded-full border-2 bg-[#0b0a08] ${
                          isCompleted ? "border-[#4ade80] shadow-[0_0_8px_#4ade80]" : isFailed ? "border-[#ef4444] shadow-[0_0_8px_#ef4444]" : isRunning ? "border-[#facc15] shadow-[0_0_8px_#facc15]" : "border-[#a09888]"
                        }`} />

                        <div className="bg-[#12100c]/60 border border-[#2a241b] p-4 rounded-xl flex flex-col gap-1.5 hover:border-[#4a4238] transition-all duration-200">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="px-1.5 py-0.5 rounded bg-[#252219]/60 text-[8px] text-[#c9a227] font-bold uppercase">
                                Action Dispatched
                              </span>
                              <span className="text-[9px] text-[#a09888] font-bold">
                                Task {task.taskId}
                              </span>
                            </div>
                            <span className="text-[8px] text-[#4a4238]">
                              {new Date(task.createdAt).toLocaleTimeString()}
                            </span>
                          </div>

                          <p className="text-xs text-white leading-relaxed font-sans font-medium">
                            {task.message.replace(/\[[^\]]+\]/g, "").trim()}
                          </p>

                          {task.actorName && (
                            <div className="text-[9px] text-[#a09888] flex items-center gap-1 mt-1">
                              <Bot className="w-3.5 h-3.5 text-[#c9a227]" />
                              <span>Assigned Worker:</span>
                              <span className="text-[#c9a227] font-bold">{task.actorName}</span>
                            </div>
                          )}

                          {task.result && (
                            <div className="mt-3 pt-3 border-t border-[#2a241b] text-[10px] bg-[#0b0a08]/40 p-2.5 rounded">
                              <span className="text-[8px] text-[#4ade80] font-bold uppercase tracking-wider block mb-1">Execution output</span>
                              <code className="text-[#4ade80] break-all leading-relaxed whitespace-pre-wrap">{task.result}</code>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-center py-16 font-mono">
                  <Clock className="w-12 h-12 text-[#2a241b] mb-3" />
                  <span className="text-xs text-[#a09888] uppercase tracking-wide">Timeline Standby</span>
                  <p className="text-xs text-[#4a4238] max-w-sm leading-relaxed mt-1.5">
                    No timeline events are available yet. Launching a mission automatically records the organizational execution milestones here.
                  </p>
                </div>
              )}

            </div>
          </div>
        )}

        {/* TAB 5: OBSERVATORY, BLACKBOARD & ANALYTICS */}
        {activeTab === "analytics" && (
          <div className="h-full overflow-y-auto p-6 flex flex-col lg:flex-row gap-6">
            
            {/* LEFT COLUMN: THE BLACKBOARD & GALAXY SESSIONS */}
            <div className="flex-1 flex flex-col gap-6">
              
              {/* THE BLACKBOARD */}
              <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/80 p-5 flex flex-col font-mono relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-radial-gradient from-[#c9a227]/5 to-transparent pointer-events-none" />
                
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#2a241b]">
                  <Terminal className="w-4 h-4 text-[#c9a227]" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-white">The Blackboard (Executive Bulletin)</h3>
                </div>

                <div className="flex flex-col gap-4 text-xs">
                  {/* CEO Alice note */}
                  <div className="border-l-2 border-[#c9a227] pl-3 py-1 bg-[#252219]/20 rounded-r">
                    <div className="flex items-center justify-between mb-1 text-[10px]">
                      <span className="text-[#c9a227] font-bold">CEO (Alice) — Strategy Department</span>
                      <span className="text-[#a09888]">10:45 AM</span>
                    </div>
                    <p className="text-[#e8e2d8] leading-relaxed italic">
                      "Constitutional directive is fully locked. Every strategic thread must register via the FastAPI endpoint. Maintain local state and ensure offline recovery continuity."
                    </p>
                  </div>

                  {/* CTO Bob note */}
                  <div className="border-l-2 border-[#4895ef] pl-3 py-1 bg-[#4895ef]/5 rounded-r">
                    <div className="flex items-center justify-between mb-1 text-[10px]">
                      <span className="text-[#4895ef] font-bold">CTO (Bob) — Technology Department</span>
                      <span className="text-[#a09888]">09:12 AM</span>
                    </div>
                    <p className="text-[#e8e2d8] leading-relaxed italic">
                      "Our 2D RPG Digital Twin and full-screen dashboards are officially aligned with Next.js 16/React 19. Standby for managed agent triggers. Offline synchronizer ready."
                    </p>
                  </div>

                  {/* CFO Dave note */}
                  <div className="border-l-2 border-[#f77f00] pl-3 py-1 bg-[#f77f00]/5 rounded-r">
                    <div className="flex items-center justify-between mb-1 text-[10px]">
                      <span className="text-[#f77f00] font-bold">CFO (Dave) — Financial Department</span>
                      <span className="text-[#a09888]">08:30 AM</span>
                    </div>
                    <p className="text-[#e8e2d8] leading-relaxed italic">
                      "Maximum budget caps enforced at $50 per execution loop. Cost metrics show standard model queries average $0.02. Solvency parameters are currently stable."
                    </p>
                  </div>
                </div>
              </div>

              {/* GALAXY VIEW (Multiverse Workspace Sessions) */}
              <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/60 p-5 flex flex-col font-mono">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#2a241b]">
                  <Compass className="w-4 h-4 text-[#c9a227]" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-white">Galaxy View (Session Multiverse)</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {state.sessions.length > 0 ? (
                    state.sessions.map((sess) => (
                      <div
                        key={sess.key}
                        className={`p-3 border rounded-lg flex items-center justify-between hover:border-[#c9a227]/40 transition-all duration-150 ${
                          state.activeSessionKey === sess.key
                            ? "bg-[#252219]/60 border-[#c9a227] shadow-[0_0_10px_rgba(201,162,39,0.1)]"
                            : "bg-[#0b0a08]/40 border-[#2a241b]"
                        }`}
                      >
                        <div className="flex flex-col gap-0.5 overflow-hidden">
                          <span className="text-[10px] text-white font-bold truncate">
                            {sess.label || `Universe: ${sess.key.slice(0, 8)}`}
                          </span>
                          <span className="text-[8px] text-[#a09888]">
                            Created: {new Date(sess.createdAt).toLocaleDateString()}
                          </span>
                        </div>
                        <span className="px-1.5 py-0.5 text-[7px] border border-[#4a4238] rounded bg-[#12100c]/60 text-[#a09888] uppercase">
                          {state.activeSessionKey === sess.key ? "ACTIVE" : "STANDBY"}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 py-6 text-center text-[10px] text-[#a09888]">
                      No previous cosmic sessions. Your primary executive session is initialized.
                    </div>
                  )}
                </div>
              </div>

            </div>

            {/* RIGHT COLUMN: ANALYTICS & OBSERVATORY STATS */}
            <div className="w-full lg:w-[350px] flex flex-col gap-6 font-mono">
              
              {/* ORGANIZATION OBSERVATORY */}
              <div className="border border-[#2a241b] rounded-xl bg-[#12100c]/80 p-5 flex-1 flex flex-col">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[#2a241b]">
                  <Activity className="w-4 h-4 text-[#c9a227]" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-white">Organization Observatory</h3>
                </div>

                <div className="flex-1 flex flex-col gap-4">
                  {/* Gauge 1: Execution Latency */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-[9px] text-[#a09888]">
                      <span>EXECUTION LATENCY</span>
                      <span className="text-[#4ade80] font-bold">142ms / STABLE</span>
                    </div>
                    <div className="h-1.5 bg-[#2a241b] rounded overflow-hidden">
                      <div className="h-full w-[24%] bg-[#4ade80]" />
                    </div>
                  </div>

                  {/* Gauge 2: Model Query Speed */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-[9px] text-[#a09888]">
                      <span>TOKEN THROUGHPUT</span>
                      <span className="text-[#4ade80] font-bold">84 tokens/sec</span>
                    </div>
                    <div className="h-1.5 bg-[#2a241b] rounded overflow-hidden">
                      <div className="h-full w-[78%] bg-gradient-to-r from-[#4ade80] to-[#c9a227]" />
                    </div>
                  </div>

                  {/* Gauge 3: System Resilience Heuristic */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-[9px] text-[#a09888]">
                      <span>SYS SOLVENCY & HEURISTIC</span>
                      <span className="text-[#4ade80] font-bold">99.8% READY</span>
                    </div>
                    <div className="h-1.5 bg-[#2a241b] rounded overflow-hidden">
                      <div className="h-full w-[99.8%] bg-[#4ade80]" />
                    </div>
                  </div>

                  {/* Gauge 4: Connection Quality */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-[9px] text-[#a09888]">
                      <span>METRIC RATIO</span>
                      <span className="text-[#c9a227] font-bold">5/5 connected</span>
                    </div>
                    <div className="h-1.5 bg-[#2a241b] rounded overflow-hidden">
                      <div className="h-full w-full bg-[#c9a227]" />
                    </div>
                  </div>

                  {/* Detailed System Status Block */}
                  <div className="mt-4 pt-4 border-t border-[#2a241b] flex-1 flex flex-col justify-between text-[10px] text-[#a09888] leading-relaxed">
                    <div className="flex flex-col gap-1.5">
                      <div className="flex justify-between">
                        <span>MODEL PLATFORM:</span>
                        <span className="text-[#c9a227]">Gemini 2.5 Flash</span>
                      </div>
                      <div className="flex justify-between">
                        <span>DATABASE ENGINE:</span>
                        <span className="text-white">Neo4j (Mock)</span>
                      </div>
                      <div className="flex justify-between">
                        <span>RECOVERY PARAM:</span>
                        <span className="text-[#4ade80] font-bold">Enabled</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 p-2.5 rounded bg-[#0b0a08]/40 border border-[#2a241b] text-[8px] uppercase tracking-wide text-center">
                      <span className="text-[#c9a227] font-bold">Observatory Heuristics lock:</span> STABLE
                    </div>
                  </div>

                </div>
              </div>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}
