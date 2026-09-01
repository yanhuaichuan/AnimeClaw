import { describe, expect, it } from "vitest";

import { parseAnimePanel } from "@/features/anime/AnimeStudio";

describe("parseAnimePanel", () => {
  it("reads a search/panel token", () => {
    expect(parseAnimePanel("world")).toBe("world");
    expect(parseAnimePanel("qa")).toBe("qa");
  });

  it("reads a full studio path", () => {
    expect(parseAnimePanel("/projects/demo/anime/characters")).toBe("characters");
  });

  it("falls back to the shot editor", () => {
    expect(parseAnimePanel("/projects/demo/anime")).toBe("episodes");
    expect(parseAnimePanel("unknown")).toBe("episodes");
  });
});
