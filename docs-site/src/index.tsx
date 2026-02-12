import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router';
import { DocsAppContainer } from './containers/DocsAppContainer';
import { StrictMode } from 'react';

import router from './router';

const root = document.getElementById('root')!;

ReactDOM.createRoot(root).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
