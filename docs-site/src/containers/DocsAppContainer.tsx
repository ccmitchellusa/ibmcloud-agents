import {
  FlexGrid,
  Row,
  Column,
} from '@carbon/react';

import '../styles/main.scss';

import config from '~/docs.config';

import BreadCrumbs from '~/components/BreadCrumbs';
import DocsPageContainer from './DocsPageContainer';
import Footer from '~/components/Footer';
import HeaderNav from '~/components/HeaderNav';
import {
  dirSlugToMetaMap,
  docSlugToMetaMap,
  fileTree
} from '~/router';
import { useLocation } from 'react-router';
import { useEffect } from 'react';

export function DocsAppContainer({ children }: { children: React.ReactNode }) {
  const loc = useLocation();

  useEffect(() => {
    let title = `${config.tabTitle}`;
    const cleanedPathName = loc.pathname
      .replace(/^\s*\/*\s*|\s*\/*\s*$/gm, '');

    title += ` | ${docSlugToMetaMap[cleanedPathName]?.title ?? cleanedPathName}`;

    document.title = title;
  }, [loc.pathname]);

  const colSizes = {
    sm: { span: 4, offset: 0 },
    md: { span: 8, offset: 0 },
    lg: { span: 13, offset: 3 },
    // xlg: { span: 16, offset: 0 },
    // max: { span: 13, offset: 3 },
  }
  const colSizesBreadcrumbs = {
    sm: { span: 4, offset: 0 },
    md: { span: 8, offset: 0 },
    lg: { span: 16, offset: 3 },
  }

  return (
    <div className="cds--layout">
      <HeaderNav routes={fileTree} githubUrl={config.githubUrl} siteName={config.siteName} />

      <div className="scrollable-content">
        <main id="main-content" className="cds--content">
          <FlexGrid fullWidth>
            <Row>
              <Column {...colSizesBreadcrumbs}>
                <BreadCrumbs
                  docSlugToMetaMap={docSlugToMetaMap}
                  dirSlugToMetaMap={dirSlugToMetaMap}
                />
              </Column>
            </Row>
            <Row>
              <Column {...colSizes}>
                <DocsPageContainer>
                  {children}
                </DocsPageContainer>
              </Column>
            </Row>
          </FlexGrid>
        </main>

        <Footer footer={config.footer} />
      </div>
    </div>
  );
}