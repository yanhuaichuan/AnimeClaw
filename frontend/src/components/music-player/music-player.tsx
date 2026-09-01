// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  ChevronDown,
  ChevronUp,
  FolderPlus,
  HelpCircle,
  Link2,
  ListMusic,
  Minimize2,
  Pause,
  Play,
  SkipBack,
  SkipForward,
  Trash2,
  Upload,
  Volume2,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { parsePlaylistText, type PlaylistTrack } from "@/lib/playlist";
import { useMusicPlayerStore } from "@/stores/music-player-store";

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function trackFromFile(file: File): PlaylistTrack {
  return {
    id: `local-${file.name}-${file.size}-${file.lastModified}`,
    title: file.name.replace(/\.[^.]+$/, ""),
    artist: "",
    url: URL.createObjectURL(file),
    local: true,
  };
}

export function MusicPlayer() {
  const { t } = useTranslation();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const playlistInputRef = useRef<HTMLInputElement | null>(null);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [urlDraft, setUrlDraft] = useState("");
  const [helpOpen, setHelpOpen] = useState(false);

  const tracks = useMusicPlayerStore((s) => s.tracks);
  const currentIndex = useMusicPlayerStore((s) => s.currentIndex);
  const playing = useMusicPlayerStore((s) => s.playing);
  const expanded = useMusicPlayerStore((s) => s.expanded);
  const minimized = useMusicPlayerStore((s) => s.minimized);
  const volume = useMusicPlayerStore((s) => s.volume);
  const setPlaying = useMusicPlayerStore((s) => s.setPlaying);
  const setExpanded = useMusicPlayerStore((s) => s.setExpanded);
  const setMinimized = useMusicPlayerStore((s) => s.setMinimized);
  const setCurrentIndex = useMusicPlayerStore((s) => s.setCurrentIndex);
  const setVolume = useMusicPlayerStore((s) => s.setVolume);
  const appendTracks = useMusicPlayerStore((s) => s.appendTracks);
  const setTracks = useMusicPlayerStore((s) => s.setTracks);
  const removeTrack = useMusicPlayerStore((s) => s.removeTrack);
  const clearTracks = useMusicPlayerStore((s) => s.clearTracks);
  const next = useMusicPlayerStore((s) => s.next);
  const prev = useMusicPlayerStore((s) => s.prev);

  const current = tracks[currentIndex] ?? null;

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.volume = volume;
  }, [volume]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !current) return;
    if (audio.src !== current.url) {
      audio.src = current.url;
    }
    if (playing) {
      void audio.play().catch(() => setPlaying(false));
    } else {
      audio.pause();
    }
  }, [current, playing, setPlaying]);

  useEffect(() => {
    if (tracks.length) return;
    let cancelled = false;
    void fetch("/music/demo-playlist.json")
      .then((response) => response.text())
      .then((text) => {
        if (cancelled) return;
        const parsed = parsePlaylistText(text, "demo");
        if (parsed.tracks.length && useMusicPlayerStore.getState().tracks.length === 0) {
          setTracks(parsed.tracks, 0, false);
        }
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [setTracks, tracks.length]);

  const addLocalFiles = (files: FileList | null) => {
    if (!files?.length) return;
    const incoming = Array.from(files)
      .filter((file) => file.type.startsWith("audio/") || /\.(mp3|m4a|aac|ogg|opus|wav|flac)$/i.test(file.name))
      .map(trackFromFile);
    if (!incoming.length) return;
    appendTracks(incoming);
    toast.success(t("musicPlayer.filesAdded", { count: incoming.length }));
  };

  const addUrl = () => {
    const url = urlDraft.trim();
    if (!/^https?:\/\//i.test(url)) {
      toast.error(t("musicPlayer.urlInvalid"));
      return;
    }
    appendTracks([
      {
        id: `url-${Date.now()}`,
        title: decodeURIComponent(url.split("/").pop()?.split("?")[0] || t("musicPlayer.untitled")),
        artist: "",
        url,
      },
    ]);
    setUrlDraft("");
    toast.success(t("musicPlayer.added"));
  };

  const importPlaylistFile = async (file: File | undefined) => {
    if (!file) return;
    try {
      const parsed = parsePlaylistText(await file.text(), file.name);
      if (!parsed.tracks.length) {
        toast.error(t("musicPlayer.importEmpty"));
        return;
      }
      appendTracks(parsed.tracks);
      toast.success(t("musicPlayer.importSuccess", { count: parsed.tracks.length }));
    } catch {
      toast.error(t("musicPlayer.importFailed"));
    }
  };

  const loadDemo = async () => {
    const response = await fetch("/music/demo-playlist.json");
    const parsed = parsePlaylistText(await response.text(), "demo");
    if (!parsed.tracks.length) {
      toast.error(t("musicPlayer.importEmpty"));
      return;
    }
    setTracks(parsed.tracks, 0);
    toast.success(t("musicPlayer.demoLoaded"));
  };

  return (
    <div className="pointer-events-none fixed right-4 bottom-12 z-45 flex flex-col items-end">
      <audio
        ref={audioRef}
        preload="none"
        onTimeUpdate={(event) => setProgress(event.currentTarget.currentTime)}
        onDurationChange={(event) => setDuration(event.currentTarget.duration || 0)}
        onEnded={() => next()}
      />
      <div
        className={cn(
          "pointer-events-auto overflow-hidden rounded-2xl border border-border bg-card/95 text-foreground shadow-lg backdrop-blur-xl",
          minimized
            ? "rounded-full"
            : expanded
              ? "w-[min(360px,calc(100vw-2rem))]"
              : "w-[min(280px,calc(100vw-2rem))]",
        )}
      >
        {minimized ? (
          <div className="flex items-center gap-0.5 p-1">
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              aria-label={playing ? t("musicPlayer.pause") : t("musicPlayer.play")}
              disabled={!current}
              onClick={() => setPlaying(!playing)}
            >
              {playing ? <Pause className="size-4" /> : <Play className="size-4" />}
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              aria-label={t("musicPlayer.restore")}
              onClick={() => setMinimized(false)}
            >
              <ListMusic className="size-4 text-primary" />
            </Button>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2 px-3 py-2">
              <ListMusic className="size-4 shrink-0 text-primary" aria-hidden />
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-semibold">
                  {current?.title ?? t("musicPlayer.title")}
                </p>
                <p className="truncate text-[11px] text-muted-foreground">
                  {current?.artist || (current ? t("musicPlayer.unknownArtist") : t("musicPlayer.empty"))}
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label={playing ? t("musicPlayer.pause") : t("musicPlayer.play")}
                disabled={!current}
                onClick={() => setPlaying(!playing)}
              >
                {playing ? <Pause className="size-4" /> : <Play className="size-4" />}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label={expanded ? t("musicPlayer.collapse") : t("musicPlayer.expand")}
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? <ChevronDown className="size-4" /> : <ChevronUp className="size-4" />}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label={t("musicPlayer.minimize")}
                onClick={() => setMinimized(true)}
              >
                <Minimize2 className="size-4" />
              </Button>
            </div>

        <div className="px-3 pb-2">
          <input
            type="range"
            min={0}
            max={duration || 0}
            step={0.1}
            value={Math.min(progress, duration || 0)}
            disabled={!current}
            aria-label={t("musicPlayer.nowPlaying")}
            className="h-1 w-full accent-primary"
            onChange={(event) => {
              const nextTime = Number(event.target.value);
              if (audioRef.current) audioRef.current.currentTime = nextTime;
              setProgress(nextTime);
            }}
          />
          <div className="mt-1 flex justify-between text-[10px] text-muted-foreground">
            <span>{formatTime(progress)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {expanded ? (
          <div className="border-t border-border px-3 py-3">
            <div className="mb-3 flex items-center gap-1">
              <Button type="button" variant="ghost" size="icon-sm" aria-label={t("musicPlayer.prev")} onClick={prev}>
                <SkipBack className="size-4" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label={playing ? t("musicPlayer.pause") : t("musicPlayer.play")}
                disabled={!current}
                onClick={() => setPlaying(!playing)}
              >
                {playing ? <Pause className="size-4" /> : <Play className="size-4" />}
              </Button>
              <Button type="button" variant="ghost" size="icon-sm" aria-label={t("musicPlayer.next")} onClick={next}>
                <SkipForward className="size-4" />
              </Button>
              <Volume2 className="ml-1 size-3.5 text-muted-foreground" aria-hidden />
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={volume}
                aria-label={t("musicPlayer.volume")}
                className="h-1 w-20 accent-primary"
                onChange={(event) => setVolume(Number(event.target.value))}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="ml-auto"
                aria-label={t("musicPlayer.helpTitle")}
                onClick={() => setHelpOpen((open) => !open)}
              >
                <HelpCircle className="size-4" />
              </Button>
            </div>

            {helpOpen ? (
              <div className="mb-3 rounded-xl bg-muted/50 px-3 py-2 text-xs leading-5 text-muted-foreground">
                <p className="mb-1 font-semibold text-foreground">{t("musicPlayer.helpTitle")}</p>
                <p>{t("musicPlayer.helpBody")}</p>
              </div>
            ) : null}

            <div className="mb-3 flex flex-wrap gap-1.5">
              <Button type="button" size="sm" variant="outline" onClick={() => fileInputRef.current?.click()}>
                <FolderPlus className="size-3.5" />
                {t("musicPlayer.addFiles")}
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={() => playlistInputRef.current?.click()}>
                <Upload className="size-3.5" />
                {t("musicPlayer.importPlaylist")}
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={() => void loadDemo()}>
                {t("musicPlayer.loadDemo")}
              </Button>
              {tracks.length ? (
                <Button type="button" size="sm" variant="ghost" onClick={clearTracks}>
                  <Trash2 className="size-3.5" />
                  {t("musicPlayer.clear")}
                </Button>
              ) : null}
            </div>

            <div className="mb-3 flex gap-1.5">
              <Input
                value={urlDraft}
                onChange={(event) => setUrlDraft(event.target.value)}
                placeholder={t("musicPlayer.urlPlaceholder")}
                className="h-8 text-xs"
                onKeyDown={(event) => {
                  if (event.key === "Enter") addUrl();
                }}
              />
              <Button type="button" size="sm" variant="outline" onClick={addUrl}>
                <Link2 className="size-3.5" />
              </Button>
            </div>

            <p className="mb-1.5 text-[11px] font-medium text-muted-foreground">{t("musicPlayer.playlist")}</p>
            <ul className="max-h-44 space-y-1 overflow-y-auto pr-1">
              {tracks.length === 0 ? (
                <li className="rounded-lg px-2 py-3 text-xs text-muted-foreground">{t("musicPlayer.empty")}</li>
              ) : (
                tracks.map((track, index) => (
                  <li key={track.id}>
                    <div
                      className={cn(
                        "flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs",
                        index === currentIndex ? "bg-primary/12 text-foreground" : "hover:bg-muted/60",
                      )}
                    >
                      <button
                        type="button"
                        className="min-w-0 flex-1 truncate text-left"
                        onClick={() => setCurrentIndex(index)}
                      >
                        <span className="block truncate font-medium">{track.title}</span>
                        <span className="block truncate text-[10px] text-muted-foreground">
                          {track.artist || (track.local ? t("musicPlayer.addFiles") : t("musicPlayer.unknownArtist"))}
                        </span>
                      </button>
                      <button
                        type="button"
                        className="shrink-0 text-muted-foreground hover:text-foreground"
                        aria-label={t("musicPlayer.remove")}
                        onClick={() => removeTrack(track.id)}
                      >
                        <X className="size-3.5" />
                      </button>
                    </div>
                  </li>
                ))
              )}
            </ul>
          </div>
        ) : null}
          </>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*,.mp3,.m4a,.aac,.ogg,.wav,.flac"
        multiple
        className="hidden"
        onChange={(event) => {
          addLocalFiles(event.target.files);
          event.target.value = "";
        }}
      />
      <input
        ref={playlistInputRef}
        type="file"
        accept=".json,.m3u,.m3u8,application/json,audio/x-mpegurl"
        className="hidden"
        onChange={(event) => {
          void importPlaylistFile(event.target.files?.[0]);
          event.target.value = "";
        }}
      />
    </div>
  );
}
