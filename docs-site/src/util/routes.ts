// NOTE:
// This was used when the react router framework strategy was used.

// import type { RoutesType } from "~/types/config";
// import { index, route } from "@react-router/dev/routes";

// import config from "../docs.config";

// type FlatRouteType = {
//   path: string,
//   file: string,
// };
// export function flattenRoutes(routes: RoutesType) {
//   const flatRoutes: FlatRouteType[]  = [];

//   function traverseRoutes(routeGroup: RoutesType, path: FlatRouteType) {
//     for (const [k, v] of Object.entries(routeGroup)) {
//       const newPath = { path: path.path.endsWith('/') ? `${path.path}${k}` : `${path.path}/${k}`, file: path.file };

//       if (v?.paths) {
//         traverseRoutes(v.paths, newPath);
//       } else {
//         flatRoutes.push({ path: newPath.path, file: v?.file ?? '' });
//       }
//     }
//   }

//   for (const [k, v] of Object.entries(routes)) {
//     if (v?.paths) {
//       traverseRoutes(v.paths, { path: k, file: '' });
//     } else {
//       flatRoutes.push({ path: k, file: v?.file ?? '',  });
//     }
//   }

//   return flatRoutes;
// }

// type PageKeyPathType = {
//   [path: string]: string
// };
// type FlatPathType = {
//   path: string,
//   page: string
// };
// export function getPathKeyToPage(routes: RoutesType) {
//   const flatRoutes: PageKeyPathType  = {};

//   function traverseRoutes(routeGroup: RoutesType, path: FlatPathType) {
//     for (const [k, v] of Object.entries(routeGroup)) {
//       const newPath = { path: path.path.endsWith('/') ? `${path.path}${k}` : `${path.path}/${k}`, page: path.page };

//       if (v?.paths) {
//         traverseRoutes(v.paths, newPath);
//       } else {
//         if (!v?.page) throw new Error(`No page specified for ${newPath.path} route.`);
//         flatRoutes[k !== '/' ? `/${newPath.path}` : newPath.path] = v?.page ?? '';
//       }
//     }
//   }

//   for (const [k, v] of Object.entries(routes)) {
//     if (v?.paths) {
//       traverseRoutes(v.paths, { path: k, page: '' });
//     } else {
//       if (!v?.page) throw new Error(`No page specified for ${k} route.`);
//       flatRoutes[k !== '/' ? `/${k}` : k] = v?.page ?? '';
//     }
//   }

//   return flatRoutes;
// }

// export const pathKeysToPage = getPathKeyToPage(config.routes);

// export const flatRoutes = flattenRoutes(config.routes).map(({ path, file }) => {
//   if (path === '/') return index(file);
//   return route(path, file);
// });
