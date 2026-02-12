import { Outlet, ScrollRestoration } from "react-router";
import { DocsAppContainer } from "./containers/DocsAppContainer";
import { Suspense } from "react";
import { MDXProvider } from "@mdx-js/react";
import { components } from "./theme/carbon";

const App = () => (
  <MDXProvider components={components}>
    <DocsAppContainer>
      <Outlet />
      <ScrollRestoration />
    </DocsAppContainer>
  </MDXProvider>
)

export default App;
