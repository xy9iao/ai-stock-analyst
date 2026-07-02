import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders its children and defaults to type=button", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: "Click me" })).toHaveAttribute("type", "button");
  });

  it("applies the primary (emerald) variant", () => {
    render(<Button variant="primary">Save</Button>);
    expect(screen.getByRole("button", { name: "Save" }).className).toContain("bg-emerald-600");
  });

  it("applies the danger (red) variant", () => {
    render(<Button variant="danger">Delete</Button>);
    expect(screen.getByRole("button", { name: "Delete" }).className).toContain("bg-red-600");
  });

  it("applies the small size", () => {
    render(
      <Button size="sm">Edit</Button>,
    );
    expect(screen.getByRole("button", { name: "Edit" }).className).toContain("h-8");
  });
});
