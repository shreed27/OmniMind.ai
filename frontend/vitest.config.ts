import { defineConfig } from "vitest/config/react";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
  },
});
