export type FileTreeNode = {
  title: string,
  path: string,
  children?: FileTree,
}

export type FileTree = {
  [path: string]: FileTreeNode
};
