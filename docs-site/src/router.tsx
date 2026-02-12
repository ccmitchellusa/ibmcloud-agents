// import { type RouteConfig, index, route } from "@react-router/dev/routes";
// import { flatRoutes } from "./util/routes";

// export default [
//   ...flatRoutes
//   // ...Object.keys(routesPages).map((routePath) => route(routePath, routesPages[routePath]))
//   // route("agents/base-agent/", "routes/base-agent.tsx"),
//   // route("agents/account-admin-agent", "routes/ibm-cloud-account-admin-agent.tsx"),
// ] satisfies RouteConfig;

import { createBrowserRouter } from "react-router";
import React, { lazy, Suspense } from "react";
import fm from "front-matter";
import fs from "fs";
import path from "path";

import App from "./App";
import type { DocMeta, DirMeta } from "./types/meta";
import type { FileTree, FileTreeNode } from "./types/file-tree";
import type { TocEntry } from "@stefanprobst/rehype-extract-toc";
import type { SlugToTocMap, TocLine } from "./types/toc";

const cleanDocRoutePath = (path: string) =>
  path
    .replace('/docs/', '')
    .replace(/home\.(mdx|md)$/, '')
    .replace(/\.(mdx|md)$/, '') || '';

const cleanDirRoutePath = (path: string) =>
  path
    .replace('/docs/', '')
    .replace(/(_meta|meta)\.json$/, '') || '';

const tocMetaFileName = (pathStr: string) =>
  path.resolve(__dirname, '../public/generated',
    `${cleanDirRoutePath(pathStr)
      .replace('/', '.')}.json`
  );

const buildFileTree = (
  slugToMetaMap: Record<string, DocMeta>,
  dirSlugToMetaMap: Record<string, DirMeta>
) => {
  let fileTree: FileTree = {};

  Object.entries(slugToMetaMap).forEach(([slug, meta]) => {
    const parts = slug
      .split('/');
    const partsLen = parts.length;
    const lastIdx = partsLen - 1;

    if (partsLen > 1 && parts[lastIdx] === '')
      parts.pop();

    let node = fileTree;
    let path = '';
    let draftFlag = false;
    parts.forEach((part, idx) => {
      if (draftFlag) return;

      const addPath = part.length === 0 ||
        idx === lastIdx ? part : `${part}/`;
      path += addPath;

      // hide draft dirs/docs from sidenav.
      if (
        dirSlugToMetaMap[path]?.draft ||
        slugToMetaMap[path]?.draft
      ) {
        draftFlag = true;
        return;
      }

      node[addPath] ??= idx === lastIdx ?
        {
          title: meta?.title ?? part,
          path,
        } :
        {
          title: dirSlugToMetaMap[path]?.title ?? part,
          path,
          children: {}
        };

      if (node[addPath]?.children)
        node = node[addPath].children;
    })
  })

  // position home entry as first item.
  if (fileTree[''])
    fileTree = { '': fileTree[''], ...fileTree };

  return fileTree;
}

export const docSlugToMetaMap: Record<string, DocMeta> = {};
export const dirSlugToMetaMap: Record<string, DirMeta> = {};

const docModules = import.meta.glob('/docs/**/*.(mdx|md)');
const docContentModules = import.meta.glob('/docs/**/*.(mdx|md)', {
  eager: true,
  query: '?raw',
  import: 'default'
  // as: 'raw'
});

const docDirMetaFiles = import.meta.glob('/docs/**/(_meta|meta).json', {
  eager: true,
  query: '?json',
  import: 'default'
})
Object.entries(docDirMetaFiles).forEach(([path, dirMeta]) => {
  const meta = dirMeta as DirMeta;
  dirSlugToMetaMap[cleanDirRoutePath(path)] = meta;
})

const docRoutes = Object.entries(docContentModules).map(
  ([path, component]) => {
    const slug = cleanDocRoutePath(path);

    // doc page meta data.
    const { attributes } = fm<DocMeta>(component as string);
    docSlugToMetaMap[slug] = attributes; // global build store.

    // compile remaining mdx/md string.
    // const lazyComponent = lazy(async () => {
    //   const compiled = await compile(body, {
    //     outputFormat: 'function-body',
    //     providerImportSource: '@mdx-js/react',
    //     remarkPlugins: [
    //       remarkGfm,
    //       [mdxMermaid, {output: 'svg'}],
    //       // customRemarkExtractHeadings,
    //     ],
    //     rehypePlugins: [
    //       rehypeSlug,
    //       // rehypeExtractToc,
    //       // rehypeExtractTocExport
    //     ]
    //   });
    //   console.info(String(compiled))

    //   const Component = await run(
    //     String(compiled),
    //     {...runtime, baseUrl: import.meta.url}
    //   );

    //   return Component;
    // })

    return {
      path: slug,
      meta: attributes,
      // Component: lazy(docModules[path] as any),
      Component: lazy(docModules[path] as any),
    }
  }
).filter((docRoute) => !docRoute.meta?.draft); // hide drafts from url hit.

const tocContentModules = import.meta.glob<TocEntry[]>('/docs/**/*.(mdx|md)', {
  eager: true,
  import: "tableOfContents",
});

const recursiveToc = (tocNode: TocEntry, flatTocEntries: TocLine[]) => {
  if (tocNode?.depth >= 3) return;
  Object.entries(tocNode?.children ?? []).forEach(([_, tocEntry]) => {
    flatTocEntries.push({
      title: tocEntry.value,
      depth: tocEntry.depth - 2,
      navId: tocEntry?.id ?? '',
    })
    recursiveToc(tocEntry, flatTocEntries);
  })
}

export const docSlugToToc: SlugToTocMap = {};
Object.entries(tocContentModules).forEach(([path, tocEntry]) => {
  const flatTocEntries: TocLine[] = [];

  const topTocEntry = tocEntry[0];
  recursiveToc(topTocEntry, flatTocEntries);

  docSlugToToc[cleanDocRoutePath(path)] = flatTocEntries;
})

// fs does not work on browser/client code.
// (async () => {
//   const depthLimit = 3;

//   const recursiveToc = (tocNode: TocEntry, flatTocEntries: { title: string, depth: number }[]) => {
//     Object.entries(tocNode?.children ?? []).forEach(([path, tocEntry]) => {
//       flatTocEntries.push({
//         title: tocEntry.value,
//         depth: tocEntry.depth
//       })
//     })
//   }

//   Object.entries(tocContentModules).forEach(([path, tocEntry]) => {
//     const flatTocEntries = [];

//     const topTocEntry = tocEntry[0];
//     flatTocEntries.push({
//       title: topTocEntry.value,
//       depth: topTocEntry.depth
//     })
//     recursiveToc(topTocEntry, flatTocEntries);
//     fs.writeFile(tocMetaFileName(path), JSON.stringify(flatTocEntries, null, 0), (err) => {
//       console.error(`Failed to generate toc for ${path}:`, err);
//     });
//     console.info('wehn all said and on', flatTocEntries)
//   })

// })();

export const fileTree = buildFileTree(
  docSlugToMetaMap,
  dirSlugToMetaMap
);

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: docRoutes.map(({ path, Component }) => ({
      path,
      element: (
        <Suspense fallback={'loading...'}>
          <Component />
        </Suspense>
      )
    }))
  }
]);

export default router;
