"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { useStudio } from "@/lib/store";
import type { ChatMessage, SeatState } from "@/types/game";
import {
  X,
  SendHorizontal,
  Volume2,
  Bot,
  Brain,
  Cpu,
  Layers,
  Coins,
  TrendingUp,
  Sparkles,
} from "lucide-react";
import CharacterPortrait from "./CharacterPortrait";

interface AgentInteractionModalProps {
  seatId: string | null;
  onClose: () => void;
}

export default function AgentInteractionModal({ seatId, onClose }: AgentInteractionModalProps) {
  const { state } = useStudio();
  const [input, setInput] = useState("");
  const [dms, setDms] = useState<ChatMessage[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Find the selected seat/agent details
  const agent = useMemo(() => {
    if (!seatId) return null;
    return state.seats.find((s) => s.seatId === seatId) || null;
  }, [seatId, state.seats]);

  // Map roles and departments beautifully
  const agentInfo = useMemo(() => {
    if (!agent) return null;
    const seatNum = agent.seatId.toLowerCase();
    
    if (seatNum.includes("s1") || seatNum.includes("alice") || seatNum.includes("character_02")) {
      return { role: "CEO", title: "Chief Executive Officer", dept: "Strategy", color: "#c9a227", icon: Brain };
    }
    if (seatNum.includes("s2") || seatNum.includes("bob") || seatNum.includes("character_03")) {
      return { role: "CTO", title: "Chief Technology Officer", dept: "Technology", color: "#4895ef", icon: Cpu };
    }
    if (seatNum.includes("s3") || seatNum.includes("carol") || seatNum.includes("character_04")) {
      return { role: "COO", title: "Chief Operations Officer", dept: "Operations", color: "#4ade80", icon: Layers };
    }
    if (seatNum.includes("s4") || seatNum.includes("dave") || seatNum.includes("character_05")) {
      return { role: "CFO", title: "Chief Financial Officer", dept: "Finance", color: "#f77f00", icon: Coins };
    }
    if (seatNum.includes("s5") || seatNum.includes("eve") || seatNum.includes("character_06")) {
      return { role: "CMO", title: "Chief Marketing Officer", dept: "Marketing", color: "#e0115f", icon: TrendingUp };
    }
    return { role: "Worker", title: "Operational Agent", dept: "Production", color: "#94a3b8", icon: Bot };
  }, [agent]);

  // Cute, real-human activities mapped based on seat status
  const currentActivity = useMemo(() => {
    if (!agent || !agentInfo) return "Resting";
    const status = agent.status;
    const role = agentInfo.role;

    if (status === "running" || status === "returning") {
      if (role === "CEO") return "Presenting corporate strategies to the Board 🏛️";
      if (role === "CTO") return "Refactoring deep compiled sub-processes 💻";
      if (role === "COO") return "Re-routing automated worker pipelines ⚙️";
      if (role === "CFO") return "Auditing active operational budget spend 💰";
      if (role === "CMO") return "Polishing campaign slogans and viral copy 📈";
      return "Executing task at high speed ⚡";
    }

    if (status === "failed") {
      if (role === "CEO") return "Filing risk crisis reports ⚠️";
      if (role === "CTO") return "Patching compilation memory leaks 🛠️";
      if (role === "COO") return "Re-routing failed socket dispatches 🔄";
      if (role === "CFO") return "Re-allocating overrun task budgets 📉";
      if (role === "CMO") return "Handling public relations feedback 📢";
      return "Analyzing runtime failure logs 🔍";
    }

    // Default standby/idle activities
    if (role === "CEO") return "Sipping an ice-cold match espresso ☕";
    if (role === "CTO") return "Munching on snack chips while debugging local config 🍕";
    if (role === "COO") return "Watering the office bonsai plants 🪴";
    if (role === "CFO") return "Filing tax forms and listening to lo-fi beats 🎵";
    if (role === "CMO") return "Chilling out on corporate social feeds 📱";
    return "Drinking cold fresh water 🥤";
  }, [agent, agentInfo]);

  // Set up initial welcoming DM when the modal opens
  useEffect(() => {
    if (!agent || !agentInfo) return;
    
    // Clear previous DMs and populate intro message
    const introMsg: ChatMessage = {
      id: `intro-${agent.seatId}`,
      runId: `run-intro-${agent.seatId}`,
      timestamp: new Date().toISOString(),
      sessionKey: "dm",
      role: "assistant",
      actorName: agent.label,
      content: `Hey! ${agent.label} here. 👋 I'm currently ${currentActivity.toLowerCase()}. How can I help you, bro? What are we working on?`,
    };
    setDms([introMsg]);
    setInput("");
    
    setTimeout(() => inputRef.current?.focus(), 150);
  }, [agent, agentInfo, currentActivity]);

  // Auto scroll chat to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [dms]);

  if (!agent || !agentInfo) return null;

  const handleSendDm = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    // Append User message locally
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      runId: `run-${Date.now()}`,
      timestamp: new Date().toISOString(),
      sessionKey: "dm",
      role: "user",
      content: trimmed,
    };
    setDms((prev) => [...prev, userMsg]);
    setInput("");

    // Fetch response from FastAPI Direct Chat API
    try {
      const response = await fetch("http://localhost:8000/api/v1/chat/direct", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          seat_id: agent.seatId,
          message: trimmed,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMsg: ChatMessage = {
          id: `assistant-${Date.now()}`,
          runId: userMsg.runId,
          timestamp: data.timestamp,
          sessionKey: "dm",
          role: "assistant",
          actorName: data.actorName,
          content: data.content,
        };
        setDms((prev) => [...prev, assistantMsg]);
      }
    } catch {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        runId: userMsg.runId,
        timestamp: new Date().toISOString(),
        sessionKey: "dm",
        role: "system",
        content: "Core server offline. Connect local FastAPI backend to speak directly.",
      };
      setDms((prev) => [...prev, errorMsg]);
    }
  };

  const handleSpeakText = (text: string) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;

    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find((v) => v.lang.startsWith("en"));
    if (englishVoice) utterance.voice = englishVoice;

    window.speechSynthesis.speak(utterance);
  };

  const IconComponent = agentInfo.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm pointer-events-auto">
      
      {/* GLOW BACKGROUND EFFECT */}
      <div
        className="absolute w-96 h-96 rounded-full opacity-20 filter blur-[80px] pointer-events-none"
        style={{ backgroundColor: agentInfo.color }}
      />

      {/* CORE MODAL CONTAINER */}
      <div className="relative w-full max-w-lg border-3 rounded-2xl bg-[#0b0a08]/95 text-[#e8e2d8] font-sans shadow-2xl flex flex-col max-h-[90vh] overflow-hidden"
        style={{ borderColor: agentInfo.color }}>
        
        {/* MODAL HEADER */}
        <div className="px-5 py-4 border-b border-[#2a241b] flex items-center justify-between bg-[#12100c]/80">
          <div className="flex items-center gap-3">
            <div className="relative p-1 rounded-lg border-2" style={{ borderColor: `${agentInfo.color}50` }}>
              <CharacterPortrait spritePath={agent.spritePath} name={agent.label} />
              <span className="absolute -bottom-1 -right-1 w-2.5 h-2.5 rounded-full border border-black"
                style={{
                  backgroundColor:
                    agent.status === "running" || agent.status === "returning"
                      ? "#4ade80"
                      : agent.status === "failed"
                      ? "#ef4444"
                      : "#4895ef",
                }}
              />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="font-bold text-base text-white leading-none">{agent.label}</h3>
                <span className="px-1.5 py-0.5 rounded font-mono text-[8px] font-bold uppercase border bg-opacity-25"
                  style={{
                    color: agentInfo.color,
                    borderColor: `${agentInfo.color}40`,
                    backgroundColor: `${agentInfo.color}15`,
                  }}
                >
                  {agentInfo.role}
                </span>
              </div>
              <p className="text-[10px] text-[#a09888] font-mono tracking-wider uppercase mt-1">
                {agentInfo.title} • {agentInfo.dept}
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-1 rounded-lg border border-[#4a4238] hover:border-white text-[#a09888] hover:text-white transition-all cursor-pointer bg-[#252219]/30"
          >
            <X size={16} />
          </button>
        </div>

        {/* STATUS BAR: CURRENT ACTIVITY */}
        <div className="px-5 py-2.5 bg-[#252219]/30 border-b border-[#2a241b] flex items-center gap-2 text-xs font-mono">
          <IconComponent size={14} style={{ color: agentInfo.color }} />
          <span className="text-[#a09888]">CURRENT ACTIVITY:</span>
          <span className="text-white font-medium">{currentActivity}</span>
        </div>

        {/* CHAT FEEDS BOX */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 flex flex-col gap-4 bg-[#12100c]/40 font-mono text-xs">
          {dms.map((dm) => {
            const isUser = dm.role === "user";
            const isSys = dm.role === "system";
            
            if (isSys) {
              return <div key={dm.id} className="text-center text-[#ef4444] bg-[#ef4444]/10 p-2 border border-[#ef4444]/20 rounded">{dm.content}</div>;
            }

            return (
              <div
                key={dm.id}
                className={`flex flex-col p-3 border rounded-xl relative max-w-[85%] ${
                  isUser
                    ? "self-end bg-[#252219]/40 border-[#4a4238]/60 text-white"
                    : "self-start bg-[#12100c]/80"
                }`}
                style={{
                  borderColor: isUser ? undefined : `${agentInfo.color}25`,
                }}
              >
                <div className="flex items-center justify-between mb-1.5 font-bold text-[9px] tracking-wide">
                  <span style={{ color: isUser ? "#4895ef" : agentInfo.color }}>
                    {isUser ? "YOU" : dm.actorName}
                  </span>
                  
                  {/* TTS Voice Speaker button for agent messages */}
                  {!isUser && (
                    <button
                      type="button"
                      onClick={() => handleSpeakText(dm.content)}
                      className="text-[#a09888] hover:text-white cursor-pointer bg-none border-none ml-2"
                      title="Listen"
                    >
                      <Volume2 size={11} />
                    </button>
                  )}
                </div>
                <p className="text-[#e8e2d8] leading-relaxed whitespace-pre-wrap">{dm.content}</p>
              </div>
            );
          })}
        </div>

        {/* INPUT SUBMIT FORM ROW */}
        <form onSubmit={handleSendDm} className="px-5 py-4 border-t border-[#2a241b] bg-[#12100c]/80 flex gap-2">
          <input
            ref={inputRef}
            type="text"
            className="flex-1 pixel-input text-xs h-10 px-3"
            placeholder={`Type a direct message to ${agent.label}...`}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            required
          />
          <button
            type="submit"
            className="pixel-icon-btn pixel-icon-btn--primary w-10 h-10 min-w-10 cursor-pointer"
            disabled={!input.trim()}
          >
            <SendHorizontal size={14} />
          </button>
        </form>

      </div>
    </div>
  );
}
