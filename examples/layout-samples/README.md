# Layout samples guide

This repository currently does **not** bundle thesis / journal / conference PDF layout samples directly.

That is intentional.

## Why samples are not bundled yet

The project is open-source, but many real-world thesis templates, school samples, journal layouts, or camera-ready PDFs may involve:

- copyright restrictions
- redistribution limits
- unclear licensing status
- institution-specific usage rules

So the safer default is:

- keep the workflow and metadata public
- let users add their own layout sample files locally
- avoid redistributing PDFs unless their license is clearly compatible

## What kinds of layout samples are recommended

If you want to build a stronger local template library, good sample inputs include:

### 1. Degree thesis samples

Examples:

- bachelor thesis PDF samples
- master thesis PDF samples
- doctoral thesis PDF samples
- official university formatting guides

### 2. Journal / conference samples

Examples:

- camera-ready conference papers
- official journal template outputs
- public author kit examples

### 3. Format guideline files

Examples:

- official PDF formatting guides
- Word templates
- LaTeX class/style bundles (`.cls`, `.sty`)

## Suggested local directory layout

If you want to extend this repository locally, a practical structure is:

```text
paper-template-library/
  layout/
    defaults/
    official/
      degree/
      journal/
      conference/
  structure/
    examples/
      pdfs/
      meta/
```

## Recommended naming convention

Examples:

```text
layout/official/degree/zh-master-university-a-sample.pdf
layout/official/journal/ieee-transaction-sample.pdf
layout/official/conference/acl-camera-ready-sample.pdf
```

Use names that encode:

- language
- level / venue type
- institution / journal / conference
- whether it is sample / official / guideline

## Recommended metadata fields

When adding a new sample, try to record at least:

- source URL
- source type
- license / redistribution status
- paper type
- language
- citation style
- numbering rule
- front matter requirements
- title / table / figure placement rules

## Best practice

If a sample is clearly redistributable, you may add it to the repo.
If the licensing status is unclear, keep only:

- the metadata
- the source URL
- local instructions for the user to fetch it themselves

That keeps the project safer while still making the workflow useful.
