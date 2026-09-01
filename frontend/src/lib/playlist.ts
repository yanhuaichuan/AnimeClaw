// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan

export type PlaylistTrack = {
  id: string;
  title: string;
  artist: string;
  url: string;
  local?: boolean;
};

export type ParsedPlaylist = {
  name: string;
  tracks: PlaylistTrack[];
};

const AUDIO_EXT = /\.(mp3|m4a|aac|ogg|opus|wav|flac)(\?|$)/i;

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `track-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function isHttpUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

export function isPlayableAudioUrl(value: string): boolean {
  if (!isHttpUrl(value) && !value.startsWith("blob:")) return false;
  if (value.startsWith("blob:")) return true;
  return AUDIO_EXT.test(value) || /audio\//i.test(value) || isHttpUrl(value);
}

function normalizeTrack(
  input: { title?: string; artist?: string; url?: string; src?: string; name?: string },
  fallbackTitle: string,
): PlaylistTrack | null {
  const url = String(input.url ?? input.src ?? "").trim();
  if (!url || !isPlayableAudioUrl(url)) return null;
  return {
    id: newId(),
    title: String(input.title ?? input.name ?? fallbackTitle).trim() || fallbackTitle,
    artist: String(input.artist ?? "").trim(),
    url,
  };
}

export function parsePlaylistText(text: string, filename = "playlist"): ParsedPlaylist {
  const trimmed = text.trim();
  if (!trimmed) return { name: filename, tracks: [] };

  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    const data = JSON.parse(trimmed) as
      | { name?: string; title?: string; tracks?: unknown[] }
      | unknown[];
    const list = Array.isArray(data) ? data : data.tracks;
    const name = Array.isArray(data)
      ? filename.replace(/\.[^.]+$/, "")
      : String(data.name ?? data.title ?? filename);
    const tracks = (list ?? [])
      .map((item, index) =>
        item && typeof item === "object"
          ? normalizeTrack(item as { title?: string; url?: string }, `曲目 ${index + 1}`)
          : typeof item === "string"
            ? normalizeTrack({ url: item }, `曲目 ${index + 1}`)
            : null,
      )
      .filter((track): track is PlaylistTrack => Boolean(track));
    return { name, tracks };
  }

  const lines = trimmed.split(/\r?\n/);
  const tracks: PlaylistTrack[] = [];
  let pendingTitle = "";
  for (const raw of lines) {
    const line = raw.trim();
    if (!line || line.startsWith("#EXTM3U")) continue;
    if (line.startsWith("#EXTINF:")) {
      const meta = line.slice(line.indexOf(",") + 1).trim();
      pendingTitle = meta;
      continue;
    }
    if (line.startsWith("#")) continue;
    const track = normalizeTrack(
      { url: line, title: pendingTitle || undefined },
      `曲目 ${tracks.length + 1}`,
    );
    pendingTitle = "";
    if (track) tracks.push(track);
  }
  return { name: filename.replace(/\.[^.]+$/, ""), tracks };
}
