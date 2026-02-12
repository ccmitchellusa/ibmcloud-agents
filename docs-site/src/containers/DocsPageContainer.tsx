import type { ReactNode } from 'react';
import { useLocation, Link } from 'react-router';
import { Column, Row } from '@carbon/react';

import { docSlugToToc } from '~/router';
import type { TocLine } from '~/types/toc';

type ColSingleSizeType = { span: number, offset?: number };
type ColSizeType = {
  sm: ColSingleSizeType,
  md: ColSingleSizeType,
  lg: ColSingleSizeType,
}

interface TOCProps {
  toc: TocLine[]
}
const TOC = ({ toc }: TOCProps) => {
  const tocNavigate = (id: string | undefined) => {
    document.getElementById(id ?? '')?.scrollIntoView();
    window.location.hash = id ?? '';
  }

  return (
    <aside className="toc">
      <ol className="toc__list">
        {/* Only supporting upto and including h3. */}
        {toc?.map(({depth, title, navId}) => (
          <li
            id={`toc-link-${navId}`}
            className="toc__item"
            style={{ marginLeft: `${depth}rem` }}
          >
            <a onClick={() => tocNavigate(navId)} className="toc__item_link">{title}</a>
          </li>
        ))}
      </ol>
    </aside>
  )
}

export default function DocsPageContainer({ children }: { children: ReactNode }) {
  const loc = useLocation();
  // match location path to docs page.
  const pathName = loc.pathname.slice(1);

  // static var of column responsive sizes.
  const colSizes = {
    sm: 4,
    md: 8,
    lg: 12,
    // xlg: 12,
  };

  return (
    <Row>
      <Column className="docs-page-container-row__readme" {...colSizes}>
        {children}
      </Column>
      <Column className="docs-page-container-row__toc">
        <TOC toc={docSlugToToc[pathName] ?? []} />
      </Column>
    </Row>
  );
}
