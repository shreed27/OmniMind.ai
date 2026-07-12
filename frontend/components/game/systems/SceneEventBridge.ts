import { gameEvents } from "@/lib/events";
import type { WorkerManager } from "./WorkerManager";
import type { InteractionManager } from "./InteractionManager";

/**
 * Wires up all gameEvents listeners that bridge HUD/store actions into the Phaser scene.
 * Returns a cleanup function that unsubscribes all listeners.
 */
export function initSceneEventBridge(
  workerManager: WorkerManager,
  interactionManager: InteractionManager,
  sessionBindings: Map<string, string>,
  setTerminalOpen: (open: boolean) => void,
): () => void {
  const unsubs: Array<() => void> = [];

  unsubs.push(
    gameEvents.on("seat-configs-updated", (seats) => {
      workerManager.syncWorkers(seats, (w) => interactionManager.clearIfNearest(w));
    }),
  );

  unsubs.push(
    gameEvents.on("task-assigned", (taskId, message, seatId, sessionKey) => {
      // Route by explicit seatId, or by session binding (session -> character), or find idle worker
      const boundSeatId = sessionKey ? sessionBindings.get(sessionKey) : undefined;
      const targetSeatId = seatId ?? boundSeatId;
      const worker = workerManager.findBySeatId(targetSeatId) ?? workerManager.findIdle();
      if (!worker) {
        gameEvents.emit("task-ready", taskId, message, seatId);
        return;
      }
      // Bind session to character when character gets the task
      if (sessionKey) sessionBindings.set(sessionKey, worker.seatId);
      gameEvents.emit("task-routed", taskId, worker.seatId, worker.label);
      // When routed to this worker (explicit seat or session-bound) and they're busy: queue on worker
      if (worker.status === "working" && worker.assignedRunId) {
        gameEvents.emit("task-staged", taskId, "queued", worker.seatId);
        worker.enqueueTask(taskId, message, () =>
          gameEvents.emit("task-ready", taskId, message, worker.seatId),
        );
        workerManager.runWorkerMap.set(taskId, worker);
        return;
      }

      if (worker.isAwayFromDesk()) {
        gameEvents.emit("task-staged", taskId, "returning", worker.seatId);
      }

      const ready = () => gameEvents.emit("task-ready", taskId, message, worker.seatId);
      worker.assignTask(taskId, message, ready);
      workerManager.runWorkerMap.set(taskId, worker);
    }),
  );

  unsubs.push(
    gameEvents.on("task-bound", (taskId, runId) => {
      const worker = workerManager.runWorkerMap.get(taskId);
      if (!worker) return;
      worker.rebindAssignedRun(taskId, runId);
      workerManager.runWorkerMap.delete(taskId);
      workerManager.runWorkerMap.set(runId, worker);
    }),
  );

  unsubs.push(
    gameEvents.on("task-bubble", (runId, text, ttl) => {
      const worker = workerManager.runWorkerMap.get(runId);
      if (worker) worker.showBubble(text, ttl ?? 5000);
    }),
  );

  unsubs.push(
    gameEvents.on("task-completed", (runId) => {
      const worker = workerManager.runWorkerMap.get(runId);
      if (worker) {
        worker.completeTask();
        workerManager.runWorkerMap.delete(runId);
      }
    }),
  );

  unsubs.push(
    gameEvents.on("task-failed", (runId) => {
      const worker = workerManager.runWorkerMap.get(runId);
      if (worker) {
        worker.failTask();
        workerManager.runWorkerMap.delete(runId);
      }
    }),
  );

  unsubs.push(
    gameEvents.on("task-aborted", (runId) => {
      const worker = workerManager.runWorkerMap.get(runId);
      if (!worker) return;
      if (worker.abortTask(runId)) {
        workerManager.runWorkerMap.delete(runId);
      }
    }),
  );

  unsubs.push(
    gameEvents.on("subagent-assigned", (runId, _parentRunId, label, seatId?) => {
      const worker = seatId
        ? (workerManager.findBySeatId(seatId) ?? workerManager.findIdle())
        : workerManager.findIdle();
      if (!worker) return;
      worker.assignTask(runId, `[Sub] ${label}`);
      workerManager.runWorkerMap.set(runId, worker);
    }),
  );

  unsubs.push(
    gameEvents.on("terminal-closed", () => {
      setTerminalOpen(false);
    }),
  );

  // --- Cinematic Board Meeting Events ---
  unsubs.push(
    gameEvents.on("delegates-meeting" as any, () => {
      const ceo = workerManager.findBySeatId("s1");
      if (!ceo) return;

      // Mathematically aligned spots in the open, guaranteed walkable area of CEO Alice's office
      const spots = [
        { x: ceo.homeX - 54, y: ceo.homeY + 112, facing: "right" as const }, // CTO Bob
        { x: ceo.homeX + 54, y: ceo.homeY + 112, facing: "left" as const },  // COO Carol
        { x: ceo.homeX - 28, y: ceo.homeY + 144, facing: "right" as const }, // CFO Dave
        { x: ceo.homeX + 28, y: ceo.homeY + 144, facing: "left" as const },  // CMO Eve
      ];

      const otherWorkers = workerManager.workers.filter((w) => w.seatId !== "s1");
      otherWorkers.forEach((worker, i) => {
        const spot = spots[i % spots.length];
        worker.stopIdleActivity();
        worker.canWander = false;
        worker.navigateTo(spot.x, spot.y, { x: ceo.homeX, y: ceo.homeY });
        worker.onArrival = () => {
          worker.sprite.play(`${worker.spriteKey}:idle-${spot.facing}`);
        };
      });
    }),
  );

  unsubs.push(
    gameEvents.on("delegates-return" as any, () => {
      workerManager.workers.forEach((worker) => {
        worker.canWander = true;
        worker.navigateHome();
      });
    }),
  );

  unsubs.push(
    gameEvents.on("seat-bubble" as any, (seatId: string, text: string, ttl?: number) => {
      const worker = workerManager.findBySeatId(seatId);
      if (worker) worker.showBubble(text, ttl ?? 5000);
    }),
  );

  return () => {
    for (const unsub of unsubs) unsub();
  };
}
