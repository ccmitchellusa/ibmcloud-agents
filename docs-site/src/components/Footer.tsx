import { FlexGrid, Row, Column, Link } from "@carbon/react";
import { Launch } from "@carbon/react/icons";
import Image from '~/components/Image';

// types.
import type { FooterType } from "~/types/config";

interface FooterProps {
  footer: FooterType
}
const Footer = ({ footer }: FooterProps) => {
  const staticColSizes = {
    sm: 4,
    md: 3,
    lg: 5
  };
  return (
    <footer id="docs-footer" className="docs-footer">
      <FlexGrid>
        <Row className="docs-footer__content">
          {Object.entries(footer.content).map(([title, links]) => (
            <Column {...staticColSizes}>
              <h5 className="docs-footer__heading">{title}</h5>
              <ul>
                {links.map(({ text, external, url }) => (
                  <li>
                    <Link href={url} renderIcon={() => external ? <Launch size={16} /> : undefined}>{text}</Link>
                  </li>
                ))}
              </ul>
            </Column>
          ))}
        </Row>
        <Row className="docs-footer__copyright">
          <div className="docs-footer__copyright_container">
            <div className="docs-footer__copyright_img_container">
              <Image src={footer.copyright.image} altText="IBM copyright logo" className="docs-footer__copyright_img" />
            </div>
            <span>{footer.copyright.notice}</span>
          </div>
        </Row>
      </FlexGrid>
    </footer>
  );
}

export default Footer;