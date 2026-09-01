// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { p } from "@/lib/api-path";
import { queryKeys } from "@/lib/query-keys";
import type { OkResponse } from "@/types/api";
import type {
  AnimeCatalog,
  AnimePreview,
  AnimeShot,
  CharacterBible,
  CostEstimate,
  EpisodeBundle,
  QAScorecard,
  SceneBible,
  StoryWorld,
  StyleBible,
} from "@/types/anime";

export function useAnimeCatalog() {
  return useQuery({
    queryKey: queryKeys.animeCatalog(),
    queryFn: ({ signal }) =>
      api.get("api/v1/anime/catalog", { signal }).json<OkResponse<AnimeCatalog>>(),
  });
}

export function useAnimeWorld(project: string) {
  return useQuery({
    queryKey: queryKeys.animeWorld(project),
    queryFn: ({ signal }) =>
      api.get(p`api/v1/anime/projects/${project}/world`, { signal }).json<OkResponse<StoryWorld>>(),
    enabled: Boolean(project),
  });
}

export function useSaveAnimeWorld(project: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: StoryWorld) =>
      api.put(p`api/v1/anime/projects/${project}/world`, { json: body }).json<OkResponse<StoryWorld>>(),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.animeWorld(project) }),
  });
}

export function useAnimeStyle(project: string) {
  return useQuery({
    queryKey: queryKeys.animeStyle(project),
    queryFn: ({ signal }) =>
      api.get(p`api/v1/anime/projects/${project}/style`, { signal }).json<OkResponse<StyleBible>>(),
    enabled: Boolean(project),
  });
}

export function useSaveAnimeStyle(project: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: StyleBible) =>
      api.put(p`api/v1/anime/projects/${project}/style`, { json: body }).json<OkResponse<StyleBible>>(),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.animeStyle(project) }),
  });
}

export function useAnimeCharacters(project: string) {
  return useQuery({
    queryKey: queryKeys.animeCharacters(project),
    queryFn: ({ signal }) =>
      api
        .get(p`api/v1/anime/projects/${project}/characters`, { signal })
        .json<OkResponse<CharacterBible[]>>(),
    enabled: Boolean(project),
  });
}

export function useSaveAnimeCharacter(project: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: CharacterBible) =>
      api
        .put(p`api/v1/anime/projects/${project}/characters/${body.id}/bible`, { json: body })
        .json<OkResponse<CharacterBible>>(),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.animeCharacters(project) }),
  });
}

export function useAnimeScenes(project: string) {
  return useQuery({
    queryKey: queryKeys.animeScenes(project),
    queryFn: ({ signal }) =>
      api.get(p`api/v1/anime/projects/${project}/scenes`, { signal }).json<OkResponse<SceneBible[]>>(),
    enabled: Boolean(project),
  });
}

export function useAnimeEpisode(project: string, episode: number) {
  return useQuery({
    queryKey: queryKeys.animeEpisode(project, episode),
    queryFn: ({ signal }) =>
      api
        .get(p`api/v1/anime/projects/${project}/episodes/${episode}/state`, { signal })
        .json<OkResponse<EpisodeBundle>>(),
    enabled: Boolean(project) && episode > 0,
  });
}

export function useSaveAnimeShot(project: string, episode: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (shot: AnimeShot) =>
      api
        .put(p`api/v1/anime/projects/${project}/episodes/${episode}/shots/${shot.id}`, {
          json: shot,
        })
        .json<OkResponse<AnimeShot>>(),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.animeEpisode(project, episode) }),
  });
}

export function useAnimeActing(project: string, episode: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: { shot: string; emotion?: string; pose?: string; intent?: string }) =>
      api
        .post(
          p`api/v1/anime/projects/${project}/episodes/${episode}/shots/${input.shot}/acting`,
          { json: input },
        )
        .json<OkResponse<AnimeShot>>(),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.animeEpisode(project, episode) }),
  });
}

export function useAnimeContinuity(project: string, episode: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () =>
      api
        .post(p`api/v1/anime/projects/${project}/episodes/${episode}/continuity/check`)
        .json<OkResponse<unknown>>(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.animeEpisode(project, episode) });
      qc.invalidateQueries({ queryKey: queryKeys.animeQA(project, episode) });
    },
  });
}

export function useAnimeQA(project: string, episode: number) {
  return useQuery({
    queryKey: queryKeys.animeQA(project, episode),
    queryFn: ({ signal }) =>
      api
        .get(p`api/v1/anime/projects/${project}/episodes/${episode}/qa`, { signal })
        .json<OkResponse<QAScorecard>>(),
    enabled: Boolean(project) && episode > 0,
  });
}

export function useAnimePreview(project: string, episode: number) {
  return useQuery({
    queryKey: queryKeys.animePreview(project, episode),
    queryFn: ({ signal }) =>
      api
        .get(p`api/v1/anime/projects/${project}/episodes/${episode}/preview`, { signal })
        .json<OkResponse<AnimePreview>>(),
    enabled: Boolean(project) && episode > 0,
  });
}

export function useAnimeCost(project: string, episode: number, tier: string) {
  return useQuery({
    queryKey: queryKeys.animeCost(project, episode, tier),
    queryFn: ({ signal }) =>
      api
        .get(p`api/v1/anime/projects/${project}/episodes/${episode}/cost`, {
          searchParams: { tier },
          signal,
        })
        .json<OkResponse<CostEstimate>>(),
    enabled: Boolean(project) && episode > 0,
  });
}

export function useSeedTenShotDemo(project: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () =>
      api
        .post(p`api/v1/anime/projects/${project}/demo/ten-shots`)
        .json<OkResponse<EpisodeBundle>>(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects", project, "anime"] });
    },
  });
}

export function useExportAnimeEpisode(project: string, episode: number) {
  return useMutation({
    mutationFn: () =>
      api
        .post(p`api/v1/anime/projects/${project}/episodes/${episode}/export`)
        .json<OkResponse<Record<string, unknown>>>(),
  });
}

export function useAnimeDirector(project: string, episode: number) {
  return useMutation({
    mutationFn: () =>
      api
        .post(p`api/v1/anime/projects/${project}/episodes/${episode}/director`)
        .json<OkResponse<Array<Record<string, string>>>>(),
  });
}

export function useRepairAnimeShot(project: string, episode: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (shot: string) =>
      api
        .post(p`api/v1/anime/projects/${project}/episodes/${episode}/shots/${shot}/repair`)
        .json<OkResponse<AnimeShot>>(),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.animeEpisode(project, episode) }),
  });
}
