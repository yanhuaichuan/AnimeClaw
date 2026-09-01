// SPDX-License-Identifier: Elastic-2.0
// Copyright (c) 2026 yanhuaichuan
import { Monitor, Moon, Sun } from "lucide-react";
import { useTranslation } from "react-i18next";

import { useResolvedTheme } from "@/components/theme-provider";
import { cn } from "@/lib/utils";
import { useAppStore, type Theme } from "@/stores/app-store";

const OPTIONS: Array<{
  value: Theme;
  labelKey: string;
  hintKey: string;
  Icon: typeof Sun;
}> = [
  { value: "light", labelKey: "theme.light", hintKey: "settings.appearancePage.lightHint", Icon: Sun },
  { value: "dark", labelKey: "theme.dark", hintKey: "settings.appearancePage.darkHint", Icon: Moon },
  { value: "system", labelKey: "theme.system", hintKey: "settings.appearancePage.systemHint", Icon: Monitor },
];

export function AppearanceSection() {
  const { t } = useTranslation();
  const theme = useAppStore((s) => s.theme);
  const setTheme = useAppStore((s) => s.setTheme);
  const resolved = useResolvedTheme();

  return (
    <section className="space-y-5 px-5 py-5">
      <header className="space-y-1.5">
        <h3 className="text-base font-semibold">{t("settings.appearancePage.title")}</h3>
        <p className="text-sm leading-6 text-muted-foreground">
          {t("settings.appearancePage.description")}
        </p>
      </header>

      <p className="text-xs text-muted-foreground">
        {t("settings.appearancePage.current")}：
        {t(`theme.${theme}`)}
        {theme === "system" ? ` · ${resolved === "dark" ? t("theme.dark") : t("theme.light")}` : null}
      </p>

      <div className="grid gap-3 sm:grid-cols-3">
        {OPTIONS.map(({ value, labelKey, hintKey, Icon }) => {
          const active = theme === value;
          return (
            <button
              key={value}
              type="button"
              onClick={() => setTheme(value)}
              aria-pressed={active}
              className={cn(
                "flex flex-col items-start gap-3 rounded-2xl border px-4 py-4 text-left transition-colors duration-150",
                active
                  ? "border-primary bg-primary/12 text-foreground"
                  : "border-border bg-card/60 text-muted-foreground hover:border-primary/40 hover:text-foreground",
              )}
            >
              <span
                className={cn(
                  "grid size-9 place-items-center rounded-xl",
                  active ? "bg-primary text-primary-foreground" : "bg-muted",
                )}
              >
                <Icon className="size-4" aria-hidden />
              </span>
              <span className="text-sm font-semibold text-foreground">{t(labelKey)}</span>
              <span className="text-xs leading-5">{t(hintKey)}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
