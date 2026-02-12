import config from "~/docs.config";

// relPath is relative to the appUrl/[public folder - skip]/...
const Image = ({
  src,
  className,
  altText
}: {
  src: string,
  className?: string,
  altText: string
}) => <img src={`${config.appUrl}${src}`} className={className} alt={altText} />

export default Image;