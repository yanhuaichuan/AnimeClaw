// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { quotaSafeStateStorage } from "@/lib/localStorageQuota";
import type { PlaylistTrack } from "@/lib/playlist";

type MusicPlayerState = {
  tracks: PlaylistTrack[];
  currentIndex: number;
  playing: boolean;
  expanded: boolean;
  minimized: boolean;
  volume: number;
  setTracks: (tracks: PlaylistTrack[], startIndex?: number, play?: boolean) => void;
  appendTracks: (tracks: PlaylistTrack[]) => void;
  removeTrack: (id: string) => void;
  clearTracks: () => void;
  setCurrentIndex: (index: number) => void;
  setPlaying: (playing: boolean) => void;
  setExpanded: (expanded: boolean) => void;
  setMinimized: (minimized: boolean) => void;
  setVolume: (volume: number) => void;
  next: () => void;
  prev: () => void;
};

function persistableTracks(tracks: PlaylistTrack[]): PlaylistTrack[] {
  return tracks.filter((track) => !track.local && !track.url.startsWith("blob:"));
}

export const useMusicPlayerStore = create<MusicPlayerState>()(
  persist(
    (set, get) => ({
      tracks: [],
      currentIndex: 0,
      playing: false,
      expanded: false,
      minimized: false,
      volume: 0.72,
      setTracks: (tracks, startIndex = 0, play = true) =>
        set({
          tracks,
          currentIndex: tracks.length ? Math.min(Math.max(0, startIndex), tracks.length - 1) : 0,
          playing: play && tracks.length > 0,
        }),
      appendTracks: (incoming) =>
        set((state) => ({
          tracks: [...state.tracks, ...incoming],
          playing: state.playing || (state.tracks.length === 0 && incoming.length > 0),
        })),
      removeTrack: (id) =>
        set((state) => {
          const index = state.tracks.findIndex((track) => track.id === id);
          if (index < 0) return state;
          const tracks = state.tracks.filter((track) => track.id !== id);
          let currentIndex = state.currentIndex;
          if (index < currentIndex) currentIndex -= 1;
          if (currentIndex >= tracks.length) currentIndex = Math.max(0, tracks.length - 1);
          return { tracks, currentIndex, playing: tracks.length > 0 && state.playing };
        }),
      clearTracks: () => set({ tracks: [], currentIndex: 0, playing: false }),
      setCurrentIndex: (index) => {
        const { tracks } = get();
        if (!tracks.length) return;
        set({ currentIndex: Math.min(Math.max(0, index), tracks.length - 1), playing: true });
      },
      setPlaying: (playing) => set({ playing }),
      setExpanded: (expanded) => set({ expanded: expanded, minimized: expanded ? false : get().minimized }),
      setMinimized: (minimized) => set({ minimized, expanded: minimized ? false : get().expanded }),
      setVolume: (volume) => set({ volume: Math.min(1, Math.max(0, volume)) }),
      next: () => {
        const { tracks, currentIndex } = get();
        if (!tracks.length) return;
        set({ currentIndex: (currentIndex + 1) % tracks.length, playing: true });
      },
      prev: () => {
        const { tracks, currentIndex } = get();
        if (!tracks.length) return;
        set({
          currentIndex: (currentIndex - 1 + tracks.length) % tracks.length,
          playing: true,
        });
      },
    }),
    {
      name: "animeclaw-music-player-v2",
      storage: createJSONStorage(() => quotaSafeStateStorage),
      partialize: (state) => ({
        tracks: persistableTracks(state.tracks),
        currentIndex: state.currentIndex,
        volume: state.volume,
        expanded: state.expanded,
        minimized: state.minimized,
      }),
    },
  ),
);
