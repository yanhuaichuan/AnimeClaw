// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { describe, expect, it } from "vitest";

import { parsePlaylistText } from "@/lib/playlist";

describe("parsePlaylistText", () => {
  it("parses JSON playlists", () => {
    const parsed = parsePlaylistText(
      JSON.stringify({
        name: "夜戏",
        tracks: [{ title: "雨夜", artist: "苏璃", url: "https://example.com/rain.mp3" }],
      }),
    );
    expect(parsed.name).toBe("夜戏");
    expect(parsed.tracks).toHaveLength(1);
    expect(parsed.tracks[0]?.title).toBe("雨夜");
  });

  it("parses M3U playlists", () => {
    const parsed = parsePlaylistText(
      "#EXTM3U\n#EXTINF:180,林夏 - 第一封信\nhttps://example.com/letter.m4a\n",
      "inbox.m3u",
    );
    expect(parsed.tracks).toHaveLength(1);
    expect(parsed.tracks[0]?.title).toBe("林夏 - 第一封信");
    expect(parsed.tracks[0]?.url).toBe("https://example.com/letter.m4a");
  });
});
