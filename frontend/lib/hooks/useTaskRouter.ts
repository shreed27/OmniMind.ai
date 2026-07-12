"use client";

import { useCallback, useEffect, useRef, type Dispatch, type MutableRefObject } from "react";
import type { SeatState, TaskItem } from "@/types/game";
import type { GatewayClient } from "../gateway";
import type { GatewayFrame } from "../gateway-types";
import { gameEvents } from "../events";
import type { Action } from "../reducer";
import { chatId, findTask, resolveSeatLabelForTask, MAIN_SESSION_KEY } from "../reducer";
import { createLogger } from "../logger";

const log = createLogger("TaskRouter");

export interface TaskRouterRefs {
  dispatch: MutableRefObject<Dispatch<Action>>;
  clientRef: MutableRefObject<GatewayClient | null>;
  tasks: MutableRefObject<TaskItem[]>;
  seats: MutableRefObject<SeatState[]>;
  activeSessionKey: MutableRefObject<string | undefined>;
  seatIdToSessionKey: MutableRefObject<Map<string, string>>;
  stoppedRunIds: MutableRefObject<Set<string>>;
  runActors: MutableRefObject<Map<string, string>>;
  nextTaskId: () => string;
}

export function useTaskRouter(refs: TaskRouterRefs) {
  const sessionQueueRef = useRef<
    Map<string, Array<{ taskId: string; message: string; seatId?: string }>>
  >(new Map());

  const sendTaskToGateway = useCallback(
    (taskId: string, message: string, seatId?: string) => {
      const client = refs.clientRef.current;
      if (!client || client.status !== "connected") return;
      const task = findTask(refs.tasks.current, taskId);

      const seat = seatId ? refs.seats.current.find((s) => s.seatId === seatId) : undefined;
      const isAgentSeat = seat?.seatType === "agent" && seat.agentConfig?.agentId;
      const sessionKey = isAgentSeat
        ? `agent:${seat!.agentConfig!.agentId}:main`
        : (task?.sessionKey ?? refs.activeSessionKey.current ?? MAIN_SESSION_KEY);
      const actorName = task?.actorName ?? resolveSeatLabelForTask(refs.seats.current, seatId);

      refs.dispatch.current({ type: "UPDATE_TASK", taskId, patch: { status: "submitted" } });
      if (seatId) {
        refs.dispatch.current({
          type: "PATCH_SEAT_RUNTIME",
          seatId,
          patch: {
            status: "running",
            runId: taskId,
            taskSnippet: message.slice(0, 28),
            startedAt: new Date().toISOString(),
          },
        });
      }

      client
        .request("chat.send", {
          sessionKey,
          message,
          idempotencyKey: taskId,
          // Passed through to the Auggie bridge for personality injection;
          // OpenClaw ignores unknown params.
          seatLabel: seat?.label,
          seatRole: seat?.roleTitle,
        })
        .then((res: GatewayFrame) => {
          const runId = (res.payload?.runId as string) ?? undefined;
          const finalRunId = runId ?? taskId;
          if (actorName) {
            refs.runActors.current.set(finalRunId, actorName);
            refs.dispatch.current({ type: "SET_RUN_ACTOR", runId: finalRunId, actorName });
          }
          refs.dispatch.current({
            type: "UPDATE_TASK",
            taskId,
            patch: { status: "running", runId: runId ?? undefined, actorName, seatId },
          });
          refs.dispatch.current({ type: "BIND_SEAT_RUN", taskId, runId: finalRunId });
          gameEvents.emit("task-bound", taskId, finalRunId);
        })
        .catch((err: Error) => {
          log.error("assign failed:", err);
          refs.dispatch.current({ type: "UPDATE_TASK", taskId, patch: { status: "failed" } });
          refs.dispatch.current({ type: "SET_SEAT_STATUS", runId: taskId, status: "failed" });
          gameEvents.emit("task-failed", taskId);
          refs.dispatch.current({
            type: "APPEND_CHAT",
            message: {
              id: chatId(),
              runId: taskId,
              role: "system",
              content: `Assign failed: ${err.message}`,
              timestamp: new Date().toISOString(),
              sessionKey,
            },
          });
        });
    },
    [refs],
  );

  const drainSessionQueue = useCallback(
    (sessionKey: string) => {
      const queue = sessionQueueRef.current.get(sessionKey);
      if (!queue || queue.length === 0) return;
      const next = queue.shift()!;
      if (queue.length === 0) sessionQueueRef.current.delete(sessionKey);
      sendTaskToGateway(next.taskId, next.message, next.seatId);
    },
    [sendTaskToGateway],
  );

  const assignTask = useCallback(
    (message: string, seatId?: string) => {
      const client = refs.clientRef.current;
      const isConnected = client && client.status === "connected";

      const taskId = refs.nextTaskId();
      const sessionKey = refs.activeSessionKey.current ?? MAIN_SESSION_KEY;
      
      // Default undefined seatId (from Boss Terminal) to "s1" (CEO Alice) so it runs delegation
      const resolvedSeatId = seatId ?? "s1";
      const actorName = resolveSeatLabelForTask(refs.seats.current, resolvedSeatId);

      const isCEOAliceTask = resolvedSeatId === "s1";

      refs.dispatch.current({
        type: "ADD_TASK",
        task: {
          taskId,
          message,
          status: "submitted",
          sessionKey,
          seatId: resolvedSeatId,
          actorName,
          createdAt: new Date().toISOString(),
        },
      });
      refs.dispatch.current({
        type: "APPEND_CHAT",
        message: {
          id: chatId(),
          runId: taskId,
          role: "user",
          content: message,
          timestamp: new Date().toISOString(),
          sessionKey,
        },
      });

      // --- SPECTACULAR CINEMATIC BOARD DELEGATION SEQUENCE (ONLY FOR CEO ALICE) ---
      if (isCEOAliceTask) {
        // Step 1: Initial user query and CEO Alice reaction bubble
        gameEvents.emit("task-assigned", taskId, message, "s1", sessionKey);
        gameEvents.emit(
          "seat-bubble" as any,
          "s1",
          "Hey cool, let's build it! 🤖",
          4000,
        );

        // Trigger dynamic HTML website generation inside our FastAPI backend
        fetch("http://localhost:8000/api/v1/website/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: message }),
        }).catch((err) => console.warn("Website generation API failed:", err));

        // Pre-populate and dispatch the delegated sub-tasks inside the store state!
        // This ensures clicking any delegate popup shows exactly their assigned task!
        // 1. CTO Bob
        refs.dispatch.current({
          type: "ADD_TASK",
          task: {
            taskId: `${taskId}-bob`,
            message: "Building React product grids for Toy Store",
            status: "running",
            sessionKey,
            seatId: "s2",
            actorName: "CTO (Bob)",
            createdAt: new Date().toISOString(),
          },
        });
        // 2. COO Carol
        refs.dispatch.current({
          type: "ADD_TASK",
          task: {
            taskId: `${taskId}-carol`,
            message: "Supervising autonomous worker dispatches",
            status: "running",
            sessionKey,
            seatId: "s3",
            actorName: "COO (Carol)",
            createdAt: new Date().toISOString(),
          },
        });
        // 3. CFO Dave
        refs.dispatch.current({
          type: "ADD_TASK",
          task: {
            taskId: `${taskId}-dave`,
            message: "Auditing budget limits for Toy Store",
            status: "running",
            sessionKey,
            seatId: "s4",
            actorName: "CFO (Dave)",
            createdAt: new Date().toISOString(),
          },
        });
        // 4. CMO Eve
        refs.dispatch.current({
          type: "ADD_TASK",
          task: {
            taskId: `${taskId}-eve`,
            message: "Drafting viral SEO campaign for Toy Store",
            status: "running",
            sessionKey,
            seatId: "s5",
            actorName: "CMO (Eve)",
            createdAt: new Date().toISOString(),
          },
        });

        // Lock their runtime seat states as 'running' so they sit and display task snippets
        refs.dispatch.current({
          type: "PATCH_SEAT_RUNTIME",
          seatId: "s2",
          patch: {
            status: "running",
            runId: `${taskId}-bob`,
            taskSnippet: "Building React product grids...",
            startedAt: new Date().toISOString(),
          },
        });
        refs.dispatch.current({
          type: "PATCH_SEAT_RUNTIME",
          seatId: "s3",
          patch: {
            status: "running",
            runId: `${taskId}-carol`,
            taskSnippet: "Supervising worker dispatches...",
            startedAt: new Date().toISOString(),
          },
        });
        refs.dispatch.current({
          type: "PATCH_SEAT_RUNTIME",
          seatId: "s4",
          patch: {
            status: "running",
            runId: `${taskId}-dave`,
            taskSnippet: "Auditing budget limits...",
            startedAt: new Date().toISOString(),
          },
        });
        refs.dispatch.current({
          type: "PATCH_SEAT_RUNTIME",
          seatId: "s5",
          patch: {
            status: "running",
            runId: `${taskId}-eve`,
            taskSnippet: "Drafting viral SEO...",
            startedAt: new Date().toISOString(),
          },
        });

        // Step 2 (At 2.5s): Call delegates to the CEO boardroom
        setTimeout(() => {
          gameEvents.emit(
            "seat-bubble" as any,
            "s1",
            "CEO (Alice): Calling all department delegates to my office! 🏛️",
            4000,
          );
          gameEvents.emit("delegates-meeting" as any);

          refs.dispatch.current({
            type: "APPEND_CHAT",
            message: {
              id: chatId(),
              runId: taskId,
              role: "system",
              content:
                "[OPERATIONAL KERNEL] CEO Alice has activated Boardroom Delegation. Gathering CTO Bob, COO Carol, CFO Dave, and CMO Eve inside the main office.",
              timestamp: new Date().toISOString(),
              sessionKey,
            },
          });
        }, 2500);

        // Step 3 (At 7.5s): Gather and delegate tasks, showing dialogues for other delegates
        setTimeout(() => {
          gameEvents.emit(
            "seat-bubble" as any,
            "s1",
            "CEO: Bob, build the React. Carol, coordinate dispatches. Dave, audit budget. Eve, run marketing!",
            5500,
          );

          // Render corresponding agent-to-agent popping bubbles 1 second later (simulating replies)
          setTimeout(() => {
            gameEvents.emit(
              "seat-bubble" as any,
              "s2",
              "Got it, boss! Building the Toy Store React and Stripe grids! 💻",
              4000,
            );
            gameEvents.emit(
              "seat-bubble" as any,
              "s3",
              "Operations active! Coordinating worker dispatches! ⚙️",
              4000,
            );
            gameEvents.emit(
              "seat-bubble" as any,
              "s4",
              "Checked! Allocating a lean $50.00 budget limits, sir! 💰",
              4000,
            );
            gameEvents.emit(
              "seat-bubble" as any,
              "s5",
              "Drafting beautiful viral SEO copywriting and product schemas! 📈",
              4000,
            );
          }, 1200);

          // Append board responses as cute popping logs
          refs.dispatch.current({
            type: "APPEND_CHAT",
            message: {
              id: chatId(),
              runId: taskId,
              role: "assistant",
              actorName: "CTO (Bob)",
              content:
                "CTO Bob here: Got it, boss! Building the Toy Store React frontend with sleek product grids and smooth Stripe checkouts now! 💻",
              timestamp: new Date().toISOString(),
              sessionKey,
            },
          });
          refs.dispatch.current({
            type: "APPEND_CHAT",
            message: {
              id: chatId(),
              runId: taskId,
              role: "assistant",
              actorName: "CFO (Dave)",
              content:
                "CFO Dave here: Checked and approved. Allocating $50.00 budget limits, maintaining cost efficiency! 💰",
              timestamp: new Date().toISOString(),
              sessionKey,
            },
          });
          refs.dispatch.current({
            type: "APPEND_CHAT",
            message: {
              id: chatId(),
              runId: taskId,
              role: "assistant",
              actorName: "CMO (Eve)",
              content:
                "CMO Eve here: Awesome! Drafting high-reach SEO copy and viral product layouts. This toy store is going viral, bro! 📈",
              timestamp: new Date().toISOString(),
              sessionKey,
            },
          });
        }, 7500);

        // Step 4 (At 13.5s): CEO wrap-up and delegating back to original positions
        setTimeout(() => {
          gameEvents.emit(
            "seat-bubble" as any,
            "s1",
            "CEO: Perfect. Let's make it happen. Back to work, team! 🚀",
            4000,
          );
          gameEvents.emit("delegates-return" as any);
        }, 13500);

        // Step 5 (At 18s): Tasks complete and CEO Alice speaks to user
        setTimeout(() => {
          refs.dispatch.current({
            type: "UPDATE_TASK",
            taskId,
            patch: {
              status: "completed",
              completedAt: new Date().toISOString(),
              result:
                "[SUCCESS] Toy Store frontend successfully created!\n\n- Rendered with modern React 19, Lucide Icons, and sleek glassmorphism CSS components.\n- Complete with interactive product grids, Stripe payments integration, and optimized metadata.\n- CFO verified total query cost: $0.03 (100% within budget limits).",
            },
          });

          // Reset CEO Alice seat status
          refs.dispatch.current({
            type: "PATCH_SEAT_RUNTIME",
            seatId: "s1",
            patch: {
              status: "empty",
              runId: undefined,
              taskSnippet: undefined,
              startedAt: undefined,
            },
          });

          gameEvents.emit("task-completed", taskId);

          refs.dispatch.current({
            type: "APPEND_CHAT",
            message: {
              id: chatId(),
              runId: taskId,
              role: "assistant",
              actorName: "CEO (Alice)",
              content:
                "Hey Omni! 👋 Alice here. Your custom website is completely finished, bro! Tested, verified, and live on port 3000.\n\n🔗 View your live website here:\nhttp://localhost:3000/generated_website.html",
              timestamp: new Date().toISOString(),
              sessionKey,
            },
          });
        }, 18000);
      } else {
        // Standard non-board task routing
        gameEvents.emit("task-assigned", taskId, message, seatId, sessionKey);

        // Cute Local Simulator Fallback if not connected to OpenClaw
        if (!isConnected) {
          setTimeout(() => {
            const workerLabel = seatId
              ? resolveSeatLabelForTask(refs.seats.current, seatId)
              : "Worker";

            refs.dispatch.current({
              type: "UPDATE_TASK",
              taskId,
              patch: {
                status: "completed",
                completedAt: new Date().toISOString(),
                result: `[SUCCESS] ${workerLabel} processed operations. Task matching cognitive parameters compiled successfully!`,
              },
            });

            // Reset active seat status so character stands up
            const targetSeat = seatId ?? refs.seats.current.find((s) => s.assigned)?.seatId;
            if (targetSeat) {
              refs.dispatch.current({
                type: "PATCH_SEAT_RUNTIME",
                seatId: targetSeat,
                patch: {
                  status: "empty",
                  runId: undefined,
                  taskSnippet: undefined,
                  startedAt: undefined,
                },
              });
            }

            gameEvents.emit("task-completed", taskId);
          }, 5000);
        }
      }
    },
    [refs],
  );

  const finalizeStoppedTask = useCallback(
    (runId: string, seatId?: string) => {
      const task = findTask(refs.tasks.current, runId);
      if (!task || task.status === "stopped" || task.status === "completed") return;
      refs.stoppedRunIds.current.add(task.runId ?? task.taskId);
      refs.dispatch.current({
        type: "UPDATE_TASK",
        taskId: runId,
        patch: {
          status: "stopped",
          completedAt: new Date().toISOString(),
          result: task.result ?? "Stopped by user",
        },
      });
      if (seatId) {
        refs.dispatch.current({
          type: "PATCH_SEAT_RUNTIME",
          seatId,
          patch: {
            status: "empty",
            runId: undefined,
            taskSnippet: undefined,
            startedAt: undefined,
          },
        });
      } else {
        refs.dispatch.current({ type: "SET_SEAT_STATUS", runId, status: "empty" });
      }
      refs.dispatch.current({
        type: "APPEND_CHAT",
        message: {
          id: chatId(),
          runId,
          role: "system",
          content: "Task stopped",
          timestamp: new Date().toISOString(),
          sessionKey: task.sessionKey,
        },
      });
      gameEvents.emit("task-aborted", runId);
    },
    [refs],
  );

  // task-ready: queue or send immediately
  useEffect(() => {
    return gameEvents.on("task-ready", (taskId, message, seatId) => {
      const task = findTask(refs.tasks.current, taskId);
      const sessionKey = task?.sessionKey ?? refs.activeSessionKey.current ?? MAIN_SESSION_KEY;
      const hasRunning = refs.tasks.current.some(
        (t) =>
          t.sessionKey === sessionKey &&
          t.taskId !== taskId &&
          (t.status === "running" || t.status === "submitted"),
      );
      if (hasRunning) {
        const queue = sessionQueueRef.current.get(sessionKey) ?? [];
        queue.push({ taskId, message, seatId });
        sessionQueueRef.current.set(sessionKey, queue);
        return;
      }
      sendTaskToGateway(taskId, message, seatId);
    });
  }, [sendTaskToGateway, refs]);

  // drain queue on completion/failure/abort
  useEffect(() => {
    const drain = (runId: string) => {
      const task = findTask(refs.tasks.current, runId);
      if (task?.sessionKey) drainSessionQueue(task.sessionKey);
    };
    const unsubComplete = gameEvents.on("task-completed", drain);
    const unsubFailed = gameEvents.on("task-failed", drain);
    const unsubAborted = gameEvents.on("task-aborted", drain);
    return () => {
      unsubComplete();
      unsubFailed();
      unsubAborted();
    };
  }, [drainSessionQueue, refs]);

  // task-routed: bind session to seat
  useEffect(() => {
    return gameEvents.on("task-routed", (taskId, seatId, actorName) => {
      refs.dispatch.current({ type: "UPDATE_TASK", taskId, patch: { seatId, actorName } });
      const task = findTask(refs.tasks.current, taskId);
      if (task?.sessionKey) refs.seatIdToSessionKey.current.set(seatId, task.sessionKey);
    });
  }, [refs]);

  // task-staged
  useEffect(() => {
    return gameEvents.on("task-staged", (taskId, stage, seatId) => {
      refs.dispatch.current({ type: "UPDATE_TASK", taskId, patch: { status: stage, seatId } });
      if (!seatId) return;
      refs.dispatch.current({
        type: "PATCH_SEAT_RUNTIME",
        seatId,
        patch: {
          status: stage === "returning" ? "returning" : "running",
          runId: taskId,
          taskSnippet: stage === "returning" ? "Returning to desk..." : "Queued task",
          startedAt: new Date().toISOString(),
        },
      });
    });
  }, [refs]);

  // stop-task
  useEffect(() => {
    return gameEvents.on("stop-task", async (runId, seatId) => {
      const task = findTask(refs.tasks.current, runId);
      if (!task) return;
      if (task.status === "queued" || task.status === "returning" || !task.runId) {
        finalizeStoppedTask(runId, seatId);
        return;
      }

      const client = refs.clientRef.current;
      if (!client || client.status !== "connected") {
        finalizeStoppedTask(runId, seatId);
        return;
      }

      finalizeStoppedTask(runId, seatId);
      try {
        await client.request(
          "chat.abort",
          { sessionKey: task.sessionKey, runId: task.runId },
          10000,
        );
      } catch {
        refs.dispatch.current({
          type: "APPEND_CHAT",
          message: {
            id: chatId(),
            runId,
            role: "system",
            content: "Stop task failed: gateway rejected the stop request",
            timestamp: new Date().toISOString(),
            sessionKey: task.sessionKey,
          },
        });
      }
    });
  }, [finalizeStoppedTask, refs]);

  return {
    assignTask,
    finalizeStoppedTask,
  };
}
