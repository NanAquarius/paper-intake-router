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
- **Template-aware final citation rendering**

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

## Requirements

### Runtime

- Python 3.10+
- A Unix-like shell environment (Linux / macOS / WSL recommended)

### Optional dependencies

Depending on which parts of the workflow you use, you may also want:

- `quarto`
- `pandoc`
- `xelatex` or an equivalent LaTeX toolchain
- `matplotlib` for figure code scaffolding that renders local charts

## API keys and external services

The **core local workflow** in this repository does **not** require an API key.

You can run the local pipeline pieces such as:

- task sheet generation
- figure/table planning
- figure/table autofix
- citation rendering
- smoke tests

without configuring external services.

However, **literature-search and evidence-building stages may require upstream tools or API keys**, depending on how you wire the project into your own agent stack.

Typical examples:

- OpenAlex / Semantic Scholar / Research-paper MCPs
- Tavily / Exa / other search providers
- Any external academic search or document parsing service

**Recommendation:** document clearly for your own deployment which search backend you use, and remind end users when a workflow step depends on external credentials rather than local scripts.

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

## More detailed usage

### A. Intake normalization

Use `build_task_sheet.py` when you already have a normalized or semi-normalized intake JSON.

Example:

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json \
  --out-md /tmp/task.md
```

This stage decides:

- paper type
- degree level
- topic
- style
- target length
- selected layout template

### B. Figure / table planning

Use `build_figure_table_plan.py` to create a structured plan before drafting.

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json \
  --out-md /tmp/figure-plan.md
```

Optional inputs:

- `--evidence-pack`
- `--citation-plan`

When provided, the plan becomes evidence-aware and citation-aware.

### C. Figure/table code scaffolding

```bash
python3 scripts/generate_figure_table_codegen.py \
  --plan /tmp/figure-plan.json \
  --base-dir /tmp/paper-artifacts
```

This can create:

- code stubs
- placeholder CSV data
- figure/table output paths

### D. Figure/table validation

```bash
python3 scripts/validate_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft /tmp/draft.md \
  --out-json /tmp/figure-validation.json \
  --out-md /tmp/figure-validation.md
```

This checks:

- missing required figure/table references
- unexpected figure/table references in prose
- numbering issues
- duplicate labels in the plan

### E. Autofix modes

`autofix_figure_table_refs.py` supports three citation modes:

- `support-note`
  - draft-oriented
  - adds prose like “can be further supported by …”

- `inline-marker`
  - transitional mode
  - writes visible inline markers such as `[2]`

- `internal-anchor`
  - best mode for full automation
  - writes internal anchors such as `[CITE:baseline comparison|lee2024benchmark]`
  - lets figure explanation text and normal prose share the same final citation rendering pipeline

Example:

```bash
python3 scripts/autofix_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft /tmp/draft.md \
  --citation-mode internal-anchor \
  --out /tmp/fixed.md \
  --report /tmp/autofix-report.json
```

### F. Final citation rendering

```bash
python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --style 'APA' \
  --out /tmp/final.md
```

Optional inputs:

- `--citation-plan`
- `--citation-profile-json`

Use `citation-profile-json` when your layout template has a rendering profile (for example, Chinese thesis bracket conventions vs APA-style inline author-year formatting).

## Typical artifacts produced by the workflow

Depending on which path you run, the workflow may produce:

- `task.json` / `task.md`
- `references-shortlist.json` / `.md`
- `reference-screening.json` / `.md`
- `reference-pack.json` / `.md`
- `writing-evidence-pack.json` / `.md`
- `citation-plan.json` / `.md`
- `figure-table-plan.json` / `.md`
- generated code / CSV / figures / tables
- fixed draft files
- final rendered draft files

## Examples

Minimal sample inputs are included in:

- `examples/intake.json`
- `examples/draft.md`
- `examples/reference-pack.json`

For a lightweight end-to-end validation, see:

- `scripts/smoke_test_pipeline.py`

## What this project is

Think of it as a:

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

## License

MIT
