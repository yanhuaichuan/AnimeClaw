// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { MusicPlayer } from "@/components/music-player/music-player";
import { useMusicPlayerStore } from "@/stores/music-player-store";

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

beforeEach(() => {
  vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue(undefined);
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => undefined);
  useMusicPlayerStore.setState({
    tracks: [{ id: "1", title: "Gymnopedie", artist: "Kevin MacLeod", url: "https://example.com/a.mp3" }],
    currentIndex: 0,
    playing: false,
    expanded: false,
    minimized: false,
    volume: 0.72,
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("MusicPlayer", () => {
  it("shrinks to a pill and restores the compact bar", async () => {
    const user = userEvent.setup();
    render(<MusicPlayer />);

    expect(screen.getByText("Gymnopedie")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "musicPlayer.minimize" }));
    expect(screen.queryByText("Gymnopedie")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "musicPlayer.restore" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "musicPlayer.play" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "musicPlayer.restore" }));
    expect(screen.getByText("Gymnopedie")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "musicPlayer.minimize" })).toBeInTheDocument();
  });
});
