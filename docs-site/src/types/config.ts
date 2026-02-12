// export type PathType = {
//   breadcrumbLabel: string,
//   file?: string,
//   paths?: {
//     [path: string]: PathType
//   },
//   page?: string
// }

// export type RoutesType = {
//   [path: string]: PathType
// };

export type FooterType = {
  copyright: {
    image: string,
    notice: string,
  },
  content: {
    [title: string]: { text: string, external: boolean, url: string }[]
  }
}

export type SiteNameType = { prefix: string, postfixBold: string };

export type Config = {
  siteName: SiteNameType,
  tabTitle: string,
  appUrl: string,
  githubUrl: string,
  // routes: RoutesType,
  footer: FooterType
};

