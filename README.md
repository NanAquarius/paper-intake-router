[English](./README.md) | [简体中文](./README.zh-CN.md)

# paper-intake-router

[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![OpenClaw-first](https://img.shields.io/badge/OpenClaw-first-4f46e5)](#-start-here-by-environment)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](#-installation)
[![Smoke-tested](https://img.shields.io/badge/validated-smoke%20test-0f766e)](#-examples-and-validation)
[![CLI](https://img.shields.io/badge/CLI-paper__router.py-111827)](#-unified-cli)
[![Citations](https://img.shields.io/badge/citations-GB%2FT%207714%20%7C%20APA-7c3aed)](#-what-the-core-covers)
[![Task workspace](https://img.shields.io/badge/artifacts-task%20workspace-9a3412)](#-workflow-artifact-map)

> 🧭 *A paper workflow core for turning vague paper requests into structured, evidence-aware, figure-aware, citation-consistent deliverables.*

## 📚 Contents

- [✨ What it is for](#-what-it-is-for)
- [🚫 What it is not for](#-what-it-is-not-for)
- [⚡ 60-second path](#-60-second-path)
- [🧩 Start here by environment](#-start-here-by-environment)
- [🗺 Workflow artifact map](#-workflow-artifact-map)
- [🔧 What the core covers](#-what-the-core-covers)
- [🚀 Installation](#-installation)
- [🛠 Unified CLI](#-unified-cli)
- [🧰 More detailed usage](#-more-detailed-usage)
- [🔑 External services](#-external-services)
- [🧪 Examples and validation](#-examples-and-validation)
- [🗂 Repository layout](#-repository-layout)
- [License](#license)

`paper-intake-router` is a **paper workflow core**, not a generic AI paper writer.

It is built for academic work where the hard part is not only drafting paragraphs, but also turning a vague request into a stable workflow with task normalization, figure/table planning, citation discipline, and deliverable-aware rendering.

## ✨ What it is for

Use it when you need an agent or local workflow to do things like:

- normalize a paper request into a structured task sheet
- decide what the next stage should be before drafting starts
- plan figures and tables before the draft drifts
- keep figure references and numbering consistent
- render citations in a predictable final style
- keep intermediate artifacts organized in a task workspace

## 🚫 What it is not for

It is **not** a promise of:

- school-specific compliance without the real official template
- real experimental validity
- trustworthy references invented from nowhere
- submission readiness without human review
- one-shot “write my whole thesis perfectly” behavior

If that boundary matters for your use case, read [`references/capability-boundaries.md`](./references/capability-boundaries.md) early.

## ⚡ 60-second path

**Input:** [`examples/intake.json`](./examples/intake.json)

**Run:**

```bash
python3 scripts/paper_router.py build-task -- \
  --input examples/intake.json \
  --out-json /tmp/task.json

python3 scripts/paper_router.py init-workspace -- \
  --base-dir /tmp/paper-runs \
  --task /tmp/task.json \
  --out-json /tmp/workspace.json

python3 scripts/paper_router.py build-figure-plan -- \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json

python3 scripts/paper_router.py smoke-test
```

**Output:**

- `/tmp/task.json`
- `/tmp/workspace.json`
- `/tmp/figure-plan.json`
- a smoke-tested local chain ending in a rendered draft with citations

If you prefer raw scripts, the same workflow is available under `scripts/`.

## 🧩 Start here by environment

### For OpenClaw

This repository is designed first for the OpenClaw ecosystem.

Use it when you want a paper-oriented workflow core behind an OpenClaw Skill, especially when the agent needs more than “generate text”: intake routing, artifact planning, and stable citation handling.

### For local CLI use

You can run the core workflow locally with Python only.

The local chain covers task normalization, task workspace initialization, figure/table planning, validation, autofix, and citation rendering.

### For other agent runtimes

It can be adapted to Claude Code, OpenCode, or similar runtimes, but it is **not guaranteed to work out of the box**.

Expect to adapt:

- runtime assumptions
- workspace and path conventions
- upstream search and evidence backends
- tool wiring and invocation glue

## 🗺 Workflow artifact map

The core artifact flow looks like this:

```text
intake.json
  → task.json
  → workspace.json
  → figure-plan.json
  → fixed.md / validation.json
  → final.md
```

What each artifact means:

- `task.json`: normalized paper request, defaults, and routing metadata
- `workspace.json`: task-scoped directory manifest for drafts, figures, tables, references, and outputs
- `figure-plan.json`: planned figures/tables, numbering rules, and codegen targets
- `validation.json`: consistency check between draft references and the figure plan
- `final.md`: citation-rendered draft after internal markers are resolved

## 🔧 What the core covers

### Intake and task routing

- normalize requests into structured task sheets
- infer defaults for paper type, language, style, and delivery mode
- resolve default layout templates when no official template is provided

### Evidence and citation workflow

- reference shortlist
- screening and retry search flow
- reference pack
- writing evidence pack
- citation plan by chapter and claim type

### Figure / table workflow

- figure/table planning before drafting
- numbering rules derived from template logic
- code / CSV / artifact scaffolding
- validation of figure references against the plan
- autofix for figure explanation prose and citation modes

### Unified citation layer

- supports both normal prose and figure explanation sentences
- supports `support-note`, `inline-marker`, and `internal-anchor`
- renders final citations into GB/T 7714 or APA-style output
- supports template-aware citation rendering profiles

## 🚀 Installation

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

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-minimal.txt
```

## 🛠 Unified CLI

The repository includes a thin CLI wrapper for the main workflow scripts:

```bash
python3 scripts/paper_router.py smoke-test
python3 scripts/paper_router.py build-task -- --input examples/intake.json --out-json /tmp/task.json
python3 scripts/paper_router.py init-workspace -- --base-dir /tmp/paper-runs --task /tmp/task.json --out-json /tmp/workspace.json
python3 scripts/paper_router.py build-figure-plan -- --task /tmp/task.json --out-json /tmp/figure-plan.json
```

This wrapper does not replace the underlying scripts. It makes the common path easier to discover and easier to document.

## 🧰 More detailed usage

### Build a normalized task sheet

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json \
  --out-md /tmp/task.md
```

### Initialize a task workspace

```bash
python3 scripts/init_task_workspace.py \
  --base-dir /tmp/paper-runs \
  --task /tmp/task.json \
  --out-json /tmp/workspace.json
```

### Build a figure/table plan

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json \
  --out-md /tmp/figure-plan.md
```

Optional inputs:

- `--evidence-pack`
- `--citation-plan`

### Generate figure/table code scaffolding

```bash
python3 scripts/generate_figure_table_codegen.py \
  --plan /tmp/figure-plan.json \
  --base-dir /tmp/paper-artifacts
```

### Validate figure/table references

```bash
python3 scripts/validate_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft /tmp/draft.md \
  --out-json /tmp/figure-validation.json \
  --out-md /tmp/figure-validation.md
```

### Render final citations with a profile

```bash
python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --citation-profile-json /tmp/profile.json \
  --style 'APA' \
  --out /tmp/final.md
```

## 🔑 External services

The local core workflow does **not** require API keys for:

- task sheet generation
- figure/table planning
- local validation and autofix
- citation rendering
- smoke tests

Full literature-search and evidence-building flows often benefit from or depend on external providers such as:

- Semantic Scholar API
- OpenAlex
- Tavily / Exa / other search providers

Document clearly in your own deployment which upstream providers are required and which steps depend on them.

## 🧪 Examples and validation

Included examples:

- [`examples/intake.json`](./examples/intake.json)
- [`examples/draft.md`](./examples/draft.md)
- [`examples/reference-pack.json`](./examples/reference-pack.json)
- [`examples/layout-samples/README.md`](./examples/layout-samples/README.md)

Minimal validation entrypoints:

```bash
python3 scripts/smoke_test_pipeline.py
python3 scripts/paper_router.py smoke-test
```

The current smoke test covers:

- task normalization
- task workspace initialization
- figure/table plan generation
- figure reference autofix
- figure reference validation
- final citation rendering

## 🗂 Repository layout

```text
paper-intake-router/
├── SKILL.md
├── scripts/
├── references/
├── paper-template-library/
├── examples/
├── paper_intake_router/
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## License

MIT
