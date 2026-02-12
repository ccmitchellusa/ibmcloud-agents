import { Breadcrumb, BreadcrumbItem } from "@carbon/react";
import { useMemo } from "react";
import { useLocation, Link } from "react-router";

import type { DirMeta, DocMeta } from "~/types/meta";

interface BreadCrumbsProps {
  docSlugToMetaMap: Record<string, DocMeta>
  dirSlugToMetaMap: Record<string, DirMeta>
};
const BreadCrumbs = ({
  docSlugToMetaMap,
  dirSlugToMetaMap
}: BreadCrumbsProps) => {
  const loc = useLocation();
  const pathNames = loc.pathname
    .split('/')
    .filter((path) => path !== '');

  const breadcrumbs = useMemo(() => {
    let path = '';
    const pathNamesLastIdx = pathNames.length - 1;
    const crumbs = pathNames.map((pathName, idx) => {
      path += idx !== pathNamesLastIdx ?
        `${pathName}/` :
        pathName;

      return {
        title: (idx === pathNamesLastIdx ?
          docSlugToMetaMap[path]?.title :
          dirSlugToMetaMap[path]?.title) ?? pathName
      }
    });

    return crumbs;
  }, [pathNames]);

  return (
    <Breadcrumb className="breadcrumbs">
      <BreadcrumbItem>
        <Link to="/">Home</Link>
      </BreadcrumbItem>
      {breadcrumbs.map(({ title }, idx) => (
        <BreadcrumbItem key={`breadcrumb-${title}`} isCurrentPage>
          {title}
        </BreadcrumbItem>
      ))}
    </Breadcrumb>
  )
}

export default BreadCrumbs;
