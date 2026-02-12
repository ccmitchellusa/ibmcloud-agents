import path from 'path';
import react from '@vitejs/plugin-react';
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import mdx from "@mdx-js/rollup";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import rehypeExtractToc from "@stefanprobst/rehype-extract-toc";
import rehypeExtractTocExport from "@stefanprobst/rehype-extract-toc/mdx";
import mdxMermaid from 'mdx-mermaid'
import remarkFrontmatter from 'remark-frontmatter';

export default defineConfig({
  plugins: [
    mdx({
      providerImportSource: "@mdx-js/react",
      remarkPlugins: [
        remarkGfm,
        [mdxMermaid, {output: 'svg'}],
        remarkFrontmatter
        // customRemarkExtractHeadings,
      ],
      rehypePlugins: [
        rehypeSlug,
        rehypeExtractToc,
        rehypeExtractTocExport
      ]
    }),
    react(),
    tsconfigPaths()
  ],
  resolve: {
    alias: {
      '~': path.resolve(__dirname, 'src')
    }
  },
  // needed for github pages just put the repo name here
  // base: '/your-repo-name-here/',
});
