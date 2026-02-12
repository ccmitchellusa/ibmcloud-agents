# Docs Site for IBM Repos 📖
A a single common repo documentation site using carbon (ibm design language) and mdx framework (markdown with react flavor).

**Solves pain points**
1. A single README is messy for use cases outside of a quick get started.
2. Markdown by itself does not provide easy extensibility and interactive customizability.
3. Lack of IBM design language, look, and feel.

**Deployment Instructions**<br/>
Add the repo name of your project where your docs will live:
- In the `"name"` json field for [`package.json`](./package.json).
- In the `base:` key value field for [`vite.config.ts`](./vite.config.ts).

**Future Improvements...**<br/>
If the use of the projects gets picked up, then
- Add SSR for even quicker doc page loads.
- A search feature.
- Bundle optimizations, saving info such as toc, maps, internal refs, to static files.
