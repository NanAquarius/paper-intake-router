[English](./README.md) | [简体中文](./README.zh-CN.md) | [繁體中文](./README.zh-TW.md)

# paper-intake-router

[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![OpenClaw-first](https://img.shields.io/badge/OpenClaw-first-4f46e5)](#-依使用環境進入)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](#-安裝)
[![Smoke-tested](https://img.shields.io/badge/validated-smoke%20test-0f766e)](#-範例與驗活)
[![CLI](https://img.shields.io/badge/CLI-paper__router.py-111827)](#-統一-cli)
[![Citations](https://img.shields.io/badge/citations-GB%2FT%207714%20%7C%20APA-7c3aed)](#-核心能力)
[![Task workspace](https://img.shields.io/badge/artifacts-task%20workspace-9a3412)](#-workflow-artifact-map)

> 🧭 *把模糊的論文需求整理成結構化、具證據脈絡、圖表感知與引用一致性的可交付成果。*

## 📚 目錄

- [✨ 它適合做什麼](#-它適合做什麼)
- [🚫 它不適合承諾什麼](#-它不適合承諾什麼)
- [⚡ 60 秒上手](#-60-秒上手)
- [🧩 依使用環境進入](#-依使用環境進入)
- [🗺 Workflow artifact map](#-workflow-artifact-map)
- [🔧 核心能力](#-核心能力)
- [🚀 安裝](#-安裝)
- [🛠 統一 CLI](#-統一-cli)
- [🧰 更詳細的使用方式](#-更詳細的使用方式)
- [🔑 外部服務](#-外部服務)
- [🧪 範例與驗活](#-範例與驗活)
- [🗂 倉庫結構](#-倉庫結構)
- [License](#license)

`paper-intake-router` 是一個 **論文 workflow core**，不是一般意義上的 AI 論文寫作器。

它處理的重點，不是替你多寫幾段文字，而是把論文工作裡最容易失控的那一層流程先收斂好：需求歸一化、任務單生成、圖表規劃、引用約束、產物管理，以及面向最終交付的渲染鏈路。

## ✨ 它適合做什麼

當你需要 agent 或本地工作流程去處理以下事情時，它就很合適：

- 把模糊的論文需求整理成結構化 task sheet
- 在開始寫正文前，先判斷下一步應該做什麼
- 在草稿逐漸發散之前，先把 figure/table 規劃好
- 維持圖表編號與正文引用的一致性
- 用穩定規則渲染最終引用格式
- 把中間產物收進同一個任務工作區裡

## 🚫 它不適合承諾什麼

它 **不代表**：

- 沒有官方模板原檔也能百分之百符合學校規範
- 自動保證實驗結果真實有效
- 不經人工複核就能直接投稿或送審
- 憑空產生可信的文獻、數據或結論
- 一次性把整篇論文「完美寫完」

如果這些邊界對你很重要，建議一開始就先看 [`references/capability-boundaries.md`](./references/capability-boundaries.md)。

## ⚡ 60 秒上手

**輸入：** [`examples/intake.json`](./examples/intake.json)

**執行：**

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

**輸出：**

- `/tmp/task.json`
- `/tmp/workspace.json`
- `/tmp/figure-plan.json`
- 一條可以在本地驗活、最後能產出帶引用草稿的 smoke test 鏈路

如果你偏好直接調用底層腳本，也可以照樣使用 `scripts/` 目錄下的原始命令。

## 🧩 依使用環境進入

### For OpenClaw

這個倉庫首先是為 OpenClaw 生態設計的。

如果你需要的是一個放在 OpenClaw Skill 背後、真正面向論文流程的內核，而不是單純的文字生成器，它的定位就是為此而來。

### For local CLI

這套核心鏈路可以純本地執行，依賴基本上就是 Python。

本地鏈路涵蓋 task normalize、task workspace init、figure/table planning、validation、autofix 與 citation rendering。

### For other agent runtimes

它也能遷移到 Claude Code、OpenCode 或其他類似的 agent runtime，但 **不保證開箱即用**。

通常你仍需要自己調整：

- runtime 假設
- workspace / 路徑慣例
- 上游檢索與證據後端
- 工具調用與命令編排方式

## 🗺 Workflow artifact map

核心產物流大致如下：

```text
intake.json
  → task.json
  → workspace.json
  → figure-plan.json
  → fixed.md / validation.json
  → final.md
```

各個產物大致代表：

- `task.json`：歸一化後的論文任務單、預設值與路由資訊
- `workspace.json`：該任務的目錄清單，集中管理 drafts、figures、tables、references 與 outputs
- `figure-plan.json`：圖表規劃、編號規則與 codegen 目標
- `validation.json`：草稿中的圖表引用是否與 figure plan 一致
- `final.md`：內部引用標記被解析後的終稿草稿

## 🔧 核心能力

### Intake 與任務路由

- 把需求歸一化成結構化 task sheet
- 推斷論文類型、語言、風格與交付模式等預設值
- 在缺少官方模板時選擇預設版式模板

### 文獻與引用工作流程

- reference shortlist
- screening 與 retry 檢索鏈
- reference pack
- writing evidence pack
- 依章節 / claim type 組織 citation plan

### 圖表工作流程

- 在寫作前先產出 figure/table plan
- 從模板邏輯推導編號規則
- 生成程式碼 / CSV / 產物腳手架
- 檢查圖表引用與編號一致性
- 自動修正圖表說明句與引用模式

### 統一引用層

- 正文段落與圖表說明句共用同一套 citation layer
- 支援 `support-note`、`inline-marker`、`internal-anchor`
- 支援 GB/T 7714 與 APA 風格渲染
- 支援模板感知的 citation rendering profile

## 🚀 安裝

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

### 手動安裝

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-minimal.txt
```

## 🛠 統一 CLI

倉庫內現在提供一層薄封裝 CLI，用來承接最常見的 workflow 命令：

```bash
python3 scripts/paper_router.py smoke-test
python3 scripts/paper_router.py build-task -- --input examples/intake.json --out-json /tmp/task.json
python3 scripts/paper_router.py init-workspace -- --base-dir /tmp/paper-runs --task /tmp/task.json --out-json /tmp/workspace.json
python3 scripts/paper_router.py build-figure-plan -- --task /tmp/task.json --out-json /tmp/figure-plan.json
```

它不會取代底層腳本，只是讓常見路徑更容易被發現，也更方便寫進 README。

## 🧰 更詳細的使用方式

### 生成標準 task sheet

```bash
python3 scripts/build_task_sheet.py \
  --input examples/intake.json \
  --out-json /tmp/task.json \
  --out-md /tmp/task.md
```

### 初始化任務工作區

```bash
python3 scripts/init_task_workspace.py \
  --base-dir /tmp/paper-runs \
  --task /tmp/task.json \
  --out-json /tmp/workspace.json
```

### 生成圖表規劃

```bash
python3 scripts/build_figure_table_plan.py \
  --task /tmp/task.json \
  --out-json /tmp/figure-plan.json \
  --out-md /tmp/figure-plan.md
```

可選輸入：

- `--evidence-pack`
- `--citation-plan`

### 生成圖表程式碼腳手架

```bash
python3 scripts/generate_figure_table_codegen.py \
  --plan /tmp/figure-plan.json \
  --base-dir /tmp/paper-artifacts
```

### 校驗圖表引用

```bash
python3 scripts/validate_figure_table_refs.py \
  --plan /tmp/figure-plan.json \
  --draft /tmp/draft.md \
  --out-json /tmp/figure-validation.json \
  --out-md /tmp/figure-validation.md
```

### 依 profile 渲染最終引用

```bash
python3 scripts/render_final_citations.py \
  --draft /tmp/fixed.md \
  --reference-pack examples/reference-pack.json \
  --citation-profile-json /tmp/profile.json \
  --style 'APA' \
  --out /tmp/final.md
```

## 🔑 外部服務

本地核心鏈本身 **不強制要求 API Key**，以下步驟可以純本地執行：

- task sheet 生成
- 圖表規劃
- 本地圖表校驗與自動修正
- 引用渲染
- smoke test

但完整的文獻檢索 / evidence-building 鏈通常會受益於或依賴外部服務，例如：

- Semantic Scholar API
- OpenAlex
- Tavily / Exa / 其他檢索服務

建議你在自己的部署文件中寫清楚：用了哪些上游、哪些步驟依賴它們、是否需要 API Key。

## 🧪 範例與驗活

倉庫附帶的最小範例：

- [`examples/intake.json`](./examples/intake.json)
- [`examples/draft.md`](./examples/draft.md)
- [`examples/reference-pack.json`](./examples/reference-pack.json)
- [`examples/layout-samples/README.md`](./examples/layout-samples/README.md)

最小驗活入口：

```bash
python3 scripts/smoke_test_pipeline.py
python3 scripts/paper_router.py smoke-test
```

目前 smoke test 覆蓋：

- task 歸一化
- 任務工作區初始化
- 圖表規劃生成
- 圖表引用自動修正
- 圖表引用校驗
- 終稿引用渲染

## 🗂 倉庫結構

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
├── README.zh-TW.md
└── LICENSE
```

## License

MIT

---

<div align="center">

*如果這套 workflow core 對你的論文流程有幫助，歡迎點個 Star、提個 issue，或分享你的實際使用場景。*

<sub>⭐ <a href="https://github.com/NanAquarius/paper-intake-router">Star</a> &nbsp;·&nbsp; 🐛 <a href="https://github.com/NanAquarius/paper-intake-router/issues">Issue</a> &nbsp;·&nbsp; 🤝 <a href="https://github.com/NanAquarius/paper-intake-router/pulls">PR</a></sub>

</div>
