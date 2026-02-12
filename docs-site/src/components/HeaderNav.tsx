import { useEffect, useState, type ReactNode } from "react";
import type { CarbonIconType } from "@carbon/react/icons";
import { Link } from "react-router";
import {
  Header,
  SkipToContent,
  HeaderMenuButton,
  HeaderName,
  HeaderGlobalBar,
  HeaderGlobalAction,
  SideNav,
  SideNavItems,
  SideNavMenu,
  SideNavMenuItem,
  Link as CarbonLink,
} from "@carbon/react";

import { LogoGithub, Asleep, Light, Devices } from "@carbon/react/icons";

import type { SiteNameType } from '~/types/config';
import type { FileTree, FileTreeNode } from "~/types/file-tree";
import type { ThemeMap } from "~/types/theme";

const SYSTEM = 'system';
const WHITE = 'white';
const G100 = 'g100';

const ICON_SIZE = 25;
const ICON_CLASSNAME = 'theme-switcher__icon';
const THEME_PREFERENCE_KEY = 'ibm-cloud-docs-theme-preference';

const themes: ThemeMap = {
  [SYSTEM]: { label: 'System', value: SYSTEM, icon: <Devices size={ICON_SIZE} className={ICON_CLASSNAME}/>},
  [WHITE]: { label: 'Light', value: WHITE, icon: <Light size={ICON_SIZE} className={ICON_CLASSNAME}/>},
  [G100]: { label: 'Dark', value: G100, icon: <Asleep size={ICON_SIZE} className={ICON_CLASSNAME}/>},
};

const themesRotation = [SYSTEM, WHITE, G100];

const fetchThemePreference = () => {
  return localStorage.getItem(THEME_PREFERENCE_KEY);
}

interface LeftNavComputedItemsProps {
  tree: FileTree
};
const LeftNavComputedItems = ({ tree }: LeftNavComputedItemsProps) => {
  const staticSideMenuProps = {
    defaultExpanded: true,
  };

  interface RecursiveComputedItemProps {
    node: FileTreeNode
  };
  const RecursiveComputedItem = ({ node }: RecursiveComputedItemProps) => (
    <>
      {Object.entries(node?.children ?? []).map(([path, node]) => {
        return (
          <>
            {node?.children && (
              <SideNavMenu title={node.title} {...staticSideMenuProps}>
                <RecursiveComputedItem node={node} />
              </SideNavMenu>
            )}
            {!node?.children && (
              <SideNavMenuItem element={Link} to={node.path}>
                {node.title}
              </SideNavMenuItem>
            )}
          </>
        );
      })}
    </>
  )

  return (
    <SideNavItems>
      {Object.entries(tree).map(([_, node]) => (
        <>
          {node?.children && (
            <SideNavMenu title={node.title} {...staticSideMenuProps}>
              <RecursiveComputedItem node={node} />
            </SideNavMenu>
          )}
          {!node?.children && (
            <SideNavMenuItem element={Link} to={node.path}>
              {node.title}
            </SideNavMenuItem>
          )}
        </>
      ))}
    </SideNavItems>
  );
}

interface HeaderNavProps {
  routes: FileTree,
  githubUrl: string,
  siteName: SiteNameType
};
const HeaderNav = ({ routes, githubUrl, siteName }: HeaderNavProps) => {
  const [isSideNavExpanded, setIsSideNavExpanded] = useState(true);

  const handleClickSideNavExpand = () => {
    setIsSideNavExpanded((prev) => !prev);
  };

  const [selectedThemeIdx, setSelectedThemeIdx] = useState<number>(0);

  const triggerStyleSheetThemeChange = (updatedThemeIdx: number) => {    // perform theme switch.
    // perform theme switch.
    const themeVal = themes[themesRotation[updatedThemeIdx]].value;
    document.documentElement.setAttribute('data-carbon-theme', themeVal);
  }
  const handleThemeChange = () => {
    // theme rotation in the ui.
    const newThemeIdx = (selectedThemeIdx + 1) % themesRotation.length
    setSelectedThemeIdx(newThemeIdx);
    // trigger stylesheet theme change.
    triggerStyleSheetThemeChange(newThemeIdx);
    // save preference in browser storage.
    localStorage.setItem(THEME_PREFERENCE_KEY,
      themes[themesRotation[newThemeIdx]].value
    );
  }

  // On init render.
  useEffect(() => {
    // fetch saved local browser storage theme preference.
    // otherwise if not set, default to system preference.
    const savedPreference = fetchThemePreference();
    const themeIdxToSet = themesRotation.indexOf(
      savedPreference && themesRotation.includes(savedPreference) ?
      savedPreference : SYSTEM
    );
    // ui update.
    setSelectedThemeIdx(
      themeIdxToSet
    );
    // stylesheet update.
    triggerStyleSheetThemeChange(themeIdxToSet);
  }, []);

  return (
    <Header aria-label="Carbon Tutorial" className="header-area">
      <SkipToContent />
      <HeaderMenuButton
        aria-label="Open menu"
        // isCollapsible
        onClick={handleClickSideNavExpand}
        isActive={isSideNavExpanded}
      />

      <HeaderName prefix={siteName.prefix}>
        {siteName.postfixBold}
      </HeaderName>

      <HeaderGlobalBar>
        <HeaderGlobalAction aria-label="Theme Switcher" tooltipAlignment="end" onClick={handleThemeChange}>
          {themes[themesRotation[selectedThemeIdx]]?.icon}
        </HeaderGlobalAction>
        <CarbonLink href={githubUrl} target="_blank">
          <HeaderGlobalAction className="github-external-action" aria-label="Github Repo" tooltipAlignment="end">
            <LogoGithub className="github-external-action__icon" size={25} />
          </HeaderGlobalAction>
        </CarbonLink>
      </HeaderGlobalBar>

      <SideNav
        aria-label="Side navigation"
        expanded={isSideNavExpanded}
        // isPersistent
        onOverlayClick={handleClickSideNavExpand}
        href="#main-content"
        onSideNavBlur={handleClickSideNavExpand}
        // isFixedNav={false}
        // isRail
      >
        <LeftNavComputedItems tree={routes} />
      </SideNav>
    </Header>
  )
}

export default HeaderNav;
