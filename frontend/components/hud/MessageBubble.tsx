"use client";

import { useMemo } from "react";
import { Square, Volume2 } from "lucide-react";
import type { ChatMessage } from "@/types/game";
import ToolBubble from "./ToolBubble";

export default function MessageBubble({
  msg,
  actorName,
  canStop,
  onStop,
}: {
  msg: ChatMessage;
  actorName?: string;
  canStop?: boolean;
  onStop?: () => void;
}) {
  const imageUrls = useMemo(() => {
    if (!msg.content) return [];
    
    // Regex to match all generated images or pollinations links in the content
    const matches = msg.content.match(/https?:\/\/[^\s]+(?:\.png|\.jpg|\.jpeg|pollinations\.ai[^\s]*|generated_[^\s]+)/gi);
    return matches ? Array.from(new Set(matches)) : [];
  }, [msg.content]);

  if (msg.role === "system") {
    return <div className="hud-chat__system">{msg.content}</div>;
  }

  if (msg.role === "tool") {
    return <ToolBubble msg={msg} />;
  }

  const handleStop = () => {
    if (onStop) onStop();
  };

  const handleSpeak = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (typeof window === "undefined" || !window.speechSynthesis) return;

    // Toggle off if currently speaking
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      return;
    }

    const utterance = new SpeechSynthesisUtterance(msg.content);
    utterance.rate = 1.05; // Natural human speed
    utterance.pitch = 1.0;

    // Grab english natural voices if available
    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(
      (v) => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google")),
    );
    if (naturalVoice) utterance.voice = naturalVoice;

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div
      className={`hud-chat__bubble ${
        msg.role === "user" ? "hud-chat__bubble--user" : "hud-chat__bubble--assistant"
      }`}
    >
      <div className="hud-chat__header" style={{ display: "flex", alignItems: "center" }}>
        <div className="hud-chat__role">
          {msg.role === "user" ? "You" : (msg.actorName ?? actorName ?? "Assistant")}
        </div>

        {/* Speak button for assistant replies */}
        {msg.role === "assistant" && (
          <button
            type="button"
            onClick={handleSpeak}
            style={{
              background: "none",
              border: "none",
              color: "var(--pixel-accent)",
              cursor: "pointer",
              padding: "2px",
              marginLeft: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              opacity: 0.8,
            }}
            title="Read message out loud"
            aria-label="Speak message"
          >
            <Volume2 size={11} className="hover:text-white transition-all duration-150" style={{ pointerEvents: "auto" }} />
          </button>
        )}

        {canStop && msg.role === "user" && (
          <button
            type="button"
            className="hud-chat__stop"
            onClick={handleStop}
            title="Stop task"
            aria-label="Stop task"
          >
            <Square size={10} fill="currentColor" />
          </button>
        )}
      </div>
      <div className="hud-chat__content">
        <div style={{ wordBreak: "break-word" }}>{msg.content}</div>
        
        {/* SINGLE IMAGE RENDER */}
        {imageUrls.length === 1 && (
          <div
            style={{
              marginTop: "8px",
              border: "2px solid var(--pixel-border)",
              borderRadius: "var(--pixel-radius-sm)",
              overflow: "hidden",
              boxShadow: "0 0 10px rgba(0, 0, 0, 0.5)",
              backgroundColor: "#12100c",
            }}
          >
            <img
              src={imageUrls[0]}
              alt="Generated Campaign Creative"
              style={{ width: "100%", height: "auto", display: "block", imageRendering: "auto" }}
            />
          </div>
        )}

        {/* MULTIPLE IMAGES CAMPAIGN GALLERY DECK (X, INSTAGRAM, LINKEDIN) */}
        {imageUrls.length > 1 && (
          <div style={{ marginTop: "10px", display: "flex", flexDirection: "column", gap: "10px" }}>
            {/* 1. TWITTER X WIDE BANNER */}
            {imageUrls[0] && (
              <div style={{ border: "2px solid var(--pixel-border)", borderRadius: "var(--pixel-radius-sm)", overflow: "hidden", backgroundColor: "#12100c" }}>
                <div style={{ background: "rgba(37, 34, 25, 0.8)", padding: "4px 8px", fontSize: "7px", fontFamily: "var(--font-pixel), monospace", textTransform: "uppercase", color: "var(--pixel-accent)", borderBottom: "1px solid var(--pixel-border)" }}>🐦 Twitter (X) Campaign Banner</div>
                <img src={imageUrls[0]} alt="Twitter Campaign" style={{ width: "100%", height: "auto", display: "block" }} />
              </div>
            )}

            {/* 2. INSTAGRAM AND LINKEDIN MULTICOLUMN GRIDS */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              {imageUrls[1] && (
                <div style={{ border: "2px solid var(--pixel-border)", borderRadius: "var(--pixel-radius-sm)", overflow: "hidden", backgroundColor: "#12100c" }}>
                  <div style={{ background: "rgba(37, 34, 25, 0.8)", padding: "4px 8px", fontSize: "7px", fontFamily: "var(--font-pixel), monospace", textTransform: "uppercase", color: "var(--pixel-accent)", borderBottom: "1px solid var(--pixel-border)" }}>📸 Instagram Post</div>
                  <img src={imageUrls[1]} alt="Instagram Post" style={{ width: "100%", height: "auto", display: "block" }} />
                </div>
              )}
              {imageUrls[2] && (
                <div style={{ border: "2px solid var(--pixel-border)", borderRadius: "var(--pixel-radius-sm)", overflow: "hidden", backgroundColor: "#12100c" }}>
                  <div style={{ background: "rgba(37, 34, 25, 0.8)", padding: "4px 8px", fontSize: "7px", fontFamily: "var(--font-pixel), monospace", textTransform: "uppercase", color: "var(--pixel-accent)", borderBottom: "1px solid var(--pixel-border)" }}>💼 LinkedIn Card</div>
                  <img src={imageUrls[2]} alt="LinkedIn Card" style={{ width: "100%", height: "auto", display: "block" }} />
                </div>
              )}
            </div>
          </div>
        )}
        
        {msg.streaming ? <span className="pixel-cursor">▌</span> : null}
      </div>
    </div>
  );
}
