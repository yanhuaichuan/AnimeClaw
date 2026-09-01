// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  BookOpen,
  Camera,
  Clapperboard,
  Download,
  Loader2,
  Palette,
  Play,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  useAnimeCatalog,
  useAnimeCharacters,
  useAnimeContinuity,
  useAnimeCost,
  useAnimeDirector,
  useAnimeEpisode,
  useAnimePreview,
  useAnimeQA,
  useAnimeStyle,
  useAnimeWorld,
  useExportAnimeEpisode,
  useRepairAnimeShot,
  useSaveAnimeShot,
  useSaveAnimeStyle,
  useSaveAnimeWorld,
  useSeedTenShotDemo,
} from "@/lib/queries/anime";
import { cn } from "@/lib/utils";
import type { AnimePanel, AnimeShot, LockKey, StyleBible } from "@/types/anime";

import "./anime-studio.css";

const LOCKS: LockKey[] = ["character", "costume", "scene", "style", "camera", "lighting"];
const INSPECTOR_TABS = ["character", "acting", "camera", "image", "voice"] as const;

export function AnimeStudio({
  project,
  panel,
  onPanelChange,
}: {
  project: string;
  panel: AnimePanel;
  onPanelChange: (panel: AnimePanel) => void;
}) {
  const { t } = useTranslation();
  const [episode] = useState(1);
  const [selectedShotId, setSelectedShotId] = useState<string | null>(null);
  const [inspector, setInspector] = useState<(typeof INSPECTOR_TABS)[number]>("character");
  const [tier, setTier] = useState("preview");

  const catalog = useAnimeCatalog();
  const world = useAnimeWorld(project);
  const style = useAnimeStyle(project);
  const characters = useAnimeCharacters(project);
  const episodeQuery = useAnimeEpisode(project, episode);
  const preview = useAnimePreview(project, episode);
  const qa = useAnimeQA(project, episode);
  const cost = useAnimeCost(project, episode, tier);
  const seedDemo = useSeedTenShotDemo(project);
  const exportEpisode = useExportAnimeEpisode(project, episode);
  const continuity = useAnimeContinuity(project, episode);
  const director = useAnimeDirector(project, episode);
  const repair = useRepairAnimeShot(project, episode);
  const saveShot = useSaveAnimeShot(project, episode);
  const saveWorld = useSaveAnimeWorld(project);
  const saveStyle = useSaveAnimeStyle(project);

  const bundle = episodeQuery.data?.data;
  const shots = bundle?.shots ?? [];
  const selected = shots.find((shot) => shot.id === selectedShotId) ?? shots[0] ?? null;
  const bible = characters.data?.data?.[0] ?? null;
  const worldData = world.data?.data;
  const styleData = style.data?.data;
  const busy = seedDemo.isPending || exportEpisode.isPending || continuity.isPending;

  const nav = useMemo(
    () =>
      [
        { id: "episodes" as const, label: t("anime.nav.episodes"), icon: Clapperboard },
        { id: "world" as const, label: t("anime.nav.world"), icon: BookOpen },
        { id: "characters" as const, label: t("anime.nav.characters"), icon: Users },
        { id: "styles" as const, label: t("anime.nav.styles"), icon: Palette },
        { id: "story" as const, label: t("anime.nav.story"), icon: Sparkles },
        { id: "qa" as const, label: t("anime.nav.qa"), icon: ShieldCheck },
      ],
    [t],
  );

  const runDemo = async () => {
    try {
      const result = await seedDemo.mutateAsync();
      setSelectedShotId(result.data?.shots[0]?.id ?? "shot-01");
      onPanelChange("episodes");
      toast.success(t("anime.toast.demoReady"));
    } catch (error) {
      toast.error(error instanceof Error ? error.message : t("anime.toast.demoFailed"));
    }
  };

  const runExport = async () => {
    try {
      const result = await exportEpisode.mutateAsync();
      const blob = new Blob([JSON.stringify(result.data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${project}-ep${String(episode).padStart(3, "0")}.json`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success(t("anime.toast.exported"));
    } catch (error) {
      toast.error(error instanceof Error ? error.message : t("anime.toast.exportFailed"));
    }
  };

  return (
    <div className="anime-studio">
      <aside className="anime-studio__rail">
        <div className="anime-studio__brand">
          <span className="anime-studio__brand-kicker">{t("anime.productEn")}</span>
          <span className="anime-studio__brand-title">{t("anime.productZh")}</span>
        </div>
        {nav.map((item) => (
          <button
            key={item.id}
            type="button"
            className="anime-studio__nav-btn"
            data-active={panel === item.id}
            onClick={() => onPanelChange(item.id)}
          >
            <item.icon className="size-3.5" />
            {item.label}
          </button>
        ))}
      </aside>

      <section className="anime-studio__stage">
        <header className="anime-studio__toolbar">
          <div>
            <h1>{t(`anime.panels.${panel}.title`)}</h1>
            <p>{t(`anime.panels.${panel}.subtitle`)}</p>
          </div>
          <div className="anime-studio__actions">
            <select
              className="h-8 rounded-full border border-white/10 bg-transparent px-3 text-xs"
              value={tier}
              onChange={(event) => setTier(event.target.value)}
            >
              <option value="draft">{t("anime.tier.draft")}</option>
              <option value="preview">{t("anime.tier.preview")}</option>
              <option value="final">{t("anime.tier.final")}</option>
            </select>
            <Button size="sm" variant="outline" onClick={() => void runDemo()} disabled={busy}>
              {seedDemo.isPending ? <Loader2 className="animate-spin" /> : <Sparkles />}
              {t("anime.actions.tenShot")}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() =>
                continuity.mutate(undefined, {
                  onSuccess: () => toast.success(t("anime.toast.continuityDone")),
                })
              }
              disabled={!shots.length || busy}
            >
              <ShieldCheck />
              {t("anime.actions.continuity")}
            </Button>
            <Button size="sm" variant="outline" onClick={() => void runExport()} disabled={!shots.length}>
              <Download />
              {t("anime.actions.export")}
            </Button>
          </div>
        </header>

        <div className="anime-studio__board">
          {panel === "world" ? (
            <WorldForm
              world={worldData}
              saving={saveWorld.isPending}
              onSave={(next) =>
                saveWorld.mutate(next, { onSuccess: () => toast.success(t("anime.toast.saved")) })
              }
            />
          ) : null}
          {panel === "styles" ? (
            <StyleForm
              style={styleData}
              saving={saveStyle.isPending}
              onSave={(next) =>
                saveStyle.mutate(next, { onSuccess: () => toast.success(t("anime.toast.saved")) })
              }
            />
          ) : null}
          {panel === "characters" ? <CharacterSheet bible={bible} /> : null}
          {panel === "story" ? (
            <StoryPanel
              hook={bundle?.episode.hook ?? ""}
              cliffhanger={bundle?.episode.cliffhanger ?? ""}
              world={worldData?.world ?? ""}
            />
          ) : null}
          {panel === "qa" ? <QAPanel score={qa.data?.data} /> : null}
          {panel === "episodes" || panel === "studio" ? (
            shots.length ? (
              <div className="anime-studio__storyboard">
                {shots.map((shot, index) => (
                  <button
                    key={shot.id}
                    type="button"
                    className="anime-shot-card"
                    data-active={selected?.id === shot.id}
                    onClick={() => setSelectedShotId(shot.id)}
                  >
                    <div className="anime-shot-card__frame">
                      <span className="anime-shot-card__index">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                    </div>
                    <div className="anime-shot-card__meta">
                      <strong>{shot.title || shot.id}</strong>
                      <span>
                        {shot.camera.shot_size.replaceAll("_", " ")} · {shot.acting.expression} ·{" "}
                        {shot.acting.pose.replaceAll("_", " ")}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="anime-empty">
                <h2>{t("anime.empty.title")}</h2>
                <p>{t("anime.empty.body")}</p>
                <Button onClick={() => void runDemo()} disabled={busy}>
                  {seedDemo.isPending ? <Loader2 className="animate-spin" /> : <Play />}
                  {t("anime.empty.cta")}
                </Button>
              </div>
            )
          ) : null}
        </div>

        {shots.length ? (
          <div className="anime-studio__timeline" aria-label={t("anime.timeline")}>
            {shots.map((shot, index) => (
              <button
                key={shot.id}
                type="button"
                className="anime-studio__tick"
                data-active={selected?.id === shot.id}
                onClick={() => setSelectedShotId(shot.id)}
              >
                {String(index + 1).padStart(2, "0")} {shot.title}
              </button>
            ))}
          </div>
        ) : null}
      </section>

      <aside className="anime-studio__inspector">
        <div className="anime-studio__tabs">
          {INSPECTOR_TABS.map((tab) => (
            <button
              key={tab}
              type="button"
              data-active={inspector === tab}
              onClick={() => setInspector(tab)}
            >
              {t(`anime.inspector.${tab}`)}
            </button>
          ))}
        </div>
        <div className="anime-studio__fields">
          {selected && inspector === "character" ? (
            <CharacterInspect bibleName={bible?.name} shot={selected} />
          ) : null}
          {selected && inspector === "acting" ? (
            <ActingInspect
              shot={selected}
              poses={catalog.data?.data?.poses ?? []}
              expressions={catalog.data?.data?.expressions ?? []}
              onAct={(emotion, pose) =>
                applyActing(saveShot, selected, emotion, pose)
              }
            />
          ) : null}
          {selected && inspector === "camera" ? (
            <CameraInspect
              shot={selected}
              cameras={catalog.data?.data?.cameras ?? []}
              onChange={(next) => saveShot.mutate(next)}
            />
          ) : null}
          {selected && inspector === "image" ? (
            <ImageInspect
              shot={selected}
              onLock={(lock) =>
                saveShot.mutate({
                  ...selected,
                  locks: selected.locks.includes(lock)
                    ? selected.locks.filter((item) => item !== lock)
                    : [...selected.locks, lock],
                })
              }
              onRepair={() =>
                repair.mutate(selected.id, {
                  onSuccess: () => toast.success(t("anime.toast.repaired")),
                })
              }
            />
          ) : null}
          {selected && inspector === "voice" ? (
            <VoiceInspect
              shot={selected}
              cost={cost.data?.data}
              previewSec={preview.data?.data?.total_sec}
            />
          ) : null}
          {!selected ? <p className="text-xs text-muted-foreground">{t("anime.inspector.empty")}</p> : null}
          <Button
            size="sm"
            variant="ghost"
            onClick={() =>
              director.mutate(undefined, {
                onSuccess: (result) => {
                  const first = result.data?.[0]?.message;
                  toast.message(first || t("anime.toast.directorQuiet"));
                },
              })
            }
          >
            <Camera />
            {t("anime.actions.director")}
          </Button>
        </div>
      </aside>
    </div>
  );
}

function applyActing(
  saveShot: ReturnType<typeof useSaveAnimeShot>,
  shot: AnimeShot,
  emotion: string,
  pose: string,
) {
  saveShot.mutate({
    ...shot,
    acting: { ...shot.acting, emotion, expression: emotion, pose },
  });
}

function CharacterInspect({ bibleName, shot }: { bibleName?: string; shot: AnimeShot }) {
  const { t } = useTranslation();
  return (
    <>
      <label>
        {t("anime.fields.character")}
        <input readOnly value={bibleName || shot.characters.join(", ")} />
      </label>
      <label>
        {t("anime.fields.scene")}
        <input readOnly value={shot.scene_id} />
      </label>
      <label>
        {t("anime.fields.locks")}
        <div className="anime-lock-row">
          {shot.locks.map((lock) => (
            <span key={lock}>🔒 {lock}</span>
          ))}
        </div>
      </label>
    </>
  );
}

function ActingInspect({
  shot,
  poses,
  expressions,
  onAct,
}: {
  shot: AnimeShot;
  poses: string[];
  expressions: string[];
  onAct: (emotion: string, pose: string) => void;
}) {
  const { t } = useTranslation();
  return (
    <>
      <label>
        {t("anime.fields.expression")}
        <select
          value={shot.acting.expression}
          onChange={(event) => onAct(event.target.value, shot.acting.pose)}
        >
          {(expressions.length ? expressions : [shot.acting.expression]).map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
      <label>
        {t("anime.fields.pose")}
        <select
          value={shot.acting.pose}
          onChange={(event) => onAct(shot.acting.expression, event.target.value)}
        >
          {(poses.length ? poses : [shot.acting.pose]).map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
      <label>
        {t("anime.fields.eyes")}
        <input readOnly value={shot.acting.eyes} />
      </label>
      <label>
        {t("anime.fields.body")}
        <input readOnly value={shot.acting.body} />
      </label>
    </>
  );
}

function CameraInspect({
  shot,
  cameras,
  onChange,
}: {
  shot: AnimeShot;
  cameras: string[];
  onChange: (shot: AnimeShot) => void;
}) {
  const { t } = useTranslation();
  return (
    <label>
      {t("anime.fields.camera")}
      <select
        value={shot.camera.shot_size}
        onChange={(event) =>
          onChange({
            ...shot,
            camera: { ...shot.camera, shot_size: event.target.value },
          })
        }
      >
        {(cameras.length ? cameras : [shot.camera.shot_size]).map((item) => (
          <option key={item} value={item}>
            {item.replaceAll("_", " ")}
          </option>
        ))}
      </select>
    </label>
  );
}

function ImageInspect({
  shot,
  onLock,
  onRepair,
}: {
  shot: AnimeShot;
  onLock: (lock: LockKey) => void;
  onRepair: () => void;
}) {
  const { t } = useTranslation();
  return (
    <>
      <label>
        {t("anime.fields.imagePrompt")}
        <textarea readOnly value={shot.image_prompt} />
      </label>
      <div className="anime-lock-row">
        {LOCKS.map((lock) => (
          <button
            key={lock}
            type="button"
            data-on={shot.locks.includes(lock)}
            onClick={() => onLock(lock)}
          >
            {shot.locks.includes(lock) ? "🔒" : "○"} {lock}
          </button>
        ))}
      </div>
      <Button size="sm" variant="outline" onClick={onRepair}>
        {t("anime.actions.repair")}
      </Button>
    </>
  );
}

function VoiceInspect({
  shot,
  cost,
  previewSec,
}: {
  shot: AnimeShot;
  cost?: { total: number; currency: string; tier: string };
  previewSec?: number;
}) {
  const { t } = useTranslation();
  return (
    <>
      <label>
        {t("anime.fields.dialogue")}
        <textarea readOnly value={shot.dialogue?.text || t("anime.fields.noDialogue")} />
      </label>
      <label>
        {t("anime.fields.voiceEmotion")}
        <input
          readOnly
          value={`${shot.acting.emotion} ${shot.acting.emotion_intensity.toFixed(2)}`}
        />
      </label>
      <p className="text-xs text-muted-foreground">
        {t("anime.cost.line", {
          total: cost?.total ?? 0,
          currency: cost?.currency ?? "USD",
          tier: cost?.tier ?? "preview",
          seconds: previewSec ?? 0,
        })}
      </p>
    </>
  );
}

function WorldForm({
  world,
  saving,
  onSave,
}: {
  world?: { world: string; era: string; rules: string[]; factions: string[]; notes: string };
  saving: boolean;
  onSave: (world: NonNullable<typeof world> & {
    locations: string[];
    timeline: string[];
    events: string[];
  }) => void;
}) {
  const { t } = useTranslation();
  const [draft, setDraft] = useStateLocal(world);
  if (!draft) return null;
  return (
    <div className="anime-studio__fields max-w-xl">
      <label>
        {t("anime.fields.world")}
        <input value={draft.world} onChange={(event) => setDraft({ ...draft, world: event.target.value })} />
      </label>
      <label>
        {t("anime.fields.era")}
        <input value={draft.era} onChange={(event) => setDraft({ ...draft, era: event.target.value })} />
      </label>
      <label>
        {t("anime.fields.rules")}
        <textarea
          value={draft.rules.join("\n")}
          onChange={(event) => setDraft({ ...draft, rules: event.target.value.split("\n").filter(Boolean) })}
        />
      </label>
      <Button size="sm" disabled={saving} onClick={() => onSave({
        locations: [],
        timeline: [],
        events: [],
        ...draft,
      })}>
        {t("anime.actions.save")}
      </Button>
    </div>
  );
}

function StyleForm({
  style,
  saving,
  onSave,
}: {
  style?: StyleBible;
  saving: boolean;
  onSave: (style: StyleBible) => void;
}) {
  const { t } = useTranslation();
  const [draft, setDraft] = useStateLocal(style);
  if (!draft) return null;
  return (
    <div className="anime-studio__fields max-w-xl">
      <label>
        {t("anime.fields.artStyle")}
        <textarea
          value={draft.art_style}
          onChange={(event) => setDraft({ ...draft, art_style: event.target.value })}
        />
      </label>
      <label>
        {t("anime.fields.palette")}
        <input
          value={draft.color_palette.join(", ")}
          onChange={(event) =>
            setDraft({
              ...draft,
              color_palette: event.target.value.split(",").map((item) => item.trim()).filter(Boolean),
            })
          }
        />
      </label>
      <Button size="sm" disabled={saving} onClick={() => onSave(draft)}>
        {t("anime.actions.save")}
      </Button>
    </div>
  );
}

function CharacterSheet({ bible }: { bible: { name: string; costume: string; signature: string[]; appearance: { hair: string; eyes: string } } | null }) {
  const { t } = useTranslation();
  if (!bible) {
    return <div className="anime-empty"><p>{t("anime.characters.empty")}</p></div>;
  }
  return (
    <div className="anime-score max-w-2xl">
      <div className="anime-score__cell">
        <span>{t("anime.fields.name")}</span>
        <strong>{bible.name}</strong>
      </div>
      <div className="anime-score__cell">
        <span>{t("anime.fields.costume")}</span>
        <strong className="!text-base">{bible.costume}</strong>
      </div>
      <div className="anime-score__cell">
        <span>{t("anime.fields.hair")}</span>
        <strong className="!text-base">{bible.appearance.hair}</strong>
      </div>
      <div className="anime-score__cell">
        <span>{t("anime.fields.eyes")}</span>
        <strong className="!text-base">{bible.appearance.eyes}</strong>
      </div>
      <div className="anime-score__cell col-span-2">
        <span>{t("anime.fields.signature")}</span>
        <strong className="!text-base">{bible.signature.join(" · ")}</strong>
      </div>
    </div>
  );
}

function StoryPanel({ hook, cliffhanger, world }: { hook: string; cliffhanger: string; world: string }) {
  const { t } = useTranslation();
  return (
    <div className="anime-score max-w-2xl">
      <div className="anime-score__cell col-span-2">
        <span>{t("anime.fields.world")}</span>
        <strong className="!text-base">{world || "—"}</strong>
      </div>
      <div className="anime-score__cell">
        <span>{t("anime.fields.hook")}</span>
        <strong className="!text-base">{hook || "—"}</strong>
      </div>
      <div className="anime-score__cell">
        <span>{t("anime.fields.cliffhanger")}</span>
        <strong className="!text-base">{cliffhanger || "—"}</strong>
      </div>
    </div>
  );
}

function QAPanel({ score }: { score?: { story: number; character: number; visual: number; audio: number; continuity: number; overall: number; notes: string[] } }) {
  const { t } = useTranslation();
  if (!score) return <div className="anime-empty"><p>{t("anime.qa.empty")}</p></div>;
  const cells = [
    ["story", score.story],
    ["character", score.character],
    ["visual", score.visual],
    ["audio", score.audio],
    ["continuity", score.continuity],
    ["overall", score.overall],
  ] as const;
  return (
    <div className="space-y-3">
      <div className="anime-score">
        {cells.map(([key, value]) => (
          <div key={key} className="anime-score__cell">
            <span>{t(`anime.qa.${key}`)}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      {score.notes.slice(0, 6).map((note) => (
        <div key={note} className="anime-issue">
          {note}
        </div>
      ))}
    </div>
  );
}

function useStateLocal<T>(value: T | undefined) {
  const [draft, setDraft] = useState(value);
  const serialized = JSON.stringify(value ?? null);
  const [seen, setSeen] = useState(serialized);
  if (serialized !== seen) {
    setSeen(serialized);
    setDraft(value);
  }
  return [draft, setDraft] as const;
}

export function parseAnimePanel(pathname: string): AnimePanel {
  const segment = pathname.split("/").pop() ?? "episodes";
  if (
    segment === "world" ||
    segment === "characters" ||
    segment === "styles" ||
    segment === "story" ||
    segment === "qa" ||
    segment === "episodes"
  ) {
    return segment;
  }
  return "episodes";
}
