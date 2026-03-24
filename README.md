[English](./README.md) | [简体中文](./README.zh-CN.md)

# paper-intake-router

> Agent-native paper workflow engine for intake, evidence organization, figure/table planning, citation alignment, and template-aware final rendering.

`paper-intake-router` is a workflow core for academic writing agents.
It is designed for paper-production workflows where text generation alone is not enough.

It helps agents manage the operational layer around papers:

- normalize intake into structured task sheets
- organize references, evidence packs, and citation plans
- plan figures/tables before drafting
- keep figure numbering and prose references consistent
- render citations through a unified, template-aware pipeline

## Highlights

- **Intake → task sheet** normalization
- **Reference shortlist / screening / retry / reference pack** workflow
- **Writing evidence pack + citation plan** generation
- **Figure/table planning, validation, and autofix**
- **Unified citation layer** for both normal prose and figure explanation sentences
- **Template-aware final citation rendering** for GB/T 7714 and APA-style outputs

## Who this is for

This project is useful if you are building:

- academic writing agents
- thesis workflow assistants
- paper-production pipelines
- citation / figure automation systems

## Repository layout

```text
paper-intake-router/
├── SKILL.md
├── scripts/
├── references/
├── paper-template-library/
├── examples/
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## Quick start

### 1. Build a task sheet

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json
```

### 2. Build a figure/table plan

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json
```

### 3. Autofix figure references into internal citation anchors

```bash
python3 scripts/autofix_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft examples/draft.md \
  --citation-mode internal-anchor \
  --out /tmp/fixed.md
```

### 4. Render final citations

```bash
python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --style 'GB/T 7714' \
  --out /tmp/final.md
```

## Core concepts

### Task sheet

A normalized task object that captures:

- paper type
- degree level
- topic
- style
- target length
- layout template selection

### Figure/table plan

A structured artifact that decides:

- what figures/tables should exist
- numbering rules
- code/data/output paths
- claim type
- support evidence and citation hints

### Unified citation layer

This project supports three citation output modes:

- `support-note`
- `inline-marker`
- `internal-anchor`

The most important one is `internal-anchor`, because it lets:

- figure explanation sentences
- normal prose
- method / experiment conclusion sentences

all pass through the same final citation rendering chain.

## What this project is

Think of it as a:

- **paper workflow engine**
- **formatting and citation stabilizer**
- **draft-to-deliverable orchestration layer for agents**

## What this project is not

This project does **not** guarantee:

- school-specific compliance without the real official template
- real experimental validity
- submission-readiness without human review
- trustworthy data/result invention

See `references/capability-boundaries.md` for current operational boundaries.

## Examples

Minimal sample inputs are included in:

- `examples/intake.json`
- `examples/draft.md`
- `examples/reference-pack.json`

For a lightweight end-to-end validation, see:

- `scripts/smoke_test_pipeline.py`

## License

MIT
