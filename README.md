[English](./README.md) | [简体中文](./README.zh-CN.md)

# paper-intake-router

> An OpenClaw-oriented paper workflow Skill / engine for intake, evidence organization, figure/table planning, citation alignment, and template-aware final rendering.

`paper-intake-router` is primarily designed as an **OpenClaw Skill** and workflow core for academic writing agents.
It is optimized for paper-production workflows where text generation alone is not enough.

It helps agents manage the operational layer around papers:

**Compatibility note**

This repository is built first for the **OpenClaw** ecosystem.

It may still be reusable in other agent / CLI environments such as **Claude Code**, **OpenCode**, or similar coding-agent runtimes, but it is **not guaranteed to work out of the box** there. In those environments, you should expect to adjust:

- runtime assumptions
- file paths and workspace conventions
- upstream search / evidence backends
- tool wiring and invocation glue

If you are not using OpenClaw, treat this repository as a portable workflow core that may require adaptation rather than a plug-and-play package.

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
- A Unix-like shell environment (Linux / macOS / WSL recommended) or Windows PowerShell

### Optional dependencies

Depending on which parts of the workflow you use, you may also want:

- `quarto`
- `pandoc`
- `xelatex` or an equivalent LaTeX toolchain
- `matplotlib` for figure code scaffolding that renders local charts

## Environment setup

### Linux / macOS / WSL

```bash
git clone https://github.com/NanAquarius/paper-intake-router.git
cd paper-intake-router
chmod +x scripts/install.sh
./scripts/install.sh
source .venv/bin/activate
```

### Windows PowerShell

```powershell
git clone https://github.com/NanAquarius/paper-intake-router.git
cd paper-intake-router
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
.\.venv\Scripts\Activate.ps1
```

### Manual setup (cross-platform)

If you prefer manual setup instead of the helper scripts:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-minimal.txt
```

On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-minimal.txt
```

### What the install scripts do

The install helpers:

- create a local virtual environment
- upgrade `pip`
- install `requirements-minimal.txt`

They intentionally keep installation minimal so the local planning / validation / citation workflow works out of the box.

If you want richer rendering or broader document workflows, install optional tools such as `quarto`, `pandoc`, or a LaTeX engine separately.

## API keys and external services

The **core local workflow** in this repository does **not** require an API key.

You can run the local pipeline pieces such as:

- task sheet generation
- figure/table planning
- figure/table autofix
- citation rendering
- smoke tests

without configuring external services.

However, the following parts of a full paper workflow are **recommended to be backed by external APIs or upstream services**:

- literature search
- reference shortlist generation
- evidence-pack construction
- external academic metadata retrieval
- large-scale document parsing / search augmentation

### Suggested external providers

Examples of upstream services you may want to configure in your own deployment:

- **Semantic Scholar API**
  - official overview: <https://www.semanticscholar.org/product/api>
  - tutorial / authentication notes: <https://www.semanticscholar.org/product/api/tutorial>
  - API docs: <https://api.semanticscholar.org/api-docs/>
  - if your workflow depends on Semantic Scholar-backed retrieval, users should obtain and configure their own API-enabled access according to the official docs

- **OpenAlex**
  - useful for paper metadata and academic graph lookups
  - depending on your usage pattern, you may not need a private key, but you should still document the backend you rely on

- **Tavily / Exa / other search providers**
  - recommended when your workflow depends on external web search, retrieval augmentation, or evidence enrichment

### Recommendation for users and maintainers

If a deployment enables literature-search or evidence-building stages through external providers, the README or deployment guide should explicitly state:

- which provider is used
- whether an API key is required
- where the user should obtain that key
- which workflow steps depend on that external credential

In other words: **the local core does not require an API key, but production-style retrieval workflows often do.**

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
- `examples/layout-samples/README.md` (guidance for building your own local layout sample library)

For a lightweight end-to-end validation, see:

- `scripts/smoke_test_pipeline.py`

## What this project is

Think of it as a:

- **paper workflow engine**
- **formatting and citation stabilizer**
- **draft-to-deliverable orchestration layer for agents**

## What this project is not

This project does **not** guarantee:

- bundled redistributable thesis / journal / conference PDF layout samples by default

- school-specific compliance without the real template or official guideline
- real experimental validity
- final submission readiness without human review
- automatic invention of trustworthy data, results, or references

See `references/capability-boundaries.md` for the current operational boundary set.

## License

MIT
