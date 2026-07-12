"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { SendHorizontal } from "lucide-react";
import { useStudio } from "@/lib/store";
import { gameEvents } from "@/lib/events";
import type { ChatMessage, SessionRecord, TaskItem } from "@/types/game";
import { findTask } from "@/lib/reducer";
import HudFlyout from "./HudFlyout";
import MessageBubble from "./MessageBubble";
import SessionSwitcher from "./SessionSwitcher";

export default function ChatPanel({
  messages,
  tasks,
  isConnected,
  sessions,
  activeSessionKey,
}: {
  messages: ChatMessage[];
  tasks: TaskItem[];
  isConnected: boolean;
  sessions: SessionRecord[];
  activeSessionKey?: string;
}) {
  const { assignTask, appendLocalChat } = useStudio();
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState<"gemini" | "gemma">("gemini");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const actorByRunId = useMemo(() => {
    const map = new Map<string, string>();
    for (const task of tasks) {
      if (!task.actorName) continue;
      if (task.runId) map.set(task.runId, task.actorName);
      map.set(task.taskId, task.actorName);
    }
    return map;
  }, [tasks]);

  const stopHandler = useCallback((runId: string, seatId: string) => {
    gameEvents.emit("stop-task", runId, seatId);
  }, []);

  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => scrollRef.current,
    estimateSize: () => 80,
    overscan: 5,
  });

  useEffect(() => {
    if (messages.length > 0) {
      virtualizer.scrollToIndex(messages.length - 1, { align: "end" });
    }
  }, [messages.length, virtualizer]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    // Create and append User message locally
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      runId: `run-${Date.now()}`,
      timestamp: new Date().toISOString(),
      sessionKey: activeSessionKey || "main",
      role: "user",
      content: trimmed,
    };
    appendLocalChat?.(userMsg);
    setInput("");

    // Try to get cognitive brief from our FastAPI backend
    try {
      const response = await fetch("http://localhost:8000/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmed,
          model: selectedModel,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        const assistantMsg: ChatMessage = {
          id: `assistant-${Date.now()}`,
          runId: userMsg.runId,
          timestamp: data.timestamp,
          sessionKey: activeSessionKey || "main",
          role: "assistant",
          actorName: data.actorName,
          content: data.content,
        };
        appendLocalChat?.(assistantMsg);
      } else {
        console.warn("FastAPI chat returned an error:", response.statusText);
      }
    } catch (err) {
      console.warn("Could not reach FastAPI chat backend:", err);
      const errorMsg: ChatMessage = {
        id: `sys-${Date.now()}`,
        runId: userMsg.runId,
        timestamp: new Date().toISOString(),
        sessionKey: activeSessionKey || "main",
        role: "system",
        content: "Cognitive core offline. To enable Gemini/Gemma briefings, please start your local FastAPI server ('uvicorn main:app --reload --port 8000') inside the 'backend/' directory.",
      };
      appendLocalChat?.(errorMsg);
    }

    // In parallel, if connected, dispatch task to 2D simulator agents
    if (isConnected) {
      assignTask(trimmed);
    }

    requestAnimationFrame(() => inputRef.current?.focus());
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    event.stopPropagation();
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <HudFlyout
      title="Chat"
      subtitle="Ask Gemini/Gemma about corporate activities"
      headerAction={<SessionSwitcher sessions={sessions} activeKey={activeSessionKey} />}
      bodyClass="hud-flyout__body--chat"
    >
      <div className="hud-chat-layout">
        
        {/* MODEL TOGGLE ROW */}
        <div style={{ display: "flex", gap: "6px", padding: "6px 8px", background: "rgba(37, 34, 25, 0.4)", borderBottom: "1px solid var(--pixel-border)" }}>
          <span style={{ fontSize: "8px", alignSelf: "center", color: "var(--pixel-accent)", fontFamily: "var(--pixel-font)", textTransform: "uppercase" }}>Model:</span>
          <button
            type="button"
            className={`pixel-button ${selectedModel === "gemini" ? "pixel-button--primary" : ""}`}
            style={{ fontSize: "7px", padding: "4px 8px", margin: 0, borderWidth: "1.5px" }}
            onClick={() => setSelectedModel("gemini")}
          >
            Gemini 2.5
          </button>
          <button
            type="button"
            className={`pixel-button ${selectedModel === "gemma" ? "pixel-button--primary" : ""}`}
            style={{ fontSize: "7px", padding: "4px 8px", margin: 0, borderWidth: "1.5px" }}
            onClick={() => setSelectedModel("gemma")}
          >
            Gemma 2B (Local)
          </button>
        </div>

        <div ref={scrollRef} className="hud-chat">
          {messages.length === 0 ? (
            <div className="hud-empty">No conversation yet. Type a message to begin.</div>
          ) : (
            <div
              style={{ height: virtualizer.getTotalSize(), width: "100%", position: "relative" }}
            >
              {virtualizer.getVirtualItems().map((virtualRow) => {
                const message = messages[virtualRow.index];
                const task = findTask(tasks, message.runId);
                const canStop = task?.status === "running" && (task.runId ?? task.taskId);
                return (
                  <div
                    key={virtualRow.key}
                    data-index={virtualRow.index}
                    ref={virtualizer.measureElement}
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                  >
                    <div style={{ paddingBottom: 8 }}>
                      <MessageBubble
                        msg={message}
                        actorName={actorByRunId.get(message.runId)}
                        canStop={!!canStop}
                        onStop={
                          canStop
                            ? () => stopHandler(task.runId ?? task.taskId, task.seatId ?? "")
                            : undefined
                        }
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="hud-chat-input-row">
          <textarea
            ref={inputRef}
            className="pixel-input"
            style={{ flex: 1, minHeight: 40, height: 40, resize: "none", padding: "8px 10px" }}
            placeholder="Ask Gemini/Gemma what's happening..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            type="button"
            className="pixel-icon-btn pixel-icon-btn--primary"
            style={{ width: 40, height: 40, minWidth: 40, minHeight: 40 }}
            onClick={handleSend}
            disabled={!input.trim()}
            title="Send"
          >
            <SendHorizontal size={16} />
          </button>
        </div>
      </div>
    </HudFlyout>
  );
}
