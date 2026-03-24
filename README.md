# paper-intake-router

**An agent-native paper workflow engine for intake, evidence organization, figure/table planning, citation alignment, and template-aware final rendering.**

`paper-intake-router` is a workflow core for academic writing agents.
It helps turn a paper request into a structured pipeline: normalize the intake, organize evidence, plan figures/tables, align citations, and render drafts toward deliverable output.

It is especially useful when you want an agent to do more than “write paragraphs” — you want it to manage the *workflow* around a paper.

## What problem this project solves

Most AI writing tools are good at generating text, but weak at the operational layer around academic writing:

- collecting and normalizing paper requirements
- deciding what information is still missing
- organizing evidence and citations by chapter / claim type
- planning figures and tables before the draft is written
- keeping figure numbering, references, and citation rendering consistent
- adapting final output to different citation and layout profiles

This project focuses on that missing layer.

## Core capabilities

### 1. Intake → task sheet

- normalize raw paper requests into structured task sheets
- infer defaults for paper type, language, style, and target length
- resolve default layout templates when no official template is provided

### 2. Evidence and citation pipeline

- build reference shortlist
- screen and retry search queries
- assemble reference pack
- generate writing evidence pack
- generate citation plan by chapter and claim type

### 3. Figure / table workflow

- generate figure-table plans before drafting
- assign numbering rules from template defaults
- scaffold code, placeholder data, and output paths
- validate figure/table references against the plan
- autofix common reference and phrasing issues

### 4. Unified citation layer

- support normal prose and figure explanation sentences through the same citation rendering chain
- support `support-note`, `inline-marker`, and `internal-anchor` citation modes
- render final citations into GB/T 7714 or APA-style output
- apply template-aware citation rendering profiles

### 5. Template-aware final rendering

- separate layout template selection from writing logic
- carry citation rendering preferences through the workflow
- support profile-aware final prose cleanup for mixed Chinese / APA contexts

## Project structure

```text
paper-intake-router/
├── SKILL.md
├── scripts/
├── references/
├── paper-template-library/
├── examples/
├── README.md
└── LICENSE
```

## Minimal workflow

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json

python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json

python3 scripts/autofix_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft examples/draft.md \
  --citation-mode internal-anchor \
  --out /tmp/fixed.md

python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --style 'GB/T 7714' \
  --out /tmp/final.md
```

## Example use cases

- building a thesis workflow agent that needs more than free-form text generation
- managing figure/table numbering and explanation sentences consistently
- keeping citations aligned across normal prose and figure explanation text
- generating structured intermediate artifacts instead of opaque black-box output

## What this project is

This project is best thought of as a:

- **paper workflow engine**
- **formatting and citation stabilizer**
- **draft-to-deliverable orchestration layer for agents**

## What this project is not

This project does **not** guarantee:

- school-specific compliance without the real template or official guideline
- real experimental validity
- final submission readiness without human review
- automatic invention of trustworthy data, results, or references

See `references/capability-boundaries.md` for the current operational boundary set.

## Why it may be interesting

Many agent projects stop at “generate text.”

This one pushes further into the operational side of academic work:

- evidence organization
- figure/table workflow
- citation normalization
- template-aware rendering
- validation and final gates

That makes it useful not only as a writing helper, but as a reusable paper-production pipeline core.

## License

MIT
