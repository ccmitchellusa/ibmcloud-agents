import type { ReactNode } from "react";

export interface ThemeMeta {
  label: string,
  value: string,
  icon: ReactNode,
};

export type ThemeMap = Record<string, ThemeMeta>;