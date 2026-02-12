import type { TocEntry } from "@stefanprobst/rehype-extract-toc";

export const docPages = import.meta.glob<TocEntry[]>("../../docs/**/*.(mdx|md)", {
  eager: true,
  import: "tableOfContents",
});
export const transformDocsPageKey = (shortKey: string) => `../docs/${shortKey}`;
