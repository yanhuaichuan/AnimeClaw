// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { beforeEach, describe, expect, it } from "vitest";

import { useMusicPlayerStore } from "@/stores/music-player-store";

beforeEach(() => {
  useMusicPlayerStore.setState({
    tracks: [],
    currentIndex: 0,
    playing: false,
    expanded: false,
    minimized: false,
    volume: 0.72,
  });
});

describe("music-player-store minimize", () => {
  it("minimizing collapses the playlist panel", () => {
    const { setExpanded, setMinimized } = useMusicPlayerStore.getState();
    setExpanded(true);
    expect(useMusicPlayerStore.getState().expanded).toBe(true);

    setMinimized(true);
    expect(useMusicPlayerStore.getState().minimized).toBe(true);
    expect(useMusicPlayerStore.getState().expanded).toBe(false);
  });

  it("expanding the playlist restores from the minimized pill", () => {
    const { setMinimized, setExpanded } = useMusicPlayerStore.getState();
    setMinimized(true);

    setExpanded(true);
    expect(useMusicPlayerStore.getState().expanded).toBe(true);
    expect(useMusicPlayerStore.getState().minimized).toBe(false);
  });

  it("restoring keeps the compact bar instead of forcing the playlist open", () => {
    const { setMinimized } = useMusicPlayerStore.getState();
    setMinimized(true);
    setMinimized(false);
    expect(useMusicPlayerStore.getState().minimized).toBe(false);
    expect(useMusicPlayerStore.getState().expanded).toBe(false);
  });
});
