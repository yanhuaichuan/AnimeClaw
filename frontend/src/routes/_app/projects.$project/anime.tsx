// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { createFileRoute, useNavigate } from "@tanstack/react-router";

import { AnimeStudio, parseAnimePanel } from "@/features/anime/AnimeStudio";
import type { AnimePanel } from "@/types/anime";

function parseSearch(search: Record<string, unknown>): { panel: AnimePanel } {
  return { panel: parseAnimePanel(String(search.panel ?? "episodes")) };
}

function AnimePage() {
  const { project } = Route.useParams();
  const { panel } = Route.useSearch();
  const navigate = useNavigate();

  return (
    <AnimeStudio
      project={project}
      panel={panel}
      onPanelChange={(next) =>
        navigate({
          to: "/projects/$project/anime",
          params: { project },
          search: { panel: next },
        })
      }
    />
  );
}

export const Route = createFileRoute("/_app/projects/$project/anime")({
  validateSearch: parseSearch,
  component: AnimePage,
});
