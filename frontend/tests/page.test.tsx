import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "./page";

describe("page", () => {
  it("renders homepage", () => {
    render(<Home />);
    expect(screen.getByText("OmniMind.ai")).toBeDefined();
    expect(screen.getByText("Operating System for Autonomous Organizations")).toBeDefined();
  });
});
